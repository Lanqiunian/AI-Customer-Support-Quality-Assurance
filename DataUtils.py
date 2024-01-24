from datetime import datetime

import pandas as pd

import jieba
import re


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
