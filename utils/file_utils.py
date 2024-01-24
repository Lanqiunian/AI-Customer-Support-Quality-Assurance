import os

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
