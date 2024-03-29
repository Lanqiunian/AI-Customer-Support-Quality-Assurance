import os
import sqlite3
import os
import sys
from pathlib import Path


def get_database_path(db_name):
    # 获取用户的AppData目录
    app_data_path = Path(os.getenv('APPDATA'))
    # 指定你的应用程序特定的子目录
    app_dir = app_data_path / 'AI Customer Support Quality Assurance'
    print(f"app_dir", app_dir)
    # 如果目录不存在，则创建它
    app_dir.mkdir(parents=True, exist_ok=True)
    # 返回数据库文件的完整路径
    return app_dir / db_name


# 使用新的方法获取数据库路径
RULE_DB_PATH = get_database_path('rules.db')
DIALOGUE_DB_PATH = get_database_path('dialogue.db')
SCHEME_DB_PATH = get_database_path('scheme.db')
DIMENSION_DB_PATH = get_database_path('dimension.db')
TASK_DB_PATH = get_database_path('task.db')
GLOBAL_DB_PATH = get_database_path('global.db')


def resource_path(relative_path):
    """ 获取资源的绝对路径。用于访问打包环境中的资源文件。"""
    try:
        # PyInstaller创建的临时文件夹中的路径
        base_path = sys._MEIPASS
    except Exception:
        # 如果没有打包，使用当前文件的相对路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


UI_PATH = resource_path('ui/main_window.ui')


# 获取GLOBAL_DB_PATH中的参数

class AppConfig:
    def __init__(self, user_name, default_ai_prompt, api_key, review_begin_inform, review_complete_inform):
        self.user_name = user_name
        self.default_ai_prompt = default_ai_prompt
        self.api_key = api_key
        self.review_complete_inform = review_complete_inform
        self.review_begin_inform = review_begin_inform


def get_global_setting():
    conn_global = sqlite3.connect(GLOBAL_DB_PATH)
    cursor_global = conn_global.cursor()
    cursor_global.execute('''CREATE TABLE IF NOT EXISTS global (
                                   user_name TEXT,
                                   default_ai_prompt TEXT,
                                   API_KEY TEXT,
                                   review_begin_inform INTEGER,
                                   review_complete_inform INTEGER)''')

    cursor_global.execute('SELECT COUNT(*) FROM global')
    data_exists = cursor_global.fetchone()[0] > 0

    # 如果表是新创建的且没有数据，插入初始值
    if not data_exists:
        cursor_global.execute('''INSERT INTO global (user_name, default_ai_prompt,API_KEY,review_begin_inform,
        review_complete_inform) VALUES ('admin', '作为一位客服对话分析专家，你的任务是:1.识别客服在对话中的表现问题，2.给出改善建议。','sk-1234567890',1,1)''')

        global_setting = (
            'admin', '作为一位客服对话分析专家，你的任务是:1.识别客服在对话中的表现问题，2.给出改善建议。',
            'sk-1234567890', 1,
            1)
        conn_global.commit()
        conn_global.close()
    else:
        cursor_global.execute("SELECT * FROM global")
        global_setting = cursor_global.fetchone()
        print(f"global_setting", global_setting)  # 假设只有一条记录
        conn_global.close()

    return AppConfig(*global_setting)


app_config = get_global_setting()

# Description: 全局配置文件
AI_PROMPT_RULES = """请根据以下需求，生成一个json格式的规则。需求："""
AI_PROMPT_RULES_JSON_EXAMPLE = """
。"regex_rules"，"keyword_rules"，"regex_rules"可以有0或多组，由你决定，你应当基于人类社会的生活情景，根据现实中的情况合理给出你的规则设计。
logic_expression描述了各组条件之间的关系，式子中必须包含全部的条件ID，例如condition_id最大值是4，那么必须包含1 2 3 4;满足这一logic_expression，说明命中了这一规则，请你根据需要设计这一逻辑关系。
"condition_id"是从"1"开始严格递增的。
"target_role"如果为1，代表对用户发言检测，0代表对客服发言检测。请你根据客服交流的情景需要设计这一逻辑关系。
"score_type"为1，代表加减总得分，值为score_value。为0，代表命中直接给分为score_value。
你禁止返回任何除了json之外的内容，也不要有任何注释，下面是一组返回格式的例子，你不需要返回一组，你必须只能返回一条：
        {
            "rule_name": "回应用户感谢",
            "logic_expression": "1 and 2",
            "score_type": "1",
            "score_value": 10,
            "script_rules": [
                {
                    "condition_id": 1,
                    "scripts": [
                        "不用谢",
                        "这是我们应该的"
                    ],
                    "similarity_threshold": 0.5,
                    "target_role": 0
                }
            ],
            "keyword_rules": [
                {
                    "condition_id": 2,
                    "keywords": [
                        "非常好",
                        "太棒了",
                        "服务很好"
                    ],
                    "check_type": "any",
                    "n": null,
                    "target_role": 1
                }
            ],
            "regex_rules": []
        },
          {
            "rule_name": "客服推销产品优势",
            "logic_expression": "1 and (2 or 3)",
            "score_type": "1",
            "score_value": 10,
            "script_rules": [
                {
                    "condition_id": 1,
                    "scripts": [
                        "这款 怎么样",
                        "你们产品有什么优势？"
                    ],
                    "similarity_threshold": 0.5,
                    "target_role": 0
                }
            ],
            "keyword_rules": [
                {
                    "condition_id": 2,
                    "keywords": [
                        "在行业内领先的性能",
                        "相比友商的产品"
                    ],
                    "check_type": "any",
                    "n": null,
                    "target_role": 0
                }
            ],
            "regex_rules": [
                {
                    "condition_id": 3,
                    "pattern": "(性能|价格|服务|质量|功能|特点|优势|特色|特性|特点|特征)",
                    "target_role": 0
                }


"""
