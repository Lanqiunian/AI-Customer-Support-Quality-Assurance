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
def get_global_setting():
    global USER_NAME, DEFAULT_AI_PROMPT, API_KEY  # 声明全局变量

    conn = sqlite3.connect(GLOBAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM global")
    global_setting = cursor.fetchall()
    conn.close()

    # 假设 global_setting[0] 包含三个元素
    USER_NAME, DEFAULT_AI_PROMPT, API_KEY = global_setting[0]
    print(f"重新获取", USER_NAME, DEFAULT_AI_PROMPT, API_KEY)
    return global_setting[0]


USER_NAME, DEFAULT_AI_PROMPT, API_KEY = get_global_setting()

# Description: 全局配置文件
AI_PROMPT_RULES = """请根据以下需求，生成一组json格式的规则。需求："""
AI_PROMPT_RULES_JSON_EXAMPLE = """
。你禁止返回任何除了json之外的内容，也不要有任何注释，一个返回格式的例子如下，：
 {
    "rule_name": "例子",
    "score_type": 1,
    "score_value": 5,
    "script_rules": [
        {
            "scripts": [
                "笑了",
                "可以尝试一下哦"
            ],
            "similarity_threshold": 0.8,
            "condition_id": "1"
        }
    ],
    "keyword_rules": [
        {
            "keywords": [
                "请",
                "谢谢",
                "不客气"
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
