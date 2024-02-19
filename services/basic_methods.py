import difflib
import re

import jieba


def string_similar(s1, s2):
    """
    对比话术相似度

    :param s1: 第一个字符串
    :param s2: 第二个字符串
    :return: 二者相似度
    """
    formatted_similarity = f"{difflib.SequenceMatcher(None, s1, s2).quick_ratio() * 100:.1f}%"
    return formatted_similarity


def Script_Matching(scripts, service_replies, similarity_threshold):
    """
    在客服回复中找到与指定话术最匹配的回复。

    :param scripts: list，包含若干句话术。
    :param service_replies: Pandas Series，包含客服的回复。
    :param similarity_threshold: float, 相似度阈值，只有当相似度超过此值时才认为是有效匹配。
    :return: 最佳匹配的话术和客服回复及其相似度。如果没有达到阈值，则返回相应提示。
    """
    best_match = ""
    best_script = ""
    highest_similarity = 0

    for reply in service_replies:
        for script in scripts:
            similarity = difflib.SequenceMatcher(None, script, reply).quick_ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = reply
                best_script = script

    if highest_similarity >= similarity_threshold:
        print(f"回复：“{best_script}”匹配了：“{best_match}”，相似度为：“{highest_similarity * 100:.1f}%“")
        return True
        # return best_script, best_match, f"{highest_similarity * 100:.1f}%"
    else:
        return False


def Keywords_Matching(service_replies, keywords, check_type, n=None):
    """
    进行给关键词检测

    :param service_replies: Pandas Series类型，存回复
    :param keywords: List，存关键词
    :param check_type:'any存在其一', 'all全部存在', 'any_n存在n个', 'none全部不存在'
    :param n:’any_n‘模式下的n
    :return:布尔值，是否满足关键词命中条件
    """
    if check_type not in ['any', 'all', 'any_n', 'none']:
        raise ValueError("无效的检测类型. 检测类型有'any', 'all', 'any_n', or 'none'.")

    # 对每个关键词使用jieba.add_word以防止被错误分词
    for keyword in keywords:
        jieba.add_word(keyword)
    for message in service_replies:  # 直接处理Series中的每个元素
        message_words = set(jieba.cut(message))
        print(f"分词结果", message_words)
        # print(message_words) 如果第一句话就满足了关键词匹配，那么就不会验证第二句话
        if check_type == 'any' and any(keyword in message_words for keyword in keywords):
            return True
        elif check_type == 'all' and all(keyword in message_words for keyword in keywords):
            return True
        elif check_type == 'any_n' and sum(keyword in message_words for keyword in keywords) >= n:
            return True
        elif check_type == 'none' and all(keyword not in message_words for keyword in keywords):
            return True

    return False


def Regex_Matching(pattern, service_replies):
    """
    检查是否有任何一条客服回复匹配给定的正则表达式。

    :param pattern: str，正则表达式。
    :param service_replies: Pandas Series，包含客服的回复。
    :return: bool，表示是否有匹配的回复。
    """
    regex = re.compile(pattern)

    for reply in service_replies:
        if regex.search(reply):
            return True
    return False
