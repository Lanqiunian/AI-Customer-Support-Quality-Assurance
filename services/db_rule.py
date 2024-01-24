from services.exceptions import RuleNameExistsException
from services.rule_manager import Rule
from utils.file_utils import RULE_DB_PATH, DIALOGUE_DB_PATH, SCHEME_DB_PATH, TASK_DB_PATH

"""

增删查改等数据库功能

"""


def init_db():
    # 初始化规则数据库
    conn_rule = sqlite3.connect(RULE_DB_PATH)
    cursor_rule = conn_rule.cursor()
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS rule_index (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT UNIQUE)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS script_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            scripts TEXT,
                            similarity_threshold REAL)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS keyword_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
                            keywords TEXT,
                            check_type TEXT,
                            n INTEGER)''')
    cursor_rule.execute('''CREATE TABLE IF NOT EXISTS regex_rules (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            rule_name TEXT,
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
                            manual_check INTEGER)''')  # 任务表

    cursor_task.execute('''CREATE TABLE IF NOT EXISTS datasets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data_name TEXT,
                            task_id INTEGER,
                            import_time TEXT,
                            FOREIGN KEY (task_id) REFERENCES tasks(id))''')  # 方案表

    cursor_task.execute('''CREATE TABLE IF NOT EXISTS evaluation_results (
                            task_id INTEGER,
                            dialogue_id TEXT PRIMARY KEY,
                            score INTEGER,
                            evaluation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    if rule_name_exists(rule.rule_name):
        # 如果规则名称已存在，抛出异常
        raise RuleNameExistsException(rule.rule_name)

    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 在 rule_index 表中插入规则名称，并获取新插入行的 id
    cursor.execute('INSERT INTO rule_index (rule_name) VALUES (?)', (rule.rule_name,))
    rule_id = cursor.lastrowid

    # 添加脚本规则
    for script_rule in rule.script_rules:
        for script in script_rule['scripts']:
            cursor.execute('INSERT INTO script_rules (rule_name, scripts, similarity_threshold) VALUES (?, ?, ?)',
                           (rule.rule_name, script, script_rule['similarity_threshold']))

    # 添加关键词规则
    for keyword_rule in rule.keyword_rules:
        for keyword in keyword_rule['keywords']:
            cursor.execute('INSERT INTO keyword_rules (rule_name, keywords, check_type, n) VALUES (?, ?, ?, ?)',
                           (rule.rule_name, keyword, keyword_rule['check_type'], keyword_rule.get('n')))

    # 添加正则表达式规则
    for regex_rule in rule.regex_rules:
        cursor.execute('INSERT INTO regex_rules (rule_name, pattern) VALUES (?, ?)',
                       (rule.rule_name, regex_rule['pattern'],))

    # 添加评分规则
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

    conn.commit()
    conn.close()


# 更新规则
def update_rule(existing_rule_name, new_rule):
    # 删除现有规则
    delete_rule(existing_rule_name)

    # 添加新规则
    add_rule(new_rule)


# 查询规则
def query_rule(rule_name):
    conn = sqlite3.connect(RULE_DB_PATH)
    cursor = conn.cursor()

    # 查询脚本规则
    cursor.execute('SELECT scripts, similarity_threshold FROM script_rules WHERE rule_name = ?', (rule_name,))
    script_rules_data = cursor.fetchall()

    # 查询关键词规则
    cursor.execute('SELECT keywords, check_type, n FROM keyword_rules WHERE rule_name = ?', (rule_name,))
    keyword_rules_data = cursor.fetchall()

    # 查询正则表达式规则
    cursor.execute('SELECT pattern FROM regex_rules WHERE rule_name = ?', (rule_name,))
    regex_rules = cursor.fetchall()

    cursor.execute('SELECT score_type, score_value FROM score_rules WHERE rule_name = ?', (rule_name,))
    score_type, score_value = cursor.fetchone()

    conn.close()

    # 构建 Rule 对象
    rule = Rule(rule_name)

    # 处理脚本规则
    script_rules = []
    similarity_threshold = None
    for script, threshold in script_rules_data:
        script_rules.append(script)
        similarity_threshold = threshold  # 假设所有脚本规则有相同的阈值
    if script_rules:
        rule.add_script_rule(script_rules, similarity_threshold)

    # 处理关键词规则
    for keywords, check_type, n in keyword_rules_data:
        rule.add_keyword_rule([keywords], check_type, n)  # 将关键词放入列表中

    # 处理正则表达式规则
    for pattern, in regex_rules:
        rule.add_regex_rule(pattern)

    # 处理评分规则
    rule.change_score_setting(score_type, score_value)

    return rule


import sqlite3


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
