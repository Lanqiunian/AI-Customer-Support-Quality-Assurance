"""
自定义异常类
"""


class RuleNameExistsException(Exception):
    """当试图添加一个已存在的规则名称时抛出此异常。"""

    def __init__(self, rule_name):
        self.message = f"规则 '{rule_name}' 已存在。"
        super().__init__(self.message)
