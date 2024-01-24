import sqlite3

from exceptions import RuleNameExistsException
from rule_manager import Rule


def init_db():
    conn = sqlite3.connect('rules.db')  # 创建或连接到数据库
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''CREATE TABLE IF NOT EXISTS script_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scripts TEXT,
                        similarity_threshold REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS keyword_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        keywords TEXT,
                        check_type TEXT,
                        n INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS regex_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern TEXT)''')

    """
    
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

    """

    conn.commit()
    conn.close()


def rule_name_exists(rule_name):
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()

    cursor.execute('SELECT EXISTS(SELECT 1 FROM script_rules WHERE rule_name=? LIMIT 1)', (rule_name,))
    exists_in_script = cursor.fetchone()[0]

    cursor.execute('SELECT EXISTS(SELECT 1 FROM keyword_rules WHERE rule_name=? LIMIT 1)', (rule_name,))
    exists_in_keyword = cursor.fetchone()[0]

    cursor.execute('SELECT EXISTS(SELECT 1 FROM regex_rules WHERE rule_name=? LIMIT 1)', (rule_name,))
    exists_in_regex = cursor.fetchone()[0]

    conn.close()

    return exists_in_script or exists_in_keyword or exists_in_regex


# 添加规则
def add_rule(rule):
    if rule_name_exists(rule.rule_name):
        # 如果规则名称已存在，抛出异常
        raise RuleNameExistsException(rule.rule_name)

    """
    try:
    # 带有异常处理的规则，记得这么用。
    add_rule(new_rule)
except RuleNameExistsException as e:
    show_error_dialog(e.message)  # 显示一个错误对话框
    """

    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()

    # 添加脚本规则
    for script_rule in rule.script_rules:
        cursor.execute('INSERT INTO script_rules (scripts, similarity_threshold) VALUES (?, ?)',
                       (script_rule['scripts'], script_rule['similarity_threshold']))

    # 添加关键词规则
    for keyword_rule in rule.keyword_rules:
        cursor.execute('INSERT INTO keyword_rules (keywords, check_type, n) VALUES (?, ?, ?)',
                       (keyword_rule['keywords'], keyword_rule['check_type'], keyword_rule.get('n')))

    # 添加正则表达式规则
    for regex_rule in rule.regex_rules:
        cursor.execute('INSERT INTO regex_rules (pattern) VALUES (?)', (regex_rule['pattern'],))

    conn.commit()
    conn.close()


# 删除规则
def delete_rule(rule_name):
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()

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
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()

    # 查询脚本规则
    cursor.execute('SELECT scripts, similarity_threshold FROM script_rules WHERE rule_name = ?', (rule_name,))
    script_rules = cursor.fetchall()

    # 查询关键词规则
    cursor.execute('SELECT keywords, check_type, n FROM keyword_rules WHERE rule_name = ?', (rule_name,))
    keyword_rules = cursor.fetchall()

    # 查询正则表达式规则
    cursor.execute('SELECT pattern FROM regex_rules WHERE rule_name = ?', (rule_name,))
    regex_rules = cursor.fetchall()

    conn.close()

    # 构建 Rule 对象
    rule = Rule(rule_name)
    for script, threshold in script_rules:
        rule.add_script_rule(script, threshold)
    for keywords, check_type, n in keyword_rules:
        rule.add_keyword_rule(keywords, check_type, n)
    for pattern, in regex_rules:
        rule.add_regex_rule(pattern)

    return rule
