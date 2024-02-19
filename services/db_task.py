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
        self.task_id = None

    def get_task_id(self):
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE task_name = ?", (self.task_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.task_id = result[0]
        else:
            self.task_id = None
        return self.task_id

    def process_task(self):
        self.get_task_id()
        for dataset in self.dataset_list:
            print(f"正在处理数据集 '{dataset}'...")
            # 在这里添加处理数据集的代码
            dialogues = load_data_from_db(dataset)
            dialogue_groups = dialogues.groupby("对话ID")
            for dialogue_id, dialogue_df in dialogue_groups:
                # 评估每个对话
                print(f"对话ID: {dialogue_id}")

                self.scheme.scheme_evaluate(self.task_id, dialogue_id, extract_service_messages(dialogue_df))
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
                       (self.task_name, self.description, self.scheme.scheme_name, self.manual_check))

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


def delete_task(task_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()

    # 删除与任务关联的数据集
    cursor.execute("DELETE FROM datasets WHERE task_id=?", (task_id,))

    # 删除与任务关联的评估结果和命中规则详情
    cursor.execute("DELETE FROM evaluation_results WHERE task_id=?", (task_id,))
    cursor.execute("DELETE FROM hit_rules_details WHERE task_id=?", (task_id,))

    # 删除任务本身
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    conn.commit()
    conn.close()

    print(f"任务 {task_id} 及其相关数据已被删除。")


def get_dialogue_count_by_task_id(task_id):
    """
    获取任务的对话数量
    :param task_id:
    :return:
    """
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT dialogue_id) FROM evaluation_results WHERE task_id=?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def get_average_score_by_task_id(task_id):
    """
    获取任务的平均分
    :param task_id:
    :return:
    """
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(score) FROM evaluation_results WHERE task_id=?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        # 保留整数
        return round(result[0], 1)
    else:
        return None


def get_hit_times_by_task_id(task_id):
    # 连接到数据库
    conn = sqlite3.connect(TASK_DB_PATH)  # 替换为实际的数据库路径
    cursor = conn.cursor()

    # 查询指定任务ID下的所有命中规则记录
    cursor.execute("""
        SELECT COUNT(*) 
        FROM hit_rules_details 
        WHERE task_id = ?
    """, (task_id,))

    # 获取查询结果，即命中规则的总次数
    hit_times = cursor.fetchone()[0]

    # 关闭数据库连接
    conn.close()

    return hit_times


def get_hit_rate_by_task_id(task_id):
    hit_rate = get_hit_times_by_task_id(task_id) / get_dialogue_count_by_task_id(task_id)
    # 转化为百分数
    hit_rate = str(round(hit_rate * 100, 2)) + '%'
    return hit_rate

# 用法示例
