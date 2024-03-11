import json
import re
import sqlite3
from datetime import datetime

import jieba
import pandas as pd

from services.db.db_dialogue_data import get_service_id_by_dialogue_id_and_task_id
from utils.global_utils import RULE_DB_PATH, TASK_DB_PATH, DIALOGUE_DB_PATH


def load_stopwords(file_path):
    """加载停用词表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set([line.strip() for line in file])
    return stopwords


def chinese_tokenization(dataframe, column_name='消息内容', stopwords_path='stopwords.txt'):
    """
    对指定Df中的消息内容，进行分词以及滤除停用词

    后期可能得改一下，直接传消息内容
    :param dataframe: 指定df
    :param column_name: 选取消息内容这一列
    :param stopwords_path: 停用词列表
    :return:
    """
    # 加载停用词表
    stopwords = load_stopwords(stopwords_path)

    # 定义一个用于匹配非中文字符的正则表达式
    pattern = re.compile(r'[^\u4e00-\u9fff]')

    # 筛选出发送方为0（客服）的行
    service_messages = dataframe[dataframe['发送方'] == 0]

    # 对每条消息进行中文分词、滤除停用词和非中文字符
    tokenized_messages = service_messages[column_name].apply(
        lambda x: ' '.join([word for word in jieba.cut(x) if word not in stopwords and not pattern.search(word)])
    )

    return tokenized_messages


def generate_html(dialogue_df):
    dialogue_html = []
    for index, row in dialogue_df.iterrows():
        sender = "客服" if row['发送方'] == 0 else "客户"
        background_color = "#e7f3fe" if sender == "客服" else "#f0f0f0"
        message_html = f"""
        <div style='margin: 10px; padding: 10px; background-color: {background_color}; border-radius: 10px; box-shadow: 2px 2px 2px #b0b0b0;'>
            <p><b>{sender}:</b> {row['消息内容']}</p>
        </div>
        """
        dialogue_html.append(message_html)
    return "".join(dialogue_html)


def calculate_time_difference(time1, time2):
    """
    计算两个日期之间的时间差

    :param time1: 靠后的时间
    :param time2: 基准时间
    :return: 分钟差
    """
    # 定义时间的格式
    time_format = '%Y/%m/%d %H:%M'

    # 将字符串时间转换为datetime对象
    datetime1 = datetime.strptime(time1, time_format)
    datetime2 = datetime.strptime(time2, time_format)

    # 计算时间差异并转换为分钟
    time_difference = abs(datetime1 - datetime2)
    minutes_difference = time_difference.total_seconds() / 60

    return minutes_difference


def extract_service_messages(df):
    """
    提取DataFrame中发送方为0（即客服）的行的消息内容。

    :param df: Pandas DataFrame，包含对话数据
    :return: 包含客服消息的Pandas Series
    """
    # 筛选发送方为0的行，并提取消息内容列
    service_messages = df[df['发送方'] == 0]['消息内容']
    return service_messages


def extract_customer_messages(df):
    """
    提取DataFrame中发送方为1（即顾客）的行的消息内容。

    :param df: Pandas DataFrame，包含对话数据
    :return: 包含顾客消息的Pandas Series
    """
    # 筛选发送方为0的行，并提取消息内容列
    customer_messages = df[df['发送方'] == 1]['消息内容']
    return customer_messages


def is_valid_logic_expression(expression, conditionsCounter):
    # 移除表达式前后的空格
    expression = expression.strip()

    # 1. 检查是否有非法符号，正确排除括号
    if re.search(r"[^0-9()\sandrotn]", expression):
        print("Contains invalid characters.")
        return False

    # 2. 检查是否包含除了 1 到 conditionsCounter 之外的数字
    invalid_numbers = [num for num in re.findall(r'\d+', expression) if not 1 <= int(num) <= conditionsCounter]
    if invalid_numbers:
        print(f"Contains numbers out of allowed range: {invalid_numbers}")
        return False

    # 3. 检查括号是否闭合
    if not brackets_match(expression):
        print("Unmatched parentheses.")
        return False

    # 4. 分词并检查每个元素是否合法
    tokens = re.split(r'(\s+|\band\b|\bor\b|\bnot\b|\(|\))', expression)
    tokens = [token.strip() for token in tokens if token.strip()]  # 移除空字符串和首尾空格

    valid_tokens = set(["and", "or", "not"] + [str(i) for i in range(1, conditionsCounter + 1)] + ['(', ')'])
    if not all(token in valid_tokens or token.isdigit() for token in tokens):
        print("Contains invalid words or numbers.")
        return False
    # 5. 确保表达式不以逻辑运算符开头或结尾
    if tokens[0] in ["and", "or"] or tokens[-1] in ["and", "or", "not"]:
        print("Expression starts or ends with a logical operator.")
        return False

    # 5. 检查操作符前后是否正确放置
    for i, token in enumerate(tokens[:-1]):  # 不检查最后一个元素，防止索引越界
        next_token = tokens[i + 1]

        # 允许 "and not" 和 "or not"
        if token in ["and", "or"] and next_token == "not":
            continue

        # 检查逻辑运算符后是否紧跟另一个逻辑运算符（除了 "not"）
        if token in ["and", "or", "not"] and next_token in ["and", "or"]:
            print("Consecutive logical operators.")
            return False

        # 检查 "not" 后是否直接跟随数字或括号
        if token == "not" and not (next_token.isdigit() or next_token == "("):
            print("Invalid 'not' usage.")
            return False

    # 通过所有检查
    return True


def brackets_match(expression):
    stack = []
    for char in expression:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack[-1] != '(':
                return False
            stack.pop()
    return not stack


class Dialogue:

    def __init__(self, dataPath):  # 直接读取对话集，来进行构造
        # 加载数据
        try:
            # 使用'gb18030'编码加载数据，适用于包含中文的CSV文件
            self.dialogue_data = pd.read_csv(dataPath, encoding='gb18030')
            print("数据加载成功。")
        except Exception as e:
            print(f"数据加载失败：{e}")

        # 显示数据的前几行以进行检查
        # print("\n数据前几行取样为：")
        # print(self.dialogue_data.head())

    def DialogueInfo(self):
        # 基本的数据操作示例
        # 1. 查看数据的基本信息
        print("\n数据基本信息：")
        print(self.dialogue_data.info())

    def customerMessageCount(self):
        print("\n每个客户的消息数量：")
        print(self.dialogue_data['客户ID'].value_counts())
        return self.dialogue_data['客户ID'].value_counts()

    def getDialogueBySession(self, specific_dialogue_id):
        # 使用条件过滤来选择对应对话ID的行
        specific_dialogue = self.dialogue_data[self.dialogue_data['对话ID'] == specific_dialogue_id]
        # 打印结果
        # print(f"对话ID为 {specific_dialogue_id} 的对话内容：")
        # print(specific_dialogue[['客户ID', '客服ID', '消息内容', '发送方', '发送时间']])

        return specific_dialogue[['客户ID', '客服ID', '消息内容', '发送方', '发送时间']]

    def getDialogueByCustomer(self, specific_customer_id):
        print(f"\n客户 {specific_customer_id} 的对话：")
        print(self.dialogue_data[self.dialogue_data['客户ID'] == specific_customer_id])
        return self.dialogue_data[self.dialogue_data['客户ID'] == specific_customer_id]

    def analyzeResponseTime(self, service_id=None):
        """
        计算相应速度

        Parameters:
            param1 - 给到客服ID时，计算此客服的平均回复时间；如果为空，则计算全部记录的客服平均回复时间

        Raises:
            KeyError - 数据不够用，就报错
        """
        response_times = []
        for _, group in self.dialogue_data.groupby('对话ID'):
            # 仅考虑包含客户和客服对话的情况
            if group['发送方'].nunique() == 2:
                last_sender = None
                last_time = None
                for _, row in group.iterrows():
                    current_sender = row['发送方']
                    current_time = row['发送时间']
                    # 如果指定了特定的客服ID，且当前行不是该客服的，则跳过
                    if service_id is not None and current_sender == 0 and row['客服ID'] != service_id:
                        continue
                    # 检查是否交替出现客户和客服
                    if last_sender is not None and current_sender != last_sender:
                        # 如果当前消息是客服的回复，计算时间差
                        if current_sender == 0:
                            response_time = calculate_time_difference(last_time, current_time)
                            response_times.append(response_time)
                    last_sender = current_sender
                    last_time = current_time

        # 计算平均回复时间
        if response_times:
            average_response_time = sum(response_times) / len(response_times)

            if service_id is not None:
                print(f"客服{service_id}的平均回复时间（分钟）: {average_response_time}")
            else:
                print(f"全体平均回复时间（分钟）: {average_response_time}")
        else:
            print("没有足够的数据来计算平均回复时间。")


def text_to_list(text):
    # 分割文本成列表，这里假设每句话直接有一个空格分隔
    scripts = text.split(" ")
    return scripts


def list_to_text(scripts):
    # 将列表合并成文本，每句话之间用空格分隔
    text = " ".join(scripts)
    return text


def get_score_info_by_name(rule_name):
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT score_type, score_value FROM score_rules WHERE rule_name=?', (rule_name,))
    scores_info = cursor.fetchall()
    return format_score(scores_info[0])


def format_score(score_tuple):
    """
    根据评分类型和评分值返回格式化的字符串。

    :param score_tuple: 一个包含评分类型和评分值的元组
    :return: 根据评分类型和评分值格式化的字符串
    """
    score_type, score_value = score_tuple

    if score_type == '0':  # 一次性评分
        return f"一次性评为{score_value}"
    elif score_type == '1':
        if score_value < 0:  # 减分
            return f"{score_value}分"  # Python在字符串格式化时会保留负号
        else:  # 加分
            return f"+{score_value}分"
    else:
        return "未知评分类型"


def create_service_id_avg_score_table():
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()

    # 查询所有对话的客服ID、对话ID、任务ID和相应得分
    cursor.execute('''
        SELECT e.dialogue_id, e.task_id, e.score
        FROM evaluation_results AS e
    ''')

    # 用于存储客服ID和其对应的得分列表
    service_scores = {}

    for dialogue_id, task_id, score in cursor.fetchall():
        # 使用 get_service_id_by_dialogue_id_and_task_id 方法获取客服ID
        task_id = int(task_id)
        dialogue_id = int(dialogue_id)
        service_id = get_service_id_by_dialogue_id_and_task_id(task_id, dialogue_id)

        if service_id not in service_scores:
            service_scores[service_id] = []

        service_scores[service_id].append(score)

    # 用于存储客服ID和其对应的平均得分
    service_avg_scores = {}

    for service_id, scores in service_scores.items():
        # 计算每个客服的平均得分
        avg_score = sum(scores) / len(scores) if scores else 0
        service_avg_scores[service_id] = avg_score

    # 假设我们需要输出这个对照表以供后续使用
    # for service_id, avg_score in service_avg_scores.items():
    #     print(f"Service ID: {service_id}, Average Score: {avg_score}")

    conn.close()

    # 返回客服ID和其平均得分的字典
    return service_avg_scores


def analyzeResponseTime(service_id=None):
    conn_dialogue = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor_dialogue = conn_dialogue.cursor()

    # 查询meta_table获取所有对话表名称
    cursor_dialogue.execute("SELECT table_name FROM meta_table")
    tables = cursor_dialogue.fetchall()

    response_times = []

    for table in tables:
        table_name = table[0]

        # 从每个对话表中读取数据
        dialogue_query = f'SELECT * FROM "{table_name}"'
        dialogues = pd.read_sql_query(dialogue_query, conn_dialogue)

        for _, group in dialogues.groupby('对话ID'):
            if group['发送方'].nunique() == 2:
                last_sender = None
                last_time = None
                for _, row in group.iterrows():
                    current_sender = row['发送方']
                    current_time = row['发送时间']
                    if service_id is not None and current_sender == 0 and row['客服ID'] != service_id:
                        continue
                    if last_sender is not None and current_sender != last_sender:
                        if current_sender == 0:
                            response_time = calculate_time_difference(last_time, current_time)
                            response_times.append(response_time)
                    last_sender = current_sender
                    last_time = current_time

    if response_times:
        average_response_time = sum(response_times) / len(response_times)
        # if service_id is not None:
        #     # print(f"客服{service_id}的平均回复时间（分钟）: {average_response_time}")
        # else:
        #     # print(f"全体平均回复时间（分钟）: {average_response_time}")
    else:
        print("没有足够的数据来计算平均回复时间。")
        average_response_time = None

    conn_dialogue.close()

    return average_response_time


if __name__ == "__main__":
    print(create_service_id_avg_score_table())
    analyzeResponseTime("吴玉涵")
