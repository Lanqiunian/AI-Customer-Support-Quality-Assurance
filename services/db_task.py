import sqlite3

from services.db_dialogue_data import load_data_from_db
from services.db_scheme import query_scheme
from utils.data_utils import extract_service_messages
from utils.file_utils import TASK_DB_PATH


class Task:
    def __init__(self, task_name, description, scheme_name, manual_check):
        self.task_name = task_name
        self.description = description
        self.scheme = query_scheme(scheme_name)
        self.dataset_list = []
        self.manual_check = manual_check

    def process_task(self):
        for dataset in self.dataset_list:
            print(f"正在处理数据集 '{dataset}'...")
            # 在这里添加处理数据集的代码
            dialogues = load_data_from_db(dataset)
            dialogue_groups = dialogues.groupby("对话ID")
            for dialogue_id, dialogue_df in dialogue_groups:
                # 评估每个对话
                print(f"对话ID: {dialogue_id}")

                self.scheme.scheme_evaluate(extract_service_messages(dialogue_df))
                print(f"对话内容:\n{extract_service_messages(dialogue_df)}")
            print(f"数据集 '{dataset}' 处理完成。")

    def append_dataset(self, dataset):
        if dataset not in self.dataset_list:
            self.dataset_list.append(dataset)

    def save_to_db(self):
        # 连接数据库
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        # 首先保存任务信息
        cursor.execute('''INSERT INTO tasks (task_name, task_description, scheme, manual_check)
                          VALUES (?, ?, ?, ?)''',
                       (self.task_name, self.description, self.scheme_name, self.manual_check))

        # 获取刚刚插入的任务的ID
        task_id = cursor.lastrowid

        # 对于任务关联的每个数据集，将其保存到数据库
        for dataset_name in self.dataset_list:
            cursor.execute('''INSERT INTO datasets (data_name, task_id, import_time)
                              VALUES (?, ?, datetime('now'))''', (dataset_name, task_id))

        # 提交事务
        conn.commit()
        # 关闭数据库连接
        conn.close()

        print(f"任务 '{self.task_name}' 及其数据集已保存到数据库。")

# 用法示例
