#! python3
# -*- coding: utf-8 -*-
import re
from pyquery import PyQuery as Pq
from peewee import IntegrityError
from dateutil.parser import parse
from db.origin import Origin_Weibo
from db.basic import Basic_Weibo
from db.sort_basic import Sort_Basic_Weibo
from logger.log import crawler, parser, other, storage
"""
对已保存到数据库的文本进行处理
1.先进行非结构化到结构化处理，将一整页的html拆成一个个评论
"""


def process_raw_data():
    fetch_from_database = []
    for row in Origin_Weibo.select():
        current_page = row.current_page
        crawler.warning(current_page)
        raw_html = row.raw_html
        d = Pq(raw_html)
        repost_list = [{'current_page': current_page, 'mid_id': i.attr('mid'), 'repost_html': i.html()} for i in d('.list_li.S_line1.clearfix').items()]
        fetch_from_database.extend(repost_list)

    basic_parse_res = []  # 第一层的解析结果
    for i in fetch_from_database:
        current_page = i['current_page']
        crawler.warning(current_page)
        mid_id = i['mid_id']
        crawler.warning(mid_id)
        repost_html = i['repost_html']
        d = Pq(repost_html)
        repost_user_id = re.findall(r'\d+', d('.WB_face.W_fl a img').attr('usercard'))[0]  # 用户id
        crawler.warning(repost_user_id)
        repost_user = d('.WB_face.W_fl a img').attr('alt')  # 用户名
        crawler.warning(repost_user)
        repost_content = d('.WB_text span').text()  # 转发评论
        crawler.warning(repost_content)
        repost_time = d('.WB_from.S_txt2').text()  # 转发时间
        crawler.warning(repost_time)
        repost_num = 0
        upvote_num = 0
        repost_list = re.findall(r'\d+', d('.WB_func.clearfix .WB_handle.W_fr .clearfix li:eq(1) .line.S_line1 .S_txt1').text())  # 转发数
        if len(repost_list) != 0:
            repost_num = repost_list[0]
        upvote_list = re.findall(r'\d+', d('.WB_func.clearfix .WB_handle.W_fr .clearfix li:eq(2) .line.S_line1 a span em:eq(1)').text())  # 点赞数
        if len(upvote_list) != 0:
            upvote_num = upvote_list[0]
        crawler.warning(repost_num)
        crawler.warning(upvote_num)
        basic_parse_res.append({'current_page': current_page, 'mid_id': mid_id, 'repost_html': repost_html,
                                'repost_user_id': repost_user_id, 'repost_user': repost_user,
                                'repost_content': repost_content, 'repost_time': repost_time,
                                'repost_num': repost_num, 'upvote_num': upvote_num})
        # break
    return basic_parse_res


def save(basic_parse_res):
    for single_res in basic_parse_res:
        try:
            Basic_Weibo.create(id=int(single_res['mid_id']),
                               current_page=single_res['current_page'],
                               mid_id=int(single_res['mid_id']),
                               repost_html=single_res['repost_html'],
                               repost_user_id=int(single_res['repost_user_id']),
                               repost_user=single_res['repost_user'],
                               repost_content=single_res['repost_content'],
                               repost_time=single_res['repost_time'],
                               repost_num=int(single_res['repost_num']),
                               upvote_num=int(single_res['upvote_num']))
        except IntegrityError as err:
            crawler.warning(err)


def sort_basic_database():
    order_by_current_page = Basic_Weibo.select().order_by(Basic_Weibo.current_page.asc())
    # order_by_repost_time = order_by_current_page.order_by(parse(str(Basic_Weibo.repost_time), fuzzy=True).asc())
    order_by_repost_time = order_by_current_page.order_by(Basic_Weibo.repost_time.asc())
    for row in order_by_repost_time:
        print(row.id, row.current_page)
        Sort_Basic_Weibo.create(id=row.id,
                                current_page=row.current_page,
                                mid_id=row.mid_id,
                                repost_html=row.repost_html,
                                repost_user_id=row.repost_user_id,
                                repost_user=row.repost_user,
                                repost_content=row.repost_content,
                                repost_time=row.repost_time,
                                repost_num=row.repost_num,
                                upvote_num=row.upvote_num)


def basic_combine():
    basic_parse_res = process_raw_data()
    save(basic_parse_res)
    # sort_basic_database()


if __name__ == '__main__':
    basic_combine()


# __all__ = ['basic_combine']
