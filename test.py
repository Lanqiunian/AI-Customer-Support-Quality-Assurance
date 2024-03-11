import pandas as pd

from services.db.db_rule import query_rule, add_rule
from services.db.db_scheme import update_score_by_HitRulesList
from services.rule_manager import Rule
from utils.data_utils import Dialogue, extract_service_messages
from utils.global_utils import DIALOGUE_DATA_PATH


def function_test():
    data = {
        '客户ID': ['123', '123', '123', '123', '123'],
        '客服ID': ['456', '456', '456', '456', '456'],
        '消息内容': ['傻逼东西', '废物玩意儿', '幽默风趣', '俊朗帅气', '优秀'],
        '发送方': [0, 0, 0, 0, 0],
        '发送时间': ['2023/8/20 16:05:00', '2023/8/21 16:05:00', '2023/8/22 16:05:00', '2023/8/23 16:05:00',
                     '2023/8/24 16:05:00']
    }
    df = pd.DataFrame(data)
    rule_instance = Rule(
        rule_name="Customer Service Quality",
        score_type=1,
        score_value=5,
        logic_expression="1 and not 2 or 3",
        script_rules=[
            {
                'scripts': ["你好，请问有什么可以帮到您的？", "很高兴为您服务，请问您需要什么帮助？"],
                'similarity_threshold': 0.8,
                'target_role': 0,  # 代表这条规则是针对客服的发言
                'condition_id': "script1"
            }
        ],
        keyword_rules=[
            {
                'keywords': ["不满意", "差评"],
                'check_type': 'any',
                'n': None,
                'target_role': 1,  # 代表这条规则是针对客户的发言
                'condition_id': "keyword1"
            }
        ],
        regex_rules=[
            {
                'pattern': r"退款|退货",
                'target_role': 1,  # 代表这条规则是针对客户的发言
                'condition_id': "regex1"
            }
        ]
    )
    add_rule(rule_instance)

    # # 更新规则以包括更多条件
    # rule = Rule(
    #     rule_name="Test Rule",
    #     score_type=1,
    #     score_value=5,
    #     keyword_rules=[
    #         {'keywords': ['傻逼', '废物'], 'check_type': 'any', 'condition_id': '客服说脏话'},
    #         {'keywords': ['优秀'], 'check_type': 'any', 'condition_id': '客服说好话'},
    #
    #
    #     ],
    #     regex_rules=[
    #         {'pattern': r'幽默|帅气', 'condition_id': '客服吹嘘'}
    #     ]
    # )
    #
    # # 定义不同的逻辑表达式进行测试
    # expressions = [
    #     "客服说脏话 and 客服说好话",
    #     "客服说脏话 or 客服吹嘘",
    #     "not 客服说好话 and (客服说脏话 or 客服吹嘘)",
    #     "客服说脏话 and not 客服说好话"
    # ]
    #
    # # 对每个逻辑表达式进行评估
    # for expr in expressions:
    #     rule.logic_expression = expr
    #     extracted_messages = extract_service_messages(df)
    #     print(f"逻辑表达式: {expr}, 评估结果: {rule.evaluate(extracted_messages)}")
    #
    # test_rule = query_rule("ExampleRule1")
    # print(f"关键词规则为：", test_rule.keyword_rules)
    # print(f"话术规则为", test_rule.script_rules)
    # print(f"正则表达式", test_rule.regex_rules)

    # df = load_data_from_db("电信客服")
    # print(load_data_from_db("电信客服"))
    # print(count_unique_dialogues(load_data_from_db("电信客服")))

    service_replies = extract_service_messages(pd.DataFrame(data))

    # print(service_replies)
    # # 话术检测

    # scripts_1 = ["您好，我们现在有试听课，您方便参加吗", "您可以先听一下试听课，感受一下",
    #              "我帮您预约时间，您什么时间方便呢"]
    # scripts_2 = ["您好，我爱你", "我喜欢你"]
    # # scripts_result = Script_Matching(scripts, service_replies, 0.7)
    # # print(f"话术检测结果：{scripts_result}")
    # # # 关键词检测
    # keywords_1 = ['傻逼', '废物']
    # keywords_2 = ['畜生', '傻狗', '幽默']
    #
    # test_rule = Rule("测试规则0")
    # test_rule.add_keyword_rule(keywords_1, 'any', 1)
    # test_rule.add_keyword_rule(keywords_2, 'any', 2)
    # test_rule.add_script_rule(scripts_1, 0.7, 1)
    # test_rule.add_script_rule(scripts_2, 0.7, 2)
    # print(test_rule.keyword_rules)
    # print(test_rule.script_rules)
    # # add_rule(test_rule)
    # queried_rule = query_rule("测试规则0")
    # keywords = queried_rule.keyword_rules
    # print(f"get方法", get_keyword_by_name("幽默", 1))
    # for keyword in keywords:
    #     print(keyword['keywords'])
    # print(get_dialogue_count_by_task_id(16))
    # print(get_average_score_by_task_id(16))
    # print(get_hit_times_by_task_id(16))
    # print(get_score_info_by_name("客服骂人"))
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
