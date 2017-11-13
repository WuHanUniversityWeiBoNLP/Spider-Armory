#! python3
# -*- coding: utf-8 -*-
import re
import json
import time
import requests
from headers import headers
from fnvhash import fnv1a_32
from pyquery import PyQuery as Pq
from peewee import IntegrityError
from random import randint, uniform
from db.comment import Comment
from logger.log import crawler, parser, other, storage


with open('cookie.json', 'r') as f:
    cookie = json.loads(f.read())
s = requests.Session()

base_url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&root_comment_max_id={}&page={}&__rnd={}'

mid = '4151542729073845'
max_mid = '4154068584896369'
cur_time = int(time.time() * 1000)


class CommentParser(object):
    @staticmethod
    def parse_page_one():
        """
        获取评论第一页的内容，返回第一页的内容，还有总的页数
        :return:
        """
        start_url = base_url.format(mid, max_mid, 1, cur_time)
        response = s.get(start_url, headers=headers, verify=False, cookies=cookie)
        crawler.warning(response.content)
        parse_able_data = json.loads(response.content)
        total_page = parse_able_data['data']['page']['totalpage']
        crawler.warning(total_page)
        current_page_num = parse_able_data['data']['page']['pagenum']
        crawler.warning(current_page_num)
        page_one_raw_html = parse_able_data['data']['html']
        return total_page, current_page_num, page_one_raw_html

    @staticmethod
    def parse_page_rest(total_page):
        generate_url = []
        int_total_page = int(total_page)
        for i in range(2, int_total_page + 1):
            generate_url.append(base_url.format(mid, max_mid, i, cur_time))
            # break
        rest_res = []
        for i in generate_url:
            response = s.get(i, headers=headers, verify=False, cookies=cookie)
            time.sleep(uniform(60, 80))
            crawler.warning(i)
            parse_able_data = json.loads(response.content)
            current_page = parse_able_data['data']['page']['pagenum']
            crawler.warning(current_page)
            raw_html = parse_able_data['data']['html']
            rest_res.append({'current_page': current_page, 'raw_html': raw_html})
            # break
        return rest_res

    @staticmethod
    def merge(page_one_raw_html, rest_res):
        total_raw_res = []
        total_raw_res.insert(0, {'current_page': '1', 'raw_html': page_one_raw_html})
        total_raw_res.extend(rest_res)
        return total_raw_res

    @staticmethod
    def parse_all(total_raw_res):
        for item in total_raw_res:
            current_page = item['current_page']
            crawler.warning(current_page)
            raw_html = item['raw_html']
            d = Pq(raw_html)
            block = d('.list_ul .list_li.S_line1.clearfix')
            for elem in block.items():
                comment_id = elem('.list_li.S_line1.clearfix').attr('comment_id')  # ok
                crawler.warning(comment_id)
                user_id = elem('.WB_text a').attr('href').replace('/', '')  # ok
                crawler.warning(user_id)
                comment_content = elem('.WB_text').text()  # ok
                crawler.warning(comment_content)
                comment_time = elem('.WB_from.S_txt2').text()  # ok
                crawler.warning(comment_time)
                up_vote_num = elem('.S_txt1 em:eq(1)').text().replace('赞', '0')  # ok
                crawler.warning(up_vote_num)
                result = {'id': comment_id, 'current_page': current_page, 'raw_html': raw_html,
                          'comment_id': comment_id, 'user_id': user_id, 'comment_content': comment_content,
                          'comment_time': comment_time, 'up_vote_num': up_vote_num}
                try:
                    Comment.create(**result)
                except IntegrityError as err:
                    crawler.warning(err)
            # break

    @staticmethod
    def main():
        total_page, current_page_num, page_one_raw_html = CommentParser.parse_page_one()
        rest_res = CommentParser.parse_page_rest(total_page)
        total_raw_res = CommentParser.merge(page_one_raw_html, rest_res)
        CommentParser.parse_all(total_raw_res)


if __name__ == '__main__':
    CommentParser.main()

