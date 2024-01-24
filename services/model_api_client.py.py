from gradio_client import Client
from bs4 import BeautifulSoup
import pandas as pd


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
        sender = '0' if row['发送方'] == 0 else '1'
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


def analyze_customer_service_interaction(df):
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
