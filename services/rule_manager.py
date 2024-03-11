"""
定义规则类，用于组合各种检测方式，并且给出检测结果
"""
import pandas as pd

from services.basic_methods import Keywords_Matching, Regex_Matching, Script_Matching


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

    def add_script_rule(self, scripts, similarity_threshold, condition_id=None):
        """
        添加一条话术匹配

        :param condition_id:
        :param scripts: 话术列表
        :param similarity_threshold: 判决阈限，达到则代表匹配上了
        """
        self.script_rules.append({
            'scripts': scripts,
            'similarity_threshold': similarity_threshold,
            'condition_id': condition_id
        })

    def add_keyword_rule(self, keywords, check_type, condition_id=None, n=None):
        """
        添加一个关键词检测.

        :param condition_id:
        :param keywords: 用于匹配的关键词列表.
        :param check_type: 检测类型: 'any', 'all', 'any_n', or 'none'.具体看定义
        :param n: 当检测类型是 'any_n'时的n
        """
        self.keyword_rules.append({
            'keywords': keywords,
            'check_type': check_type,
            'n': n,
            'condition_id': condition_id
        })

    def add_regex_rule(self, pattern, condition_id=None):
        """
        添加一个正则表达式检测.

        :param condition_id:
        :param pattern: 正则表达式.
        """
        self.regex_rules.append({
            'pattern': pattern,
            'condition_id': condition_id
        })

    def evaluate(self, material_to_evaluate):
        material_to_evaluate_series = pd.Series(material_to_evaluate)
        condition_results = {}  # 存储每个条件的匹配结果

        # 对每种规则类型进行评估，并存储结果
        for rule in (self.script_rules + self.keyword_rules + self.regex_rules):
            if 'condition_id' not in rule or rule['condition_id'] is None:
                continue
            condition_id = rule['condition_id']
            if rule in self.script_rules:
                matched = any(
                    Script_Matching(rule['scripts'], material_to_evaluate_series, rule['similarity_threshold']) for
                    reply in material_to_evaluate)
            elif rule in self.keyword_rules:
                matched = Keywords_Matching(material_to_evaluate_series, rule['keywords'], rule['check_type'],
                                            rule.get('n'))
            elif rule in self.regex_rules:
                matched = Regex_Matching(rule['pattern'], material_to_evaluate_series)
            condition_results[condition_id] = matched

        # 计算逻辑表达式
        try:
            if self.logic_expression:
                match_result = eval(self.logic_expression, {}, condition_results)
            else:
                # 如果没有定义逻辑表达式，则默认所有条件都必须匹配
                match_result = all(condition_results.values())
        except Exception as e:
            print(f"逻辑表达式计算错误: {e}")
            return False
        if match_result:
            return self.score_type, self.score_value
        else:
            return False
