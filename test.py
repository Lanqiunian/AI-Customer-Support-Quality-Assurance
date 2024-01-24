import pandas as pd

from services.db_dialogue_data import load_data_from_db, count_unique_dialogues
from utils.data_utils import Dialogue, extract_service_messages
from utils.file_utils import DIALOGUE_DATA_PATH


def function_test():
    global test_0, data
    test_0 = Dialogue(DIALOGUE_DATA_PATH)
    # 手动定义service_replies DataFrame
    data = {
        '客户ID': ['123', '123'],
        '客服ID': ['456', '456'],
        '消息内容': ['傻逼东西', '智障玩意儿'],
        '发送方': [0, 0],
        '发送时间': ['2023/8/20 16:05:00', '2023/8/21 16:05:00']
    }
    df = load_data_from_db("电信客服")
    print(load_data_from_db("电信客服"))
    print(count_unique_dialogues(load_data_from_db("电信客服")))

    dialogue_groups = df.groupby("对话ID")

    for dialogue_id, dialogue_df in dialogue_groups:
        # 评估每个对话
        print(f"对话ID: {dialogue_id}")
        print(f"对话内容:\n{extract_service_messages(dialogue_df)}")

    service_replies = extract_service_messages(pd.DataFrame(data))

    # print(service_replies)
    # # 话术检测
    # scripts = ["您好，我们现在有试听课，您方便参加吗", "您可以先听一下试听课，感受一下", "我帮您预约时间，您什么时间方便呢"]
    # scripts_result = Script_Matching(scripts, service_replies, 0.7)
    # print(f"话术检测结果：{scripts_result}")
    # # 关键词检测
    # keywords = ['您', '可以', '试听课', '报名', '孩子']
    # keyword_result = Keywords_Matching(service_replies, keywords, 'all')
    # print(f"关键词检测结果：{keyword_result}")
    # # 正则表达式检测
    # # Assume material_to_evaluate is a Pandas Series containing service replies
    # pattern = "(孩子|娃|姑娘).{0,4}(多大|几岁)|(孩子|娃|姑娘|上).{0,3}(几年级|初几|高几)|您.{0,3}做什么|什么工作|报过.{0,3}(其他|别的).{0,3}辅导班"
    # regex_result = Regex_Matching(pattern, service_replies)
    # print(f"正则表达式检测结果：{regex_result}")
    #
    # # 新建规则对象
    # test_rule = rm.Rule("测试规则0")
    # test_rule.add_script_rule(scripts, 0.1)
    # test_rule.add_keyword_rule(keywords, 'all')
    # test_rule.add_regex_rule(pattern)
    # test_rule.change_score_setting(1, -5)
    # print(test_rule.evaluate(service_replies))
    #
    # # 数据库操作
    # # delete_rule("测试规则1")
    # # add_rule(test_rule)
    # print("执行了添加规则到数据库")
    #
    # # 查询规则，并使用
    # rule_query = query_rule("测试规则1")
    # print(f"提取后规则命中结果为", rule_query.evaluate(service_replies))
    #
    # # get方法
    # print(f"ID为1的规则为：", get_name_by_id(1))
    #
    # print(f"查询对应正则表达式为:", get_regex_by_name("测试规则1"))
    #
    # print(f"查询对应关键词为：", get_keyword_by_name("测试规则1", 0))
    # print(f"查询对应关键词匹配类型为：", get_keyword_by_name("测试规则1", 1))
    #
    # print(f"查询对应话术为：", get_script_by_name("测试规则1", 0))
    # print(f"查询对应阈值为：", get_script_by_name("测试规则1", 1))

    # import_data_to_db("测试数据1", DIALOGUE_DATA_PATH, use_existing_db=False)

    # delete_dataset_by_name("测试数据1")

    # test_scheme = Scheme("测试方案1", "测试方案描述1")
    # test_scheme.append("test0")
    # test_scheme.append("test1")
    # test_scheme.save()
    #
    # test_scheme0 = Scheme("测试方案2", "测试方案描述2")
    # test_scheme0.append("test0")
    # test_scheme0.save()
    #
    # print(f"执行了方案评估", test_scheme.scheme_evaluate(service_replies))
    #
    # print(get_scheme_by_rule_name("test0"))
    #
    # query_scheme("测试方案1")
    #
    # my_task = Task("Task1", "This is a test task.", "Scheme1", 1)
    # my_task.append_dataset("Dataset1")
    # my_task.append_dataset("Dataset2")
    # my_task.save_to_db()
    # 获取特定对话ID的内容
    # print(test_0.getDialogueBySession(17))

    # 大模型对话分析功能
    # feedback1 = analyze_customer_service_interaction(test_0.getDialogueBySession(17))
    # print(f"测试样例2：", feedback1)

    # 查找某个特定客户的对话
    # test_0.getDialogueByCustomer('wmFS0DDgAAEJXr6ga3RFr-69yQxHiUIw')

    # # 统计每个客户的消息数量
    # test_0.customerMessageCount()
    # test_0.analyzeResponseTime()
    # test_0.analyzeResponseTime(17308401160)

    # 中文分词
    # tokenized = chinese_tokenization(test_0.getDialogueBySession(2))
    # print(tokenized)


function_test()
