# Description: 全局配置文件
AI_PROMPT_RULES = """请根据以下需求，生成一组json格式的规则。需求："""
AI_PROMPT_RULES_JSON_EXAMPLE = """
。你禁止返回任何除了json之外的内容，也不要有任何注释，一个返回格式的例子如下，：
 {
    "rule_name": "例子",
    "score_type": 1,
    "score_value": 5,
    "script_rules": [
        {
            "scripts": [
                "笑了",
                "可以尝试一下哦"
            ],
            "similarity_threshold": 0.8,
            "condition_id": "1"
        }
    ],
    "keyword_rules": [
        {
            "keywords": [
                "请",
                "谢谢",
                "不客气"
            ],
            "check_type": "any",
            "condition_id": "2",
            "n": null
        }
    ],
    "regex_rules": [
        {
            "pattern": "(怎么|如何|什么时候|哪里|谁).*",
            "condition_id": "3"
        }
    ]
}

    
"""
