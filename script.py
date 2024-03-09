import json
import sqlite3

from services.db_rule import add_rule
from services.rule_manager import Rule
from utils.file_utils import TASK_DB_PATH


def import_rules_from_json(json_file_path):
    """
    从 JSON 文件批量导入规则到数据库。

    :param json_file_path: JSON 文件的路径。
    """
    # 加载 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        rules_data = json.load(file)

    # 遍历每个规则并保存到数据库
    for rule_data in rules_data['rules']:
        try:
            rule = Rule(
                rule_name=rule_data['rule_name'],
                score_type=rule_data.get('score_type', 1),
                score_value=rule_data.get('score_value', 0),
                script_rules=rule_data.get('script_rules', []),
                keyword_rules=rule_data.get('keyword_rules', []),
                regex_rules=rule_data.get('regex_rules', [])
            )
            add_rule(rule)
            print(f"规则 '{rule.rule_name}' 已成功导入数据库。")
        except Exception as e:
            print(f"导入规则 '{rule.rule_name}' 时发生错误：{e}")


# 示例调用
json_file_path = 'repositories/json/rule.json'
import_rules_from_json(json_file_path)
