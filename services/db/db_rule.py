import json
import sqlite3
from collections import defaultdict

from services.exceptions import RuleNameExistsException
from services.rule_manager import Rule
from utils.global_utils import RULE_DB_PATH, DIALOGUE_DB_PATH, SCHEME_DB_PATH, TASK_DB_PATH, GLOBAL_DB_PATH

"""

增删查改等数据库功能

"""


def init_db():
    # 初始化规则数据库
    conn_rule = sqlite3.connect(RULE_DB_PATH)
    cursor_rule = conn_rule.cursor()
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS rule_index (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT UNIQUE,
                            logic_expression TEXT)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS script_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            condition_id INTEGER,
                            scripts TEXT,
                            similarity_threshold REAL)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS keyword_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            condition_id INTEGER,
                            keywords TEXT,
                            check_type TEXT,
                            n INTEGER)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS regex_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            condition_id INTEGER,
                            pattern TEXT)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS score_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            score_type TEXT,
                            score_value INTEGER)''')
    conn_rule.commit()
    conn_rule.close()

    # 初始化对话数据库
    conn_dialogue = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor_dialogue = conn_dialogue.cursor()
    cursor_dialogue.execute('''CREATE TABLE IF NOT EXISTS meta_table (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                data_name TEXT,
                                table_name TEXT,
                                import_time TEXT)''')
    conn_dialogue.commit()
    conn_dialogue.close()

    # 初始化方案数据库
    conn_SCHEME = sqlite3.connect(SCHEME_DB_PATH)
    cursor_SCHEME = conn_SCHEME.cursor()
    cursor_SCHEME.execute('''CREATE TABLE IF NOT EXISTS Schemes (
                              SCHEME_name TEXT PRIMARY KEY,
                              description TEXT)''')
    cursor_SCHEME.execute('''CREATE TABLE IF NOT EXISTS Scheme_Rule_Relationship (
                              SCHEME_name TEXT,
                              rule_name TEXT,
                              FOREIGN KEY (SCHEME_name) REFERENCES Schemes(SCHEME_name),
                              FOREIGN KEY (rule_name) REFERENCES rule_index(rule_name))''')
    conn_SCHEME.commit()
    conn_SCHEME.close()

    # 初始化任务数据库，选择方案，数据库，构成任务
    conn_task = sqlite3.connect(TASK_DB_PATH)
    cursor_task = conn_task.cursor()
    cursor_task.execute('''CREATE TABLE IF NOT EXISTS tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task_name TEXT,
                            task_description TEXT,
                            scheme TEXT,
                            manually_check INTEGER,
                            AI_prompt TEXT)''')  # 任务表

    cursor_task.execute('''CREATE TABLE IF NOT EXISTS datasets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data_name TEXT,
                            task_id INTEGER,
                            import_time TEXT,
                            FOREIGN KEY (task_id) REFERENCES tasks(id))''')  # 方案表

    cursor_task.execute('''CREATE TABLE IF NOT EXISTS evaluation_results (
                            task_id INTEGER,
                            dialogue_id TEXT,
                            score INTEGER,
                            evaluation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                            manually_check INTEGER DEFAULT 0,
                            manual_review_completed INTEGER DEFAULT 0,
                            manual_review_corrected_errors INTEGER DEFAULT 0,
                            FOREIGN KEY (task_id) REFERENCES tasks(id))''')  # 评估结果表

    cursor_task.execute('''CREATE TABLE IF NOT EXISTS hit_rules_details (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task_id INTEGER,
                            dialogue_id TEXT,
                            rule_name TEXT,
                            impact TEXT,
                            FOREIGN KEY (dialogue_id) REFERENCES evaluation_results(dialogue_id),
                            FOREIGN KEY (task_id) REFERENCES tasks(id))''')  # 命中规则详情表

    conn_task.commit()
    conn_task.close()

    conn_global = sqlite3.connect(GLOBAL_DB_PATH)
    cursor_global = conn_global.cursor()
    cursor_global.execute('''CREATE TABLE IF NOT EXISTS global (
                                user_name TEXT,
                                default_ai_prompt TEXT,
                                API_KEY TEXT)''')

    cursor_global.execute('SELECT COUNT(*) FROM global')
    data_exists = cursor_global.fetchone()[0] > 0

    # 如果表是新创建的且没有数据，插入初始值
    if not data_exists:
        cursor_global.execute('''INSERT INTO global (user_name, default_ai_prompt,API_KEY) VALUES ('admin', 
        '作为一位客服对话分析专家，你的任务是:1.识别客服在对话中的表现问题，2.给出改善建议。','sk-1234567890')''')

    conn_global.commit()
    conn_global.close()
    print("All databases have been initialized successfully.")

    """
    # 数据库表结构
## rule_index 表
| 字段名     | 数据类型 | 描述                    |
|------------|----------|------------------------|
| id         | INTEGER  | 唯一标识符，主键，自增  |
| rule_name  | TEXT     | 规则名称，唯一         |

## script_rules 表
| 字段名               | 数据类型  | 描述                           |
|----------------------|-----------|--------------------------------|
| id                   | INTEGER   | 唯一标识符，主键，自增         |
| rule_name            | TEXT      | 规则名称，与 Rule 对象关联     |
| scripts              | TEXT      | 脚本匹配规则的脚本内容         |
| similarity_threshold | REAL      | 脚本匹配的相似度阈值           |

## keyword_rules 表
| 字段名      | 数据类型 | 描述                                  |
|-------------|----------|---------------------------------------|
| id          | INTEGER  | 唯一标识符，主键，自增                 |
| rule_name   | TEXT     | 规则名称，与 Rule 对象关联            |
| keywords    | TEXT     | 关键词匹配规则的关键词列表             |
| check_type  | TEXT     | 关键词检测类型（如 'any'、'all' 等）   |
| n           | INTEGER  | ‘any_n’ 检测类型下的数字 n           |

## regex_rules 表
| 字段名     | 数据类型 | 描述                             |
|------------|----------|----------------------------------|
| id         | INTEGER  | 唯一标识符，主键，自增            |
| rule_name  | TEXT     | 规则名称，与 Rule 对象关联        |
| pattern    | TEXT     | 正则表达式匹配规则的模式           |


## score_rules 表
| 字段名       | 数据类型 | 描述                                      |
|--------------|----------|------------------------------------------|
| id           | INTEGER  | 唯一标识符，主键，自增                    |
| rule_name    | TEXT     | 评分规则的名称，与特定的评分逻辑关联      |
| score_type   | TEXT     | 评分类型（如"一次性得分"，"加减n分"等）   |
| score_value  | INTEGER  | 根据评分类型定义的分值                    |

-- 评估结果表 (evaluation_results)
-- | 字段名          | 数据类型 | 描述                                           |
-- |-----------------|----------|------------------------------------------------|
-- | task_id         | INTEGER  | 关联的任务ID，外键关联到tasks表的id            |
-- | dialogue_id     | TEXT     | 对话ID，唯一标识每个对话                       |
-- | score           | INTEGER  | 对话的总评分                                   |
-- | evaluation_time | DATETIME | 评估时间，默认为当前时间                       |
-- | FOREIGN KEY     |          | (task_id) REFERENCES tasks(id)    

-- 命中规则详情表 (hit_rules_details)
-- | 字段名      | 数据类型    | 描述                                     |
-- |-------------|-------------|------------------------------------------|
-- | task_id     | INTEGER     | 关联的任务ID，外键关联到tasks表的id      |
-- | id          | INTEGER     | 唯一标识符，主键，自增                   |
-- | dialogue_id | TEXT        | 对话ID，外键关联到evaluation_results表   |
-- | rule_name   | TEXT        | 命中的规则名称                           |
-- | impact      | TEXT        | 规则对总分数的影响           |
-- | FOREIGN KEY |             | (dialogue_id) REFERENCES evaluation_results(dialogue_id) |
-- | FOREIGN KEY |             | (task_id) REFERENCES tasks(id)           |


    """


def rule_name_exists(rule_name):
    """
    # 检查规则名称是否已存在
    :param rule_name:
    :return:是否存在。True为存在
    """
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT EXISTS(SELECT 1 FROM rule_index WHERE rule_name=? LIMIT 1)', (rule_name,))
    exists = cursor.fetchone()[0]

    conn.close()

    return exists


# 添加规则
def add_rule(rule):
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()
    if not rule_name_exists(rule.rule_name):
        # 规则名称不存在，插入新的规则名称到 rule_index 表中。如果存在，则只更新。
        cursor.execute('INSERT INTO rule_index (rule_name) VALUES (?)', (rule.rule_name,))
    else:
        # 删除规则绑定的脚本规则
        cursor.execute('DELETE FROM script_rules WHERE rule_name = ?', (rule.rule_name,))
        # 删除规则绑定的关键词规则
        cursor.execute('DELETE FROM keyword_rules WHERE rule_name = ?', (rule.rule_name,))
        # 删除规则绑定的正则表达式规则
        cursor.execute('DELETE FROM regex_rules WHERE rule_name = ?', (rule.rule_name,))
        # 删除规则绑定的评分规则
        cursor.execute('DELETE FROM score_rules WHERE rule_name = ?', (rule.rule_name,))
        # 删除规则绑定的评分规则
        cursor.execute('DELETE FROM score_rules WHERE rule_name = ?', (rule.rule_name,))
        # 删除规则绑定的逻辑表达式
        cursor.execute('UPDATE rule_index SET logic_expression = ? WHERE rule_name = ?',
                       (rule.logic_expression, rule.rule_name))
    # 添加逻辑表达式
    cursor.execute('UPDATE rule_index SET logic_expression = ? WHERE rule_name = ?',
                   (rule.logic_expression, rule.rule_name))
    # 添加脚本规则
    for script_rule in rule.script_rules:
        for script in script_rule['scripts']:
            cursor.execute(
                'INSERT INTO script_rules (rule_name, condition_id, scripts, similarity_threshold) VALUES (?, ?, ?, ?)',
                (rule.rule_name, script_rule['condition_id'], script, script_rule['similarity_threshold']))

    # 添加关键词规则
    for keyword_rule in rule.keyword_rules:
        for keyword in keyword_rule['keywords']:
            cursor.execute('INSERT INTO keyword_rules (rule_name, condition_id, keywords, check_type, n) VALUES (?, '
                           '?, ?, ?, ?)',
                           (rule.rule_name, keyword_rule['condition_id'], keyword, keyword_rule['check_type'],
                            keyword_rule.get('n', None)))

    # 添加正则表达式规则
    for regex_rule in rule.regex_rules:
        cursor.execute('INSERT INTO regex_rules (rule_name, condition_id, pattern) VALUES (?, ?, ?)',
                       (rule.rule_name, regex_rule['condition_id'], regex_rule['pattern']))

    # 添加评分规则，先删除可能存在的评分规则后再添加新的评分规则
    cursor.execute('DELETE FROM score_rules WHERE rule_name = ?', (rule.rule_name,))
    cursor.execute('INSERT INTO score_rules (rule_name, score_type, score_value) VALUES (?, ?, ?)',
                   (rule.rule_name, rule.score_type, rule.score_value))

    conn.commit()
    conn.close()


# 删除规则
def delete_rule(rule_name):
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 删除索引表
    cursor.execute('DELETE FROM rule_index WHERE rule_name = ?', (rule_name,))

    # 删除脚本规则
    cursor.execute('DELETE FROM script_rules WHERE rule_name = ?', (rule_name,))

    # 删除关键词规则
    cursor.execute('DELETE FROM keyword_rules WHERE rule_name = ?', (rule_name,))

    # 删除正则表达式规则
    cursor.execute('DELETE FROM regex_rules WHERE rule_name = ?', (rule_name,))

    conn_scheme = sqlite3.connect(SCHEME_DB_PATH)
    cursor_scheme = conn_scheme.cursor()

    # 在方案规则关系表中删除相关规则
    cursor_scheme.execute('DELETE FROM Scheme_Rule_Relationship WHERE rule_name = ?', (rule_name,))
    conn.commit()
    conn.close()
    conn_scheme.commit()
    conn_scheme.close()


def query_rule(rule_name):
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 查询脚本规则，并根据condition_id分组
    cursor.execute('SELECT condition_id, scripts, similarity_threshold FROM script_rules WHERE rule_name = ?',
                   (rule_name,))
    script_rules_data = cursor.fetchall()

    # 查询关键词规则，并根据condition_id分组
    cursor.execute('SELECT condition_id, keywords, check_type, n FROM keyword_rules WHERE rule_name = ?', (rule_name,))
    keyword_rules_data = cursor.fetchall()

    # 查询正则表达式规则
    cursor.execute('SELECT condition_id, pattern FROM regex_rules WHERE rule_name = ?', (rule_name,))
    regex_rules_data = cursor.fetchall()

    # 查询评分规则
    cursor.execute('SELECT score_type, score_value FROM score_rules WHERE rule_name = ?', (rule_name,))
    score_data = cursor.fetchone()
    score_type, score_value = score_data if score_data else (None, None)
    # 查询逻辑表达式
    cursor.execute('SELECT logic_expression FROM rule_index WHERE rule_name = ?', (rule_name,))
    logic_expression = cursor.fetchone()[0]

    conn.close()

    # 构建 Rule 对象
    rule = Rule(rule_name, score_type, score_value, logic_expression)

    # 处理脚本规则，先按condition_id分组
    script_rules_by_condition = {}
    for condition_id, scripts, similarity_threshold in script_rules_data:
        if condition_id not in script_rules_by_condition:
            script_rules_by_condition[condition_id] = {'scripts': [], 'similarity_threshold': similarity_threshold}
        script_rules_by_condition[condition_id]['scripts'].append(scripts)

    # 将分组后的脚本规则添加到Rule对象
    for condition_id, rule_data in script_rules_by_condition.items():
        rule.add_script_rule(rule_data['scripts'], rule_data['similarity_threshold'], condition_id)

    # 处理关键词规则，先按condition_id分组
    keyword_rules_by_condition = {}
    for condition_id, keywords, check_type, n in keyword_rules_data:
        if condition_id not in keyword_rules_by_condition:
            keyword_rules_by_condition[condition_id] = {'keywords': [], 'check_type': check_type, 'n': n}
        keyword_rules_by_condition[condition_id]['keywords'].append(keywords)

    # 将分组后的关键词规则添加到Rule对象
    for condition_id, rule_data in keyword_rules_by_condition.items():
        rule.add_keyword_rule(rule_data['keywords'], rule_data['check_type'], condition_id, rule_data['n'])

    # 处理正则表达式规则
    for condition_id, pattern in regex_rules_data:
        rule.add_regex_rule(pattern, condition_id)

    return rule


def get_script_by_name(script_name, get_type):
    """
    根据规则名称获取话术内容
    :param get_type: 0为话术，1为阈值,2为表格形式
    :param script_name: 规则名称
    :return: 格式化的话术内容或None
    """
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 查询脚本规则
    cursor.execute('SELECT scripts, similarity_threshold FROM script_rules WHERE rule_name = ?', (script_name,))
    script_rules_data = cursor.fetchall()

    conn.close()

    # 检查是否有查询结果
    if not script_rules_data:
        return None  # 如果查询结果为空，返回 None

    script_rules = []
    similarity_threshold = script_rules_data[0][1]  # 假设至少有一条数据返回

    if get_type == 0:
        for script, _ in script_rules_data:
            script_rules.append(script)
        return script_rules
    elif get_type == 1:
        return similarity_threshold
    elif get_type == 2:
        # 重新组织数据格式
        formatted_data = []
        for script, threshold in script_rules_data:
            formatted_data.append({
                'scripts': script,
                'similarity_threshold': threshold
            })
        return formatted_data


def get_keyword_by_name(rule_name, get_type):
    """
    根据规则名称获取关键词内容或检测类型
    :param rule_name: 规则的名称
    :param get_type: 0为返回关键词列表，1为返回检测类型
    :return: 关键词列表或检测类型列表
    """
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 一次查询获取所有相关信息
    cursor.execute('SELECT keywords, check_type FROM keyword_rules WHERE rule_name = ?', (rule_name,))
    results = cursor.fetchall()

    # 关闭数据库连接
    conn.close()

    if get_type == 0:
        # 提取并返回关键词列表
        keywords = [result[0] for result in results]
        return keywords
    elif get_type == 1:
        # 提取并返回检测类型（假设所有行的检测类型都相同，只返回第一行的检测类型）
        if results:
            return [results[0][1]]
        else:
            return []


def get_regex_by_name(rule_name):
    """
    根据规则名称获取正则表达式内容
    :param rule_name:
    :return:
    """
    # 连接数据库
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 查询关键词规则
    cursor.execute('SELECT pattern FROM regex_rules WHERE rule_name = ?', (rule_name,))
    regex_rules = cursor.fetchall()

    conn.close()
    script_rules = []
    for pattern, in regex_rules:
        script_rules.append(pattern)
    if script_rules:
        return script_rules
    else:
        return None


def get_score_by_name(rule_name, get_type):
    """
    根据规则名称获取评分规则
    :param rule_name:
    :param get_type: 0为评分类型，1为评分值
    :return:
    """
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT score_type, score_value FROM score_rules WHERE rule_name = ?', (rule_name,))
    score_type, score_value = cursor.fetchone()

    conn.close()

    if get_type == 0:
        return score_type
    elif get_type == 1:
        return score_value


def get_name_by_id(rule_id):
    """
    根据规则id获取规则名称
    :param rule_id:
    :return:
    """
    try:
        conn = sqlite3.connect(RULE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT rule_name FROM rule_index WHERE id = ?', (rule_id,))
        rule_name = cursor.fetchone()[0]

        conn.close()
        return rule_name

    except Exception as e:
        print("查询失败", e)
        return None


def rule_exists(rule_name):
    """
    检查规则是否存在
    :param rule_name:
    :return:
    """
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT EXISTS(SELECT 1 FROM rule_index WHERE rule_name=? LIMIT 1)', (rule_name,))
    exists = cursor.fetchone()[0]

    conn.close()

    return exists


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
                logic_expression=rule_data.get('logic_expression', None),
                score_type=rule_data.get('score_type', 1),
                score_value=rule_data.get('score_value', 0),
                script_rules=rule_data.get('script_rules', []),
                keyword_rules=rule_data.get('keyword_rules', []),
                regex_rules=rule_data.get('regex_rules', [])
            )
            add_rule(rule)
            print(f"规则 '{rule.rule_name}' 已成功导入数据库。")
        except Exception as e:
            print(f"导入规则时发生错误：{e}")


def fetch_rules(cursor, rule_name, query, rule_type):
    """
    从数据库中获取规则信息，并构造规则字典列表。
    """
    cursor.execute(query, (rule_name,))
    if rule_type == "keyword":
        # 处理关键词规则，关键词为逗号分隔的字符串转换为列表
        return [{"keywords": keywords.split(','), "check_type": check_type, "n": n, "condition_id": condition_id} for
                keywords, check_type, n, condition_id in cursor.fetchall()]
    elif rule_type == "script":
        # 处理脚本规则，确保scripts是一个列表
        return [
            {"scripts": scripts.split('|'), "similarity_threshold": similarity_threshold, "condition_id": condition_id}
            for scripts, similarity_threshold, condition_id in cursor.fetchall()]
    elif rule_type == "regex":
        # 处理正则表达式规则
        return [{"pattern": pattern, "condition_id": condition_id} for pattern, condition_id in cursor.fetchall()]


def export_rules_to_json(database_path, json_file_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute("SELECT rule_name, logic_expression FROM rule_index")
    rules_info = cursor.fetchall()

    exported_rules = {"rules": []}

    queries = {
        "script": "SELECT scripts, similarity_threshold, condition_id FROM script_rules WHERE rule_name = ?",
        "keyword": "SELECT keywords, check_type, n, condition_id FROM keyword_rules WHERE rule_name = ?",
        "regex": "SELECT pattern, condition_id FROM regex_rules WHERE rule_name = ?"
    }

    for rule_name, logic_expression in rules_info:
        score_type, score_value = cursor.execute("SELECT score_type, score_value FROM score_rules WHERE rule_name = ?",
                                                 (rule_name,)).fetchone() or (None, None)

        rule_dict = {
            "rule_name": rule_name,
            "logic_expression": logic_expression,
            "score_type": score_type,
            "score_value": score_value
        }

        for rule_type, query in queries.items():
            rule_dict[f"{rule_type}_rules"] = fetch_rules(cursor, rule_name, query, rule_type)

        exported_rules["rules"].append(rule_dict)

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(exported_rules, json_file, ensure_ascii=False, indent=4)

    print(f"Rules have been exported to {json_file_path}.")

    conn.close()
