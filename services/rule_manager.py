"""
定义规则类，用于组合各种检测方式，并且给出检测结果
"""
import pandas as pd

from services.basic_methods import Keywords_Matching, Regex_Matching, Script_Matching
from utils.data_utils import extract_customer_messages, extract_service_messages


class Rule:
    def __init__(self, rule_name, score_type=1, score_value=0, logic_expression=None, script_rules=None,
                 keyword_rules=None,
                 regex_rules=None):
        """
        使用可选的脚本匹配规则、关键词匹配规则和正则表达式匹配规则初始化 Rule 类。每种规则类型预期是一个字典列表，
        其中包含每种方法所需的参数。

        :param script_rules: 字典列表，每个字典包含脚本匹配的参数。
        :param keyword_rules: 字典列表，每个字典包含关键词匹配的参数。
        :param regex_rules: 字典列表，每个字典包含正则表达式匹配的参数。
        :param score_type: 评分类型,0为一次性得分，1为加减分
        :param score_value: 评分值，正负整数
        评分规则默认为扣0分
        """
        # 规则们以字典的形式储存
        self.rule_name = rule_name
        self.script_rules = script_rules if script_rules is not None else []
        self.keyword_rules = keyword_rules if keyword_rules is not None else []
        self.regex_rules = regex_rules if regex_rules is not None else []

        self.score_type = score_type
        self.score_value = score_value
        self.logic_expression = logic_expression

    def add_logic_expression(self, logic_expression):
        self.logic_expression = logic_expression

    def change_score_setting(self, score_type, score_value):
        """
        更改评分设置
        :param score_type: 评分类型,0为一次性得分，1为加减分
        :param score_value: 评分值，正负整数
        """
        self.score_type = score_type
        self.score_value = score_value

    def add_script_rule(self, scripts, similarity_threshold, target_role=0, condition_id=None):
        """
        添加一条话术匹配

        :param condition_id:
        :param scripts: 话术列表
        :param target_role:  0代表客服，1代表客户
        :param similarity_threshold: 判决阈限，达到则代表匹配上了
        """
        self.script_rules.append({
            'scripts': scripts,
            'similarity_threshold': similarity_threshold,
            'target_role': target_role,  # 0代表客服，1代表客户
            'condition_id': condition_id
        })

    def add_keyword_rule(self, keywords, check_type, target_role=0, condition_id=None, n=None):
        """
        添加一个关键词检测.

        :param condition_id:
        :param keywords: 用于匹配的关键词列表.
        :param check_type: 检测类型: 'any', 'all', 'any_n', or 'none'.具体看定义
        :param target_role: 0代表客服，1代表客户
        :param n: 当检测类型是 'any_n'时的n
        """
        self.keyword_rules.append({
            'keywords': keywords,
            'check_type': check_type,
            'n': n,
            'target_role': target_role,  # 0代表客户，1代表客服
            'condition_id': condition_id
        })

    def add_regex_rule(self, pattern, target_role=0, condition_id=None):
        """
        添加一个正则表达式检测.

        :param condition_id:
        :param target_role: 0代表客服，1代表客户
        :param pattern: 正则表达式.
        """
        self.regex_rules.append({
            'pattern': pattern,
            'target_role': target_role,  # 0代表客户，1代表客服
            'condition_id': condition_id
        })

    def evaluate(self, material_to_evaluate):
        print(f"material_to_evaluate: {material_to_evaluate}")
        customer_material_to_evaluate = extract_customer_messages(material_to_evaluate)
        service_material_to_evaluate = extract_service_messages(material_to_evaluate)
        print(f"customer_material_to_evaluate: {customer_material_to_evaluate}")
        print(f"service_material_to_evaluate: {service_material_to_evaluate}")
        customer_material_to_evaluate_series = pd.Series(customer_material_to_evaluate)
        service_material_to_evaluate_series = pd.Series(service_material_to_evaluate)
        condition_results = {}  # 存储每个条件的匹配结果

        # 对每种规则类型进行评估，并存储结果
        for rule in (self.script_rules + self.keyword_rules + self.regex_rules):
            print(f"11")
            if 'condition_id' not in rule or rule['condition_id'] is None:
                continue
            print(f"2222")
            condition_id = rule['condition_id']
            if rule in self.script_rules:
                material_to_evaluate_series = service_material_to_evaluate_series if rule[
                                                                                         'target_role'] == 0 else customer_material_to_evaluate_series

                matched = any(
                    Script_Matching(rule['scripts'], material_to_evaluate_series, rule['similarity_threshold']) for
                    reply in material_to_evaluate)
                try:
                    print(
                        f"进行话术检测，检测的内容是{material_to_evaluate_series}，检测的结果是{matched}，检测的条件是{rule['scripts']}，检测的角色是{rule['target_role']}")
                except Exception as e:
                    print(f"输出检测过程1", e)
            elif rule in self.keyword_rules:
                material_to_evaluate_series = service_material_to_evaluate_series if rule[
                                                                                         'target_role'] == 0 else customer_material_to_evaluate_series
                matched = Keywords_Matching(material_to_evaluate_series, rule['keywords'], rule['check_type'],
                                            rule.get('n'))
                try:
                    print(
                        f"进行关键词检测，检测的内容是{material_to_evaluate_series}，检测的结果是{matched}，检测的条件是{rule['keywords']}，检测的角色是{rule['target_role']}")
                except Exception as e:
                    print(f"输出检测过程2", e)
            elif rule in self.regex_rules:
                material_to_evaluate_series = service_material_to_evaluate_series if rule[
                                                                                         'target_role'] == 0 else customer_material_to_evaluate_series
                matched = Regex_Matching(rule['pattern'], material_to_evaluate_series)
                try:
                    print(
                        f"进行正则表达式检测，检测的内容是{material_to_evaluate_series}，检测的结果是{matched}，检测的条件是{rule['pattern']}，检测的角色是{rule['target_role']}")
                except Exception as e:
                    print(f"输出检测过程3", e)
            condition_results[condition_id] = matched

        if self.logic_expression:
            # 将逻辑表达式中的条件标识符替换为它们的布尔值
            logic_expr_evaluable = self.logic_expression
            for condition_id, result in condition_results.items():
                # 将条件标识符替换为它的布尔值（True/False）
                logic_expr_evaluable = logic_expr_evaluable.replace(str(condition_id), str(result))

            try:
                print(f"原始逻辑表达式: {self.logic_expression}")
                print(f"条件结果: ", condition_results)
                print(f"评估前逻辑表达式: {logic_expr_evaluable}")
                # 直接使用eval计算布尔表达式
                match_result = eval(logic_expr_evaluable)
                print(f"逻辑表达式计算结果: {match_result}")
            except Exception as e:
                print(f"逻辑表达式计算错误: {e}")
                return False
        else:
            # 如果没有定义逻辑表达式，则默认所有条件都必须匹配
            match_result = all(condition_results.values())

        if match_result:
            print(f"匹配成功，得分类型: {self.score_type}，得分值: {self.score_value}")
            return self.score_type, self.score_value
        else:
            print("匹配失败")
            return False
