# 测试代码
from DataUtils import Dialogue, chinese_tokenization, extract_service_messages
from basic_methods import Script_Matching, Keywords_Matching, Regex_Matching
import pandas as pd
import rule_manager as rm
from database_manager import init_db, add_rule, delete_rule, update_rule, query_rule

# 在程序开始时初始化数据库
if __name__ == "__main__":
    init_db()
# 加载数据
test_0 = Dialogue('CT_dialogue.csv')

# 手动定义service_replies DataFrame
data = {
    '客户ID': ['123', '123'],
    '客服ID': ['456', '456'],
    '消息内容': ['您可以先报名一下试听课，尝试一下', '孩子今年几岁了？'],
    '发送方': [0, 0],
    '发送时间': ['2023/8/20 16:05:00', '2023/8/21 16:05:00']
}

service_replies = extract_service_messages(pd.DataFrame(data))
print(service_replies)
test_message = extract_service_messages(test_0.getDialogueBySession(47))

# 话术检测
scripts = ["您好，我们现在有试听课，您方便参加吗", "您可以先听一下试听课，感受一下", "我帮您预约时间，您什么时间方便呢"]
scripts_result = Script_Matching(scripts, service_replies, 0.7)
print(f"话术检测结果：{scripts_result}")

# 关键词检测
keywords = ['您', '可以', '试听课', '报名', '孩子']
keyword_result = Keywords_Matching(service_replies, keywords, 'all')
print(f"关键词检测结果：{keyword_result}")

# 正则表达式检测
# Assume material_to_evaluate is a Pandas Series containing service replies
pattern = "(孩子|娃|姑娘).{0,4}(多大|几岁)|(孩子|娃|姑娘|上).{0,3}(几年级|初几|高几)|您.{0,3}做什么|什么工作|报过.{0,3}(其他|别的).{0,3}辅导班"
regex_result = Regex_Matching(pattern, service_replies)
print(f"正则表达式检测结果：{regex_result}")

# 规则匹配
test_rule = rm.Rule("客服幽默风趣")
test_rule.add_script_rule(scripts, 0.7)
test_rule.add_keyword_rule(keywords, 'all')
test_rule.add_regex_rule(pattern)
print(test_rule.evaluate(service_replies))

# 数据库操作
add_rule(test_rule)
delete_rule('script_rules', 1)  # 假设要删除 ID 为 1 的规则
update_rule('script_rules', 1, {'scripts': 'new script', 'similarity_threshold': 0.9})  # 更新 ID 为 1 的规则
all_script_rules = query_rules('script_rules')
print(all_script_rules)

# 查找某个特定客户的对话
# test_0.getDialogueByCustomer('wmFS0DDgAAEJXr6ga3RFr-69yQxHiUIw')
#
# # 获取特定对话ID的内容
# test_0.getDialogueBySession(2)
#
# # 统计每个客户的消息数量
# test_0.customerMessageCount()
# test_0.analyzeResponseTime()
# test_0.analyzeResponseTime(17308401160)
#
#
# tokenized = chinese_tokenization(test_0.getDialogueBySession(2))
# print(tokenized)
