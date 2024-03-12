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
DIALOGUE_DATA_PATH = os.path.join(root_directory, 'repositories', '中国电信数据集.csv')
DIALOGUE_DB_PATH = os.path.join(root_directory, 'repositories', 'dialogue.db')
SCHEME_DB_PATH = os.path.join(root_directory, 'repositories', 'scheme.db')
DIMENSION_DB_PATH = os.path.join(root_directory, 'repositories', 'dimension.db')
TASK_DB_PATH = os.path.join(root_directory, 'repositories', 'task.db')
GLOBAL_DB_PATH = os.path.join(root_directory, 'repositories', 'global.db')


# 获取GLOBAL_DB_PATH中的参数

class AppConfig:
    def __init__(self, user_name, default_ai_prompt, api_key, review_begin_inform, review_complete_inform):
        self.user_name = user_name
        self.default_ai_prompt = default_ai_prompt
        self.api_key = api_key
        self.review_complete_inform = review_complete_inform
        self.review_begin_inform = review_begin_inform


def get_global_setting():
    conn = sqlite3.connect(GLOBAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM global")
    global_setting = cursor.fetchone()  # 假设只有一条记录
    conn.close()

    return AppConfig(*global_setting)


app_config = get_global_setting()

# Description: 全局配置文件
AI_PROMPT_RULES = """请根据以下需求，生成一个json格式的规则。需求："""
AI_PROMPT_RULES_JSON_EXAMPLE = """
。"regex_rules"，"keyword_rules"，"regex_rules"可以有0或多组，由你决定，你应当基于人类社会的生活情景，根据现实中的情况合理给出你的规则设计。
logic_expression描述了各组条件之间的关系，式子中必须包含全部的条件ID，例如condition_id最大值是4，那么必须包含1 2 3 4;满足这一logic_expression，说明命中了这一规则，请你根据需要设计这一逻辑关系。
"condition_id"是从"1"开始严格递增的。
"target_role"如果为1，代表对用户发言检测，0代表对客服发言检测。请你根据客服交流的情景需要设计这一逻辑关系。
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