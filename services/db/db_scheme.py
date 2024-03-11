import sqlite3

from services.db.db_dialogue_data import load_data_from_db
from services.db.db_rule import query_rule
from utils.data_utils import list_to_text
from utils.global_utils import SCHEME_DB_PATH, TASK_DB_PATH, RULE_DB_PATH


# scheme类，多个rule组成一个scheme
class Scheme:
    def __init__(self, scheme_name, description):
        self.scheme_name = scheme_name
        self.description = description
        self.rules = []  # 存储与此方案相关联的规则对象

    def append(self, rule):
        if rule not in self.rules:
            self.rules.append(rule)

    def remove_rule(self, rule):
        self.rules.remove(rule)

    def save(self):
        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()

        # 检查方案是否已存在
        cursor.execute("SELECT scheme_name FROM Schemes WHERE scheme_name = ?", (self.scheme_name,))
        scheme_exists = cursor.fetchone()

        if scheme_exists:
            # 如果方案已存在，更新描述
            cursor.execute("UPDATE Schemes SET description = ? WHERE scheme_name = ?",
                           (self.description, self.scheme_name))
        else:
            # 否则，插入新方案
            cursor.execute("INSERT INTO Schemes (scheme_name, description) VALUES (?, ?)",
                           (self.scheme_name, self.description))

        # 更新方案和规则的关联
        # 首先，删除旧的关联
        cursor.execute("DELETE FROM Scheme_Rule_Relationship WHERE scheme_name = ?", (self.scheme_name,))

        # 然后，为方案添加新的规则关联
        for rule in self.rules:
            # 确保规则已经存在于 Rules 表中
            cursor.execute("INSERT INTO Scheme_Rule_Relationship (scheme_name, rule_name) VALUES (?, ?)",
                           (self.scheme_name, rule))

        conn.commit()  # 提交事务
        conn.close()  # 关闭数据库连接

        print(f"方案 '{self.scheme_name}' 已保存到数据库。")

    def update(self, new_scheme_name, new_description):
        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE Schemes SET scheme_name = ?, description = ? WHERE scheme_name = ?",
                       (new_scheme_name, new_description, self.scheme_name))
        cursor.execute("UPDATE Scheme_Rule_Relationship SET scheme_name = ? WHERE scheme_name = ?",
                       (new_scheme_name, self.scheme_name))
        conn.commit()
        conn.close()

        print(f"方案 '{self.scheme_name}' 已更新。")

    def scheme_evaluate(self, task_id, dialogue_id, dialogue_df, manually_check):
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        base_score = 100  # 基础分
        hit_rules = []  # 用于存储命中的规则及其影响

        for rule in self.rules:
            evaluation_result = query_rule(rule).evaluate(dialogue_df)

            if not evaluation_result:
                continue  # 规则未命中

            if isinstance(evaluation_result, tuple):
                score_type, score_value = evaluation_result

                # 记录命中的规则及其影响
                hit_rules.append((rule, score_value))

                if score_type == "0":
                    # 一次性评分, 直接返回该得分并结束评估
                    base_score = score_value
                    break
                elif score_type == "1":
                    # 加减分
                    base_score += score_value

        # 将评分结果保存到数据库
        cursor.execute('''
            INSERT INTO evaluation_results (task_id, dialogue_id, score,manually_check)
            VALUES (?, ?, ?, ?)
        ''', (task_id, dialogue_id, base_score, manually_check))

        # 获取最新插入评分结果的ID
        result_id = cursor.lastrowid
        load_data_from_db("测试数据1")
        # 将命中的规则详情保存到数据库
        for rule, impact in hit_rules:
            cursor.execute('''
                INSERT INTO hit_rules_details (task_id, dialogue_id, rule_name, impact)
                VALUES (?, ?, ?, ?)
            ''', (task_id, dialogue_id, rule, impact))

        conn.commit()
        conn.close()

        return base_score


def update_score_by_HitRulesList(task_id, dialogue_id, hit_rules):
    """
    更新数据库中的评分记录
    :param task_id: 任务ID
    :param dialogue_id: 对话ID
    :param hit_rules: 命中的规则列表,储存名称
    :return: base_score
    """
    # 基础分数设置为 100，或者你可以从数据库读取初始分数
    base_score = 100
    conn_rule = sqlite3.connect(RULE_DB_PATH)
    cursor_rule = conn_rule.cursor()

    # 遍历每个命中的规则名称
    for rule_name in hit_rules:
        # 从 score_rules 表中获取评分类型和影响分值
        cursor_rule.execute('''
            SELECT score_type, score_value FROM score_rules
            WHERE rule_name = ?
        ''', (rule_name,))
        rule_info = cursor_rule.fetchone()
        if rule_info:
            score_type, score_value = rule_info
            if score_type == "0":
                # 一次性评分, 直接设置分数并结束循环
                base_score = int(score_value)
                break
            elif score_type == "1":
                # 加减分, 在基础分上进行加减
                base_score += int(score_value)

    conn_rule.close()  # 关闭规则数据库连接

    conn_task = sqlite3.connect(TASK_DB_PATH)
    cursor_task = conn_task.cursor()

    # 更新数据库中的评分记录
    cursor_task.execute('''
        UPDATE evaluation_results
        SET score = ?
        WHERE task_id = ? AND dialogue_id = ?
    ''', (base_score, task_id, dialogue_id))

    conn_task.commit()
    conn_task.close()  # 关闭任务数据库连接

    print(f"Task ID: {task_id}, Dialogue ID: {dialogue_id} score has been updated to {base_score}.")
    return base_score


def query_scheme(scheme_name):
    # 从数据库中查询方案，构建一个方案对象，然后返回
    conn = sqlite3.connect(SCHEME_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM Schemes WHERE scheme_name = ?", (scheme_name,))
    scheme_data = cursor.fetchone()
    cursor.execute("SELECT rule_name FROM Scheme_Rule_Relationship WHERE scheme_name = ?", (scheme_name,))
    rule_data = cursor.fetchall()

    conn.close()
    if scheme_data:
        scheme = Scheme(scheme_name, scheme_data[0])
        for rule in rule_data:
            scheme.append(rule[0])
        return scheme

    else:
        return None


def delete_scheme(scheme_name):
    conn = sqlite3.connect(SCHEME_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Schemes WHERE scheme_name = ?", (scheme_name,))
    conn.commit()
    conn.close()
    print(f"方案 '{scheme_name}' 已从数据库中删除。")


# 通过规则名，获取所属方案,返回唯一方案名字符串
def get_scheme_by_rule_name(rule_name):
    """
    通过规则名，获取所属方案
    :param rule_name:
    :return: 一个字符串，包含所有包含该规则的方案名，用空格分隔
    """
    conn = sqlite3.connect(SCHEME_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT scheme_name FROM Scheme_Rule_Relationship WHERE rule_name = ?", (rule_name,))
    scheme_data = cursor.fetchall()
    conn.close()
    scheme_names = [item[0] for item in scheme_data]
    scheme_str = list_to_text(scheme_names)
    return scheme_str


# 假设的辅助函数，根据方案name从数据库获取规则
def get_rules_by_scheme_name(scheme_name):
    conn = sqlite3.connect(SCHEME_DB_PATH)
    cursor = conn.cursor()

    # 只选择与scheme_name相关联的规则名称
    cursor.execute("SELECT rule_name FROM Scheme_Rule_Relationship WHERE scheme_name = ?", (scheme_name,))
    rules_data = cursor.fetchall()

    # 从查询结果中提取规则名称，并构建规则名称列表
    rule_list = [rule_name[0] for rule_name in rules_data]

    print(rule_list)
    conn.close()
    return rule_list
