import os
import sqlite3

# 获取当前正在执行的脚本的绝对路径
current_script_path = os.path.abspath(__file__)
# 获取当前脚本所在的目录
current_directory = os.path.dirname(current_script_path)
# 回溯到项目根目录（假设 utils 目录在项目根目录下）
root_directory = os.path.dirname(current_directory)

# 构建数据库文件的绝对路径
RULE_DB_PATH = os.path.join(root_directory, 'repositories', 'rules.db')
REPOSITORY_PATH = os.path.join(root_directory, 'repositories')
DIALOGUE_DATA_PATH = os.path.join(root_directory, 'repositories', 'CT_dialogue.csv')
DIALOGUE_DB_PATH = os.path.join(root_directory, 'repositories', 'dialogue.db')
SCHEME_DB_PATH = os.path.join(root_directory, 'repositories', 'scheme.db')
DIMENSION_DB_PATH = os.path.join(root_directory, 'repositories', 'dimension.db')
TASK_DB_PATH = os.path.join(root_directory, 'repositories', 'task.db')
GLOBAL_DB_PATH = os.path.join(root_directory, 'repositories', 'global.db')


# 获取GLOBAL_DB_PATH中的参数

class AppConfig:
    def __init__(self, user_name, default_ai_prompt, api_key):
        self.user_name = user_name
        self.default_ai_prompt = default_ai_prompt
        self.api_key = api_key


def get_global_setting():
    conn = sqlite3.connect(GLOBAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM global")
    global_setting = cursor.fetchone()  # 假设只有一条记录
    conn.close()

    return AppConfig(*global_setting)


app_config = get_global_setting()

# Description: 全局配置文件
AI_PROMPT_RULES = """请根据以下需求，生成一组json格式的规则。需求："""
AI_PROMPT_RULES_JSON_EXAMPLE = """
。"regex_rules"，"keyword_rules"，"regex_rules"可以有0或多组，由你决定，你应当基于人类社会的生活情景，根据现实中的情况合理给出你的规则设计。
logic_expression描述了各组条件之间的关系，式子中必须包含全部的条件ID，例如condition_id最大值是4，那么就得包含1 2 3 4;满足这一logic_expression，说明命中了这一规则，请你根据需要设计这一逻辑关系。
"condition_id"是从"1"开始严格递增的
你禁止返回任何除了json之外的内容，也不要有任何注释，一个返回格式的例子如下，：
 {
    "rule_name": "客服问候有礼貌",
    "logic_expression": "(1 or not 2) and 3",
    "score_type": 1,
    "score_value": 5,
    "script_rules": [
        {
            "scripts": [
                "你好，很欢迎见到你",
                "很高兴为您服务",
            ],
            "similarity_threshold": 0.8,
            "condition_id": "1"
        }
    ],
    "keyword_rules": [
        {
            "keywords": [
                "嗨",
                "可以",
                "不行"
            ],
            "check_type": "any",
            "condition_id": "2",
            "n": null
        }
    ],
    "regex_rules": [
        {
            "pattern": "(怎么|如何|什么时候|哪里|谁).*",
            "condition_id": "3"
        }
    ]
}


"""
