"""
定义规则类，用于组合各种检测方式，并且给出检测结果
"""
import pandas as pd

from services.basic_methods import Keywords_Matching, Regex_Matching, Script_Matching


class Rule:
    def __init__(self, rule_name, score_type=1, score_value=0, script_rules=None, keyword_rules=None,
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

    def change_score_setting(self, score_type, score_value):
        """
        更改评分设置
        :param score_type: 评分类型,0为一次性得分，1为加减分
        :param score_value: 评分值，正负整数
        """
        self.score_type = score_type
        self.score_value = score_value

    def add_script_rule(self, scripts, similarity_threshold):
        """
        添加一条话术匹配

        :param scripts: 话术列表
        :param similarity_threshold: 判决阈限，达到则代表匹配上了
        """
        self.script_rules.append({
            'scripts': scripts,
            'similarity_threshold': similarity_threshold
        })

    def add_keyword_rule(self, keywords, check_type, n=None):
        """
        添加一个关键词检测.

        :param keywords: 用于匹配的关键词列表.
        :param check_type: 检测类型: 'any', 'all', 'any_n', or 'none'.具体看定义
        :param n: 当检测类型是 'any_n'时的n
        """
        self.keyword_rules.append({
            'keywords': keywords,
            'check_type': check_type,
            'n': n
        })

    def add_regex_rule(self, pattern):
        """
        添加一个正则表达式检测.

        :param pattern: 正则表达式.
        """
        self.regex_rules.append({
            'pattern': pattern
        })

    def evaluate(self, material_to_evaluate):
        """
        评估全部的规则，全部命中，则返回True，否则返回False

        :param material_to_evaluate: Panda Series类型 待评估的语料.
        :return: 评估结果的布尔值.
        """
        material_to_evaluate_series = pd.Series(material_to_evaluate)

        # 查话术
        for rule in self.script_rules:
            scripts = rule['scripts']
            threshold = rule['similarity_threshold']
            if not scripts:
                continue

            matched = any(Script_Matching(scripts, material_to_evaluate_series, threshold) for reply in material_to_evaluate)
            if not matched:
                print("话术匹配中断")
                return False

        # 查关键词
        for rule in self.keyword_rules:
            keywords = rule['keywords']
            check_type = rule['check_type']
            n = rule.get('n')
            if not keywords:
                continue
            matched = Keywords_Matching(material_to_evaluate_series, keywords, check_type, n)
            if not matched:
                print("关键词匹配中断")
                return False

        # 查正则表达式
        for rule in self.regex_rules:
            pattern = rule['pattern']
            if not pattern:
                continue
            matched = Regex_Matching(pattern, material_to_evaluate_series)
            if not matched:
                print("正则表达式匹配中断")
                return False

        return self.score_type, self.score_value
        # 返回一个元组，记得可以这么访问
        # result = get_score_by_name("Rule1")
        # if result:
        #     score_type, score_value = result
        #     print(f"Score Type: {score_type}, Score Value: {score_value}")
        # else:
        #     print("No matching record found.")
