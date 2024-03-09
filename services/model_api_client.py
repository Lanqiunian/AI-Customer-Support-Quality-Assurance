import openai
from PyQt6.QtCore import pyqtSignal, QObject, QThread
from bs4 import BeautifulSoup
from gradio_client import Client
from dotenv import load_dotenv
import os
from services.global_setting import AI_PROMPT_RULES, AI_PROMPT_RULES_JSON_EXAMPLE


def convert_dataframe_to_single_string_dialog(df):
    """
    将 DataFrame 转换为单一字符串形式的对话。

    参数:
    df (pd.DataFrame): 包含对话信息的 DataFrame

    返回:
    str: 转换后的对话字符串
    """
    dialog = ''
    for index, row in df.iterrows():
        sender = '客服：' if row['发送方'] == 0 else '用户：'
        message = f"{sender}: {row['消息内容']} "
        dialog += message
    return dialog.strip()


def extract_relevant_feedback(html_content):
    """
        提取需要的反馈部分。

        参数:
        html_content (str): HTML格式的内容

        返回:
        str: 需要的反馈部分
        """
    # 使用 BeautifulSoup 解析 HTML 内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有 <ol> 标签，这些标签包含了所需的反馈
    relevant_feedback = soup.find_all('ol')

    # 将找到的反馈转换为纯文本
    feedback_text = ''
    for feedback in relevant_feedback:
        feedback_text += feedback.get_text()

    return feedback_text


def get_ai_analysis_chatglm6b(df):
    """
    分析客服与客户之间的 DataFrame 形式对话并提供反馈。

    参数:
    df (pd.DataFrame): 客服与客户之间的对话 DataFrame

    返回:
    str: 对话分析的反馈
    """
    dialog = convert_dataframe_to_single_string_dialog(df)
    message = "请具体分析以下对话中客服存在的问题并给出改进措施，不存在的问题，请不要无中生有；其中“0”代表客服，“1”代表客户：" + dialog
    client = Client("https://656041d841c1853a09.gradio.live/")
    result = client.predict(
        message,
        4096,  # Maximum length
        0.7,  # Top P
        0.9,  # Temperature
        fn_index=0
    )

    feedback = extract_relevant_feedback(str(result))
    return feedback


def get_ai_analysis_chatgpt(dialogue, AI_prompt=None):
    print(f"AI_prompt为", AI_prompt)
    load_dotenv()  # 加载.env文件中的变量
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if AI_prompt == "":  # 这里用""而不是None
        AI_prompt = "作为一位客服对话分析专家，你的任务是:1.识别客服在对话中的表现问题，2.给出改善建议。"
    else:
        AI_prompt = "作为一位客服对话分析专家，你的任务是:" + AI_prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": AI_prompt},
            {"role": "user", "content": dialogue}
        ]
    )

    analysis = response.choices[0].message['content'].strip()
    return analysis


def get_ai_rule_json_chatgpt(direction=None):
    load_dotenv()  # 加载.env文件中的变量
    openai.api_key = os.getenv('OPENAI_API_KEY')

    AI_prompt = AI_PROMPT_RULES + direction + AI_PROMPT_RULES_JSON_EXAMPLE

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": AI_prompt},

        ]
    )

    rule_json = response.choices[0].message['content'].strip()
    return rule_json


# AIAnalysisWorker类中添加finished信号
class AIAnalysisWorker(QObject):
    analysisCompleted = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, dialogue_data, AI_prompt=None):
        super().__init__()
        self.dialogue_data = dialogue_data
        self.AI_prompt = AI_prompt

    def process(self):
        dialogue_str = convert_dataframe_to_single_string_dialog(self.dialogue_data)
        ai_response = get_ai_analysis_chatgpt(dialogue_str, self.AI_prompt)
        print(ai_response)
        self.analysisCompleted.emit(ai_response)
        self.finished.emit()


class AISuggestionThread(QThread):
    finished = pyqtSignal(str, object)  # object 可以接受任何类型，包括 NoneType 和 Exception

    def __init__(self, direction, parent=None):
        super().__init__(parent)
        self.direction = direction

    def run(self):
        try:
            rule_json = get_ai_rule_json_chatgpt(self.direction)  # 假设这是获取 AI 建议的函数
            self.finished.emit(rule_json, None)  # 没有异常时，第二个参数为 None
        except Exception as e:
            self.finished.emit("", e)  # 捕获到异常时，发送异常对象


if __name__ == "__main__":
    print(get_ai_rule_json_chatgpt("分析客服的营销意识"))
