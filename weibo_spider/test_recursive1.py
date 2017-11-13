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
from db.basic import Basic_Weibo
from db.complete import Complete_Weibo
from db.test_recursive1 import Test_Recursive_Ancestor, Test_Recursive_Descendant
from logger.log import crawler, parser, other, storage
"""
开始根据是否有转发数来进行递归抓取
思路:
1.先从之前的表中将数据分为有转发/没转发两类，然后加入有转发路径的表中
2.如果原先转发数为零，那么直接将path置空就行，就写默认值为1或者直接写mid
3.如果原先转发数不为零，先将path写成mid/的形式，然后请求url,获取页面内容，存数据库，将后续节点的路径改为mid/mid/
以此类推
"""
with open('cookie.json', 'r') as f:
    cookie = json.loads(f.read())
s = requests.Session()


def shift():
    """
    将数据转移到有外键的表中
    :return:
    """
    for row in Basic_Weibo.select():
        Test_Recursive_Ancestor.create(
            id=row.id,
            current_page=row.current_page,
            mid_id=row.mid_id,
            repost_html=row.repost_html,
            repost_user_id=row.repost_user_id,
            repost_user=row.repost_user,
            repost_content=row.repost_content,
            repost_time=row.repost_time,
            repost_num=row.repost_num,
            upvote_num=row.upvote_num,
            is_crawl=False
        )


def recursive():
    more_than_zero = Test_Recursive_Ancestor.select().where(Test_Recursive_Ancestor.repost_num > 0,
                                                            Test_Recursive_Ancestor.is_crawl == False)
    crawler.warning('----------------------------------------------------------')
    crawler.warning(more_than_zero.count())
    crawler.warning('----------------------------------------------------------')
    while more_than_zero:
        for row in more_than_zero:
            origin_mid = row.mid_id
            crawler.warning(origin_mid)
            crawler.warning('@@@@@@@')
            crawler.warning(row.repost_num)
            crawler.warning('@@@@@@@')
            rnd = int(time.time() * 1000)
            repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
            response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
            time.sleep(2)
            """
            发过请求之后，立刻修改数据库状态
            """
            # query = Test_Recursive_Ancestor.update(is_crawl=True).where(Test_Recursive_Ancestor.id == row.id)
            # query.execute()
            total_json_data = resp_to_text(origin_mid, response)
            total_repost_data = split_the_text(origin_mid, total_json_data)
            save(total_repost_data)
            break
            # return recursive()


def resp_to_text(origin_mid, response):
    """
    拆解数据库中原有评论有转发的下一层文本
    :param origin_mid:
    :param response:
    :return:
    """
    crawler.warning("resp_to_test function")
    crawler.warning(origin_mid)
    crawler.warning(response.content)
    crawler.warning("resp_to_test function")
    total_json_data = []
    meta_json_data = json.loads(response.content)
    total_json_data.append(meta_json_data)  # 第一页
    total_page = meta_json_data['data']['page']['totalpage']
    int_total_page = int(total_page)
    crawler.warning(int_total_page)
    if int_total_page != 1:
        for page_num in range(2, int_total_page+1):
            crawler.warning(page_num)
            rest_repost_url = 'http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&page={}'.format(origin_mid, page_num)
            rest_resp = s.get(rest_repost_url, headers=headers, verify=False, cookies=cookie)
            time.sleep(2)
            rest_resp_content = json.loads(rest_resp.content)
            total_json_data.append(rest_resp_content)  # 其它页
            # break
    return total_json_data


def split_the_text(origin_mid, total_json_data):
    """
    将下一层的文本拆分成一个个评论字典
    :param origin_mid:
    :param total_json_data:
    :return:
    """
    crawler.warning("split_the_text function")
    total_repost_data = []
    for item in total_json_data:
        item_data_html = item['data']['html']
        current_page = item['data']['page']['pagenum']
        crawler.warning(current_page)
        d = Pq(item_data_html)
        block = d('.list_li.S_line1.clearfix')
        for elem in block.items():
            # print(elem.html())
            elem_outer_html = elem.outer_html()
            elem_outer_d = Pq(elem_outer_html)
            mid_id = elem_outer_d('.list_li.S_line1.clearfix').attr('mid')
            crawler.warning(mid_id)
            user_id = re.findall(r'\d+', elem('.WB_face.W_fl a img').attr('usercard'))[0]  # 用户id
            # print(user_id)
            user = elem('.WB_text a:eq(0)').text()  # 用户
            # print(user)
            repost_content = elem('.WB_text span').text()  # 转发评论
            repost_time = elem('.WB_from.S_txt2').text()  # 转发时间
            repost_num = 0  # 转发数
            upvote_num = 0  # 点赞数
            repost_list = re.findall(r'\d+', elem(
                '.WB_func.clearfix .WB_handle.W_fr .clearfix li:eq(1) .line.S_line1 .S_txt1').text())  # 转发数
            if len(repost_list) != 0:
                repost_num = repost_list[0]
            upvote_list = re.findall(r'\d+', elem(
                '.WB_func.clearfix .WB_handle.W_fr .clearfix li:eq(2) .line.S_line1 a span em:eq(1)').text())  # 点赞数
            if len(upvote_list) != 0:
                upvote_num = upvote_list[0]
            crawler.warning(str(origin_mid) + '->' + mid_id + '->')
            total_repost_data.append({'origin_mid': str(origin_mid), 'current_page': current_page, 'mid_id': mid_id,
                                      'repost_html': elem.html(), 'repost_user_id': user_id, 'repost_user': user,
                                      'repost_content': repost_content, 'repost_time': repost_time,
                                      'repost_num': repost_num, 'upvote_num': upvote_num,
                                      'repost_path': str(origin_mid) + '->' + mid_id, 'is_crawl': False})
        #     break
        # break
    return total_repost_data


def save(total_repost_data):
    for item in total_repost_data:
        try:
            crawler.warning('saving %s' % item['id'])
            # Test_Recursive_Descendant.create(**item)
            # Test_Recursive_Descendant.create(
            #     id=
            # )
            prime_key = fnv1a_32(''.join(item['repost_path'].split('->')))
            print(prime_key)
            print(item)
            repost_path = item['repost_path']
            print(repost_path.split('->'))
        except IntegrityError as err:
            """
            可能存在本层与下一级的mid是一样的情况，这时为了展现树的层次关系，应该修改主键
            """
            crawler.warning(err)
            # query = Test_Recursive.update(repost_path=item['repost_path']).where(Test_Recursive.id == item['id'])
            # query.execute()
            # crawler.warning('********')
            # crawler.warning(item['repost_num'])
            # crawler.warning('********')


def combine():
    # shift()
    recursive()


if __name__ == '__main__':
    combine()

"""
4152039828718852/4152043821902354/4152047614153047/4152052344671841/4152052693588418/


我觉得应该叫鄙婚鄙孕好不好 // @TSUYAYA : 肯定有啊 几亿美元的彩票也有人中啊// @ShojoS_HT沼 :不说信不信的问题，代表我自己表示，因为讨厌小孩子，对我来说的理想爱情和婚姻必须建立在男方全家都不想要下一代的基础上 参考国情，你们懂的
"""