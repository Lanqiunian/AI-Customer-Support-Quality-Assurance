import asyncio

import httpx
import openai
from PyQt6.QtCore import pyqtSignal, QObject, QThread
from bs4 import BeautifulSoup
from gradio_client import Client
from utils.global_utils import AI_PROMPT_RULES, AI_PROMPT_RULES_JSON_EXAMPLE


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


async def call_openai_api_async(dialogue, AI_prompt):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",  # 使用正确的聊天模型名称
                    "messages": [
                        {"role": "system", "content": AI_prompt},
                        {"role": "user", "content": dialogue}
                    ],
                },
                timeout=10.0  # 设置超时时间为20秒
            )
            response.raise_for_status()  # 如果请求失败，则抛出异常
            return response.json()
        except httpx.TimeoutException:
            return "处理超时"
        except httpx.HTTPStatusError as http_err:
            # 这里捕获具体的HTTP状态错误，方便调试
            return f"请求失败: {http_err.response.status_code} {http_err.response.text}"
        except Exception as e:
            return f"请求异常: {str(e)}"


async def get_ai_analysis_chatgpt(dialogue, AI_prompt=None):
    try:
        if not AI_prompt:
            AI_prompt = DEFAULT_AI_PROMPT
        else:
            AI_prompt = "作为一位客服对话分析专家，你的任务是:" + AI_prompt

        result = await call_openai_api_async(dialogue, AI_prompt)
        print(result)
        if result == "处理超时":
            return "处理超时，请网络连接并重试"
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"未知错误: {str(e)}"


async def call_openai_api_async_with_rules(AI_prompt):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": AI_prompt},
                    ],
                },
                timeout=10.0  # 设置超时时间为10秒
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return "处理超时"
        except httpx.HTTPStatusError as http_err:
            return f"请求失败: {http_err.response.status_code} {http_err.response.text}"
        except Exception as e:
            return f"请求异常: {str(e)}"


def get_ai_rule_json_chatgpt(direction=None):
    try:
        AI_prompt = AI_PROMPT_RULES + (direction or "") + AI_PROMPT_RULES_JSON_EXAMPLE
        result = asyncio.run(call_openai_api_async_with_rules(AI_prompt))
        if result == "处理超时":
            return "处理超时，请检查网络连接并重试"
        elif "请求失败" in result or "请求异常" in result:
            return result
        rule_json = result['choices'][0]['message']['content'].strip()
        return rule_json
    except Exception as e:
        return f"未知错误: {str(e)}"


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
        ai_response = asyncio.run(get_ai_analysis_chatgpt(dialogue_str, self.AI_prompt))
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
