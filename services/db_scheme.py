import sqlite3

from services.db_rule import query_rule
from utils.data_utils import list_to_text
from utils.file_utils import SCHEME_DB_PATH, TASK_DB_PATH


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

    def scheme_evaluate(self, dialogue_id, dialogue_df):
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor_record_result = conn.cursor()
        base_score = 100  # 基础分
        for rule in self.rules:
            # 对每个规则进行评估，并将结果保存到变量中
            evaluation_result = query_rule(rule).evaluate(dialogue_df)

            # 检查评估结果是否为元组，如果不是（即规则未命中），继续下一个规则
            if not evaluation_result:
                continue  # 规则未命中，继续评估下一个规则,下面的代码跳过

            # 如果规则命中，处理评分逻辑
            if isinstance(evaluation_result, tuple):
                score_type, score_value = evaluation_result
                print(score_type, score_value)
                if score_type == "0":
                    print(f"一次性评分,命中规则：", rule)
                    # 如果评分类型为一次性得分，直接返回该得分
                    return score_value
                elif score_type == "1":
                    print(f"加减分,命中规则：", rule)
                    # 如果是加减分，则在基础分上进行加减
                    base_score += score_value
            else:
                # 如果返回结果既不是 False 也不是元组，则打印错误或进行其他处理
                print("Unexpected return value from rule evaluation:", evaluation_result)

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
    print(f"scheme_data", scheme_data)
    if scheme_data:
        scheme = Scheme(scheme_name, scheme_data[0])
        for rule in rule_data:
            scheme.append(rule[0])
            print(f"添加了规则", rule[0])

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
    print(scheme_data)
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
