import sqlite3

from utils.file_utils import TASK_DB_PATH

conn = sqlite3.connect(TASK_DB_PATH)
cursor_task = conn.cursor()
cursor_task.execute('''Drop table if exists review_statistics''')
cursor_task.execute('''
    CREATE TABLE IF NOT EXISTS review_statistics (
        variable_name TEXT PRIMARY KEY,
        value INTEGER DEFAULT 0
    )
''')

# 初始化变量名和值
initial_values = [
    ("review_count", 0),
    ("review_completion_count", 0),
    ("review_mistake_count", 0)
]

# 插入初始值
for variable, value in initial_values:
    cursor_task.execute('''
        INSERT INTO review_statistics (variable_name, value)
        VALUES (?, ?)
    ''', (variable, value))

# 提交更改


conn.commit()
conn.close()
