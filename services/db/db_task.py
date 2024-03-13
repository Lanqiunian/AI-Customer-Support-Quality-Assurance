import sqlite3

from services.db.db_dialogue_data import load_data_from_db
from services.db.db_scheme import query_scheme, update_score_by_HitRulesList

from utils.global_utils import TASK_DB_PATH


class Task:
    def __init__(self, task_name, description, scheme_name, manually_check, AI_prompt=None):
        self.task_name = task_name
        self.description = description
        self.scheme = query_scheme(scheme_name)
        self.dataset_list = []
        self.manually_check = manually_check
        self.task_id = None
        self.AI_prompt = AI_prompt

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

                self.scheme.scheme_evaluate(self.task_id, dialogue_id, dialogue_df,
                                            self.manually_check)

            print(f"数据集 '{dataset}' 处理完成。")

    def append_dataset(self, dataset):
        if dataset not in self.dataset_list:
            self.dataset_list.append(dataset)

    def save_to_db(self):
        # 连接数据库
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        # 首先保存任务信息
        cursor.execute('''INSERT INTO tasks (task_name, task_description, scheme, manually_check, AI_prompt)
                          VALUES (?, ?, ?, ?, ?)''',
                       (self.task_name, self.description, self.scheme.scheme_name, self.manually_check, self.AI_prompt))

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


def get_AI_prompt_by_task_id(task_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT AI_prompt FROM tasks WHERE id=?", (task_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


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
    # 复检信息
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


def remove_hit_rule(task_id, dialogue_id, rule_name):
    print(f"正在删除任务ID为{task_id}，对话ID为{dialogue_id}，规则名为{rule_name}的命中规则...")
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM hit_rules_details WHERE task_id=? AND dialogue_id=? AND rule_name=?",
                   (task_id, dialogue_id, rule_name))
    conn.commit()
    # 获取一个hit_rules的List
    cursor.execute("SELECT rule_name FROM hit_rules_details WHERE task_id=? AND dialogue_id=?", (task_id, dialogue_id))
    original_list = cursor.fetchall()

    hit_rules = [item[0] for item in original_list]
    print(f"hit_rules: {hit_rules}")
    update_score_by_HitRulesList(task_id, dialogue_id, hit_rules)
    conn.commit()
    conn.close()


def add_hit_rule(task_id, dialogue_id, rule_name):
    print(f"正在添加任务ID为{task_id}，对话ID为{dialogue_id}，规则名为{rule_name}的命中规则...")
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hit_rules_details (task_id, dialogue_id, rule_name) VALUES (?, ?, ?)",
                   (task_id, dialogue_id, rule_name))
    conn.commit()
    # 获取一个hit_rules的List
    cursor.execute("SELECT rule_name FROM hit_rules_details WHERE task_id=? AND dialogue_id=?", (task_id, dialogue_id))
    original_list = cursor.fetchall()

    hit_rules = [item[0] for item in original_list]
    print(f"hit_rules: {hit_rules}")
    update_score_by_HitRulesList(task_id, dialogue_id, hit_rules)
    conn.commit()
    conn.close()


def get_task_id_by_task_name(task_name):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE task_name=?", (task_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def get_score_by_task_id_and_dialogue_id(task_id, dialogue_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM evaluation_results WHERE task_id=? AND dialogue_id=?", (task_id, dialogue_id))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def change_manual_check(task_id, dialogue_id, manually_check):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE evaluation_results SET manual_review_completed=? WHERE task_id=? AND dialogue_id=?",
                   (manually_check, task_id, dialogue_id))
    conn.commit()
    conn.close()
    print(f"任务ID为{task_id}，对话ID为{dialogue_id}的人工审核状态已更新为{manually_check}。")


def get_manually_check_by_task_id_and_dialogue_id(task_id, dialogue_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT manually_check FROM evaluation_results WHERE task_id=? AND dialogue_id=?",
                   (task_id, dialogue_id))
    result = cursor.fetchone()
    conn.close()
    if result:
        return str(result[0])
    else:
        return None


def get_overall_info():
    """
    获取已进行的全部任务的总体信息
        total_dialogue_count
        average_score
        hit_times
        hit_rate
    """
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM (SELECT DISTINCT task_id, dialogue_id FROM evaluation_results)")
    total_dialogue_count = cursor.fetchone()[0]
    cursor.execute("SELECT AVG(score) FROM evaluation_results")
    try:
        average_score = round(cursor.fetchone()[0], 1)
    except TypeError:
        average_score = 0
    # average_score = round(cursor.fetchone()[0], 1)
    cursor.execute("SELECT COUNT(*) FROM hit_rules_details")
    hit_times = cursor.fetchone()[0]
    if total_dialogue_count == 0:
        hit_rate = '0%'
    else:
        hit_rate = str(round(hit_times / total_dialogue_count * 100, 2)) + '%'
    conn.close()
    return total_dialogue_count, average_score, hit_times, hit_rate


def add_review_count(num):
    pass


def change_manual_review_corrected_errors(task_id, dialogue_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    # 更新 manual_review_corrected_errors 为 1
    cursor.execute("UPDATE evaluation_results SET manual_review_corrected_errors = 1 WHERE task_id=? AND "
                   "dialogue_id=?",
                   (task_id, dialogue_id))
    conn.commit()
    conn.close()
    print(f"任务ID为{task_id}，对话ID为{dialogue_id}的人工审核状态已更新为1。")


def get_review_statistics():
    """获取review_count, review_completion_count, review_mistake_count, 以字典的形式返回"""
    # 连接到数据库
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()

    # 查询要求人工复检的总数
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE manually_check = 1")
    review_count = cursor.fetchone()[0]

    # 查询已完成人工复检的总数
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE manual_review_completed = 1")
    review_completion_count = cursor.fetchone()[0]

    # 查询通过人工复检纠正的错误总数
    cursor.execute("SELECT COUNT(*) FROM evaluation_results WHERE manual_review_corrected_errors = 1")
    review_mistake_count = cursor.fetchone()[0]

    # 关闭数据库连接
    conn.close()
    print(
        f"review_count: {review_count}, review_completion_count: {review_completion_count}, review_mistake_count: {review_mistake_count}")
    # 返回结果
    return review_count, review_completion_count, review_mistake_count


def insert_review_comment(task_id, dataset_name, dialogue_id, review_comment):
    print(f"正在保存或更新任务ID为{task_id}，数据集名称为{dataset_name}，对话ID为{dialogue_id}的评价...")
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()

    # 首先检查是否存在具有相同 dataset_name 和 dialogue_id 的记录
    cursor.execute("SELECT * FROM analysis WHERE dataset_name = ? AND dialogue_id = ?",
                   (dataset_name, dialogue_id))
    exists = cursor.fetchone()

    if exists:
        # 如果存在，更新 review_comment
        cursor.execute("UPDATE analysis SET review_comment = ?, task_id = ? WHERE dataset_name = ? AND dialogue_id = ?",
                       (review_comment, task_id, dataset_name, dialogue_id))
        print(f"任务ID为{task_id}，数据集名称为{dataset_name}，对话ID为{dialogue_id}的评价已更新。")
    else:
        # 如果不存在，插入新记录
        cursor.execute("INSERT INTO analysis (task_id, dataset_name, dialogue_id, review_comment) VALUES (?, ?, ?, ?)",
                       (task_id, dataset_name, dialogue_id, review_comment))
        print(f"任务ID为{task_id}，数据集名称为{dataset_name}，对话ID为{dialogue_id}的评价已保存。")

    conn.commit()
    conn.close()


def check_review_exist(task_id, dialogue_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT review_comment FROM analysis WHERE task_id=? AND dialogue_id=?",
                   (task_id, dialogue_id))
    result = cursor.fetchone()
    conn.close()
    if result:
        print(f"已存在的评价", result[0])
        return result[0]

    else:
        print("不存在的评价")
        return False


def get_comment_by_task_id_and_dialogue_id(task_id, dialogue_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT review_comment FROM analysis WHERE task_id=? AND dialogue_id=?",
                   (task_id, dialogue_id))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None
