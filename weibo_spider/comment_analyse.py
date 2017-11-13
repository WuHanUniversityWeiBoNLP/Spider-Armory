#! python3
# -*- coding: utf-8 -*-
import os
import jieba
import json
from db.comment import Comment
from collections import Counter
from logger.log import crawler, parser, other, storage
from decorators.decorator import save_decorator


@save_decorator('list')
def test1(input_value):
    return input_value


@save_decorator('not a list')
def test2(input_value):
    return input_value


"""
词频分析。对所有评论中出现的词频进行分析，
即在讨论婚姻观中，出现的词频最多的词有哪些，
相关的词和词组有哪些？找出频率最高的。并制表。
"""


def cut_raw_word():
    token = []
    for row in Comment.select():
        comment_content = row.comment_content
        clean_comment_content = comment_content.strip()
        other.info(clean_comment_content)
        if len(clean_comment_content) > 0:
            seg_list = jieba.cut(comment_content, cut_all=False)   # 精确模式
            for word in seg_list:
                other.info(word)
                token.append(word)
        # break
    return token


def count_raw_word(token):
    counter = Counter(token)
    for item in counter.most_common(5):
        print(item[0] + '\t' + str(item[1]))


def filter_useless_word(token):
    non_empty = [i for i in token if i != ' ']
    base_path = os.path.abspath(os.path.dirname(__file__))
    stop_word_path = os.path.join(base_path, 'stop_words')
    stop_word_file = os.listdir(stop_word_path)
    stop_word_abs_file = []
    for file in stop_word_file:
        stop_word_abs_file.append(os.path.join(stop_word_path, file))
    stop_word = []
    for file in stop_word_abs_file:
        with open(file, 'r', encoding='utf8') as f:
            line = f.read()
            for word in line:
                if word != '\n':
                    stop_word.append(word)
    """
    增加微博独特停用词，回复
    """
    stop_word.append('回复')
    non_empty_and_non_stop_word = []
    for word in non_empty:
        if word not in stop_word:
            non_empty_and_non_stop_word.append(word)
    return non_empty_and_non_stop_word


def count(non_empty_and_non_stop_word):
    counter = Counter(non_empty_and_non_stop_word)
    result = {}
    for item in counter.most_common(10):
        result.setdefault(item[0], item[1])
    return result


def main():
    token = cut_raw_word()
    # count_raw_word(token)
    non_empty_and_non_stop_word = filter_useless_word(token)
    result = count(non_empty_and_non_stop_word)
    with open('machine_learning_res/comment_freq.json', 'wt') as f:
        f.write(json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    main()