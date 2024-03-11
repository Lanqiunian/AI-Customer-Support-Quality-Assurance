import sqlite3
from datetime import datetime

import pandas as pd

from utils.global_utils import DIALOGUE_DB_PATH, TASK_DB_PATH


# 数据库总览:
# 1. meta_table: 存储每次数据导入的元信息，如数据集名称、表名和导入时间。
# 2. dialogue_<timestamp>: 每次导入数据时创建的表，存储对话数据，<timestamp> 代表导入的时间戳，确保表名的唯一性。

# 元表 (meta_table) 结构:
# | 字段名     | 数据类型    | 描述                                   |
# |------------|-------------|----------------------------------------|
# | id         | INTEGER     | 唯一标识符，主键，自增                 |
# | data_name  | TEXT        | 数据集名称，描述导入数据的标识         |
# | table_name | TEXT        | 对应的对话数据表名称                   |
# | import_time| TEXT        | 数据导入时间，格式为 'YYYY-MM-DD_HH-MM-SS' |

def import_dialogue_data(dataName, dataPath, use_existing_db=False):
    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()

    if not use_existing_db:
        # 创建元表，如果不存在的话
        cursor.execute('''CREATE TABLE IF NOT EXISTS meta_table (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data_name TEXT,
                            table_name TEXT,
                            import_time TEXT)''')

        # 当前时间，用于表名和记录导入时间
        current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        table_name = "dialogue_" + current_time_str

        try:
            dialogue_data = pd.read_csv(dataPath, encoding='utf-8')
            dialogue_data.to_sql(table_name, conn, if_exists='replace', index=False)
            cursor.execute('INSERT INTO meta_table (data_name, table_name, import_time) VALUES (?, ?, ?)',
                           (dataName, table_name, current_time_str))
            conn.commit()
            print("数据加载并存储到新表成功。")
        except Exception as e:
            print(f"数据加载失败：{e}")
    else:
        print("使用已有数据库。")

    conn.close()


def get_table_name_by_id(dataset_id):
    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM meta_table WHERE id = ?', (dataset_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


def load_data_from_db(data_name):
    # 传入data_name,找到对应的table_name，然后返回对应的dataframe
    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM meta_table WHERE data_name = ?', (data_name,))
    result = cursor.fetchone()
    if result:
        table_name = result[0]
        # 注意表名要用双引号括起来,这可以确保即便表名中包含了-这样的特殊字符，SQL查询也能够正确执行，不会引发语法错误。
        query = f'SELECT * FROM "{table_name}"'
        df = pd.read_sql_query(query, conn)
    else:
        df = None
    return df


def get_dialogue_by_datasetname_and_dialogueid(dataset_name, dialogue_id):
    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM meta_table WHERE data_name = ?', (dataset_name,))
    result = cursor.fetchone()
    if result:
        table_name = result[0]
        query = f"SELECT * FROM '{table_name}' WHERE 对话ID = '{dialogue_id}'"
        df = pd.read_sql_query(query, conn)
    else:
        df = None
    return df


def dialogue_info(dataset_id):
    table_name = get_table_name_by_id(dataset_id)
    if table_name:
        query = f"SELECT * FROM {table_name}"
        df = load_data_from_db(query)
        print("\n数据基本信息：")
        print(df.info())
    else:
        print("指定的数据集 ID 不存在。")


def customer_message_count(dataset_id):
    table_name = get_table_name_by_id(dataset_id)
    if table_name:
        query = f"SELECT 客户ID, COUNT(*) as message_count FROM {table_name} GROUP BY 客户ID"
        df = load_data_from_db(query)
        print("\n每个客户的消息数量：")
        print(df)
        return df
    else:
        print("指定的数据集 ID 不存在。")


def get_dialogue_by_session(dataset_id, specific_dialogue_id):
    table_name = get_table_name_by_id(dataset_id)
    if table_name:
        query = f"SELECT 客户ID, 客服ID, 消息内容, 发送方, 发送时间 FROM {table_name} WHERE 对话ID = '{specific_dialogue_id}'"
        df = load_data_from_db(query)
        return df
    else:
        print("指定的数据集 ID 不存在。")


def get_dialogue_by_customer(dataset_id, specific_customer_id):
    table_name = get_table_name_by_id(dataset_id)
    if table_name:
        query = f"SELECT * FROM {table_name} WHERE 客户ID = '{specific_customer_id}'"
        df = load_data_from_db(query)
        print(f"\n客户 {specific_customer_id} 的对话：")
        print(df)
        return df
    else:
        print("指定的数据集 ID 不存在。")


def delete_dataset_by_name(dataset_name):
    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM meta_table WHERE data_name = ?', (dataset_name,))
    result = cursor.fetchone()
    if result:
        table_name = result[0]
        print(f" {dataset_name, table_name} ...")
        cursor.execute('DELETE FROM meta_table WHERE data_name = ?', (dataset_name,))
        cursor.execute(f'DROP TABLE "{table_name}"')
        conn.commit()
        print(f"数据集 {dataset_name} 已删除。")
    else:
        print(f"数据集 {dataset_name} 不存在。")
    conn.close()


#############以下方法是基于DataFrame的操作#############
def count_unique_dialogues(df):
    """
    计算DataFrame中唯一对话ID的数量。

    参数:
    df (pandas.DataFrame): 包含对话数据的DataFrame，假设有一个名为'对话ID'的列。

    返回:
    int: 唯一对话ID的数量。
    """
    if '对话ID' in df.columns:
        unique_dialogue_count = df['对话ID'].nunique()
        print(f"总共有 {unique_dialogue_count} 个唯一对话。")
        return unique_dialogue_count
    else:
        print("DataFrame中没有找到'对话ID'列。")
        return 0


def get_service_id_by_dialogue_id_and_task_id(task_id, dialogue_id):
    dataset_id = get_dataset_by_task_id(task_id)[0]

    conn = sqlite3.connect(DIALOGUE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT table_name FROM meta_table WHERE data_name = ?', (dataset_id,))

    try:

        dataset_name = cursor.fetchone()[0]
    except:
        print('No such dataset')
        dataset_name = "未知"
        return None
    df = load_data_from_db(dataset_id)
    if df is not None:
        if '对话ID' in df.columns and '客服ID' in df.columns:
            service_id = df[df['对话ID'] == dialogue_id]['客服ID'].iloc[0]

            return service_id
        else:
            print("DataFrame中没有找到'对话ID'或'客服ID'列。")
            return None
    else:
        print(f"数据集 {dataset_name} 不存在。")
        return None


def get_dataset_by_task_id(task_id):
    conn = sqlite3.connect(TASK_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data_name FROM datasets WHERE task_id=?", (task_id,))
    result = cursor.fetchall()

    conn.close()

    if result:
        return [item[0] for item in result]

    else:
        return None


if __name__ == "__main__":
    get_service_id_by_dialogue_id_and_task_id(7, 1)
