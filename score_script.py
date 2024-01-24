import time
import webbrowser
from datetime import datetime

import requests
from plyer import notification  # 引入通知功能

url = 'http://yzfs.bupt.edu.cn/Open/Master/CjSignin.aspx'
previous_content = None


def fetch_content():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching the webpage: {e}")
        return None


def check_updates():
    global previous_content
    current_content = fetch_content()
    if current_content is None:
        return  # 如果获取内容失败，则直接返回

    # 获取当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if previous_content is None:
        previous_content = current_content
        print(f"[{current_time}] 初始化检查...")
    elif previous_content != current_content:
        notification.notify(
            title='网页更新通知',
            message='检测到网页内容变化，请检查。',
            app_name='网页变化检测'
        )
        print(f"[{current_time}] 检测到内容变化！正在打开网页...")
        webbrowser.open(url)  # 使用默认浏览器打开网页
        previous_content = current_content
    else:
        print(f"[{current_time}] 内容未发生变化。")


# 循环检查直到发现更新
while True:
    check_updates()
    time.sleep(20)  # 等待时间（秒），根据需要调整
