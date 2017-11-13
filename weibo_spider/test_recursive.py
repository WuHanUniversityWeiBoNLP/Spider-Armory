#! python3
# -*- coding: utf-8 -*-
import re
import json
import time
import requests
from headers import headers
from pyquery import PyQuery as Pq
from peewee import IntegrityError
from db.basic import Basic_Weibo
from db.complete import Complete_Weibo
from db.test_recursive import Test_Recursive
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


def pre_process():
    """
    先将之前的没有深度路径的表转存到有深度的另一张表中
    :return:
    """
    for row in Basic_Weibo.select():
        if row.repost_num != 0:
            Complete_Weibo.create(
                id=row.mid_id,
                current_page=row.current_page,
                mid_id=row.mid_id,
                repost_html=row.repost_html,
                repost_user_id=row.repost_user_id,
                repost_user=row.repost_user,
                repost_content=row.repost_content,
                repost_time=row.repost_time,
                repost_num=row.repost_num,
                upvote_num=row.upvote_num,
                repost_path=str(row.mid_id),  # 方案一：先用mid->mid->的形式
                is_crawled=False
            )
        else:
            """
            没有转发数的部分
            """
            Complete_Weibo.create(
                id=row.mid_id,
                current_page=row.current_page,
                mid_id=row.mid_id,
                repost_html=row.repost_html,
                repost_user_id=row.repost_user_id,
                repost_user=row.repost_user,
                repost_content=row.repost_content,
                repost_time=row.repost_time,
                repost_num=row.repost_num,
                upvote_num=row.upvote_num,
                repost_path='0',  # 代表没有下一层了
                is_crawled=False
            )


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


def split_the_text(origin_repost_path, total_json_data):
    """
    将下一层的文本拆分成一个个评论字典
    :param origin_repost_path:
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
            crawler.warning(origin_repost_path + mid_id + '/')
            total_repost_data.append({'id': mid_id, 'current_page': current_page, 'mid_id': mid_id,
                                      'repost_html': elem.html(), 'repost_user_id': user_id, 'repost_user': user,
                                      'repost_content': repost_content, 'repost_time': repost_time,
                                      'repost_num': repost_num, 'upvote_num': upvote_num,
                                      'repost_path': origin_repost_path + mid_id + '/', 'is_crawled': False})
        #     break
        # break
    return total_repost_data


def save_repost_data(total_repost_data):
    for item in total_repost_data:
        try:
            crawler.warning('saving %s' % item['id'])
            Complete_Weibo.create(**item)
        except IntegrityError as err:
            """
            可能存在本层与下一级的mid是一样的情况，这时为了展现树的层次关系，应该修改主键
            """
            crawler.warning(err)
            query = Complete_Weibo.update(repost_path=item['repost_path']).where(Complete_Weibo.id == item['id'])
            query.execute()
            crawler.warning('********')
            crawler.warning(item['repost_num'])
            crawler.warning('********')


def recursive_fetch():
    """
    退出条件，如果数据库中不存在转发且全部已经爬过了
    :return:
    """
    for row in Complete_Weibo.select().where(Complete_Weibo.repost_num > 0):
        if not row.is_crawled:
            break
    else:
        """
        退出递归 
        """
        return

    for row in Complete_Weibo.select().where(Complete_Weibo.repost_num > 0):
        if not row.is_crawled:
            origin_mid = row.mid_id
            crawler.warning(origin_mid)
            crawler.warning('@@@@@@@')
            crawler.warning(row.repost_num)
            crawler.warning('@@@@@@@')
            repost_path = row.repost_path
            rnd = int(time.time() * 1000)
            repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
            # 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=4153983608441949&__rnd=1506391984010'
            response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
            time.sleep(2)
            """
            发过请求之后，立刻修改数据库状态
            """
            query = Complete_Weibo.update(is_crawled=True).where(Complete_Weibo.id==row.id)
            query.execute()
            crawler.warning("change is_crawled: %s" % row.is_crawled)
            total_json_data = resp_to_text(origin_mid, response)
            total_repost_data = split_the_text(repost_path, total_json_data)
            save_repost_data(total_repost_data)
            # break
    return recursive_fetch()


def test_pre_process():
    """
    通过递归抓取id='4152039828718852'的微博来验证递归程序准确性
    :return:
    """
    target = Complete_Weibo.get(Complete_Weibo.id == '4152039828718852')
    Test_Recursive.create(id=target.id,
                          current_page=target.current_page,
                          mid_id=target.mid_id,
                          repost_html=target.repost_html,
                          repost_user_id=target.repost_user_id,
                          repost_user=target.repost_user,
                          repost_content=target.repost_content,
                          repost_time=target.repost_time,
                          repost_num=target.repost_num,
                          upvote_num=target.upvote_num,
                          repost_path=target.repost_path,
                          is_crawled=target.is_crawled,
                          created_time=target.created_time)


def test_save(total_repost_data):
    for item in total_repost_data:
        try:
            crawler.warning('saving %s' % item['id'])
            Test_Recursive.create(**item)
        except IntegrityError as err:
            """
            可能存在本层与下一级的mid是一样的情况，这时为了展现树的层次关系，应该修改主键
            """
            crawler.warning(err)
            query = Test_Recursive.update(repost_path=item['repost_path']).where(Test_Recursive.id == item['id'])
            query.execute()
            crawler.warning('********')
            crawler.warning(item['repost_num'])
            crawler.warning('********')


def test_recursive():
    more_than_zero = Test_Recursive.select().where(Test_Recursive.repost_num > 0, Test_Recursive.is_crawled == False)
    crawler.warning('----------------------------------------------------------')
    crawler.warning(more_than_zero.count())
    crawler.warning('----------------------------------------------------------')
    while more_than_zero:
        for row in more_than_zero:
            origin_mid = row.mid_id
            with open('test.json', 'w') as f:
                f.write(str(origin_mid))
            crawler.warning(origin_mid)
            crawler.warning('@@@@@@@')
            crawler.warning(row.repost_num)
            crawler.warning('@@@@@@@')
            repost_path = row.repost_path
            rnd = int(time.time() * 1000)
            repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
            response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
            time.sleep(2)
            """
            发过请求之后，立刻修改数据库状态
            """
            query = Test_Recursive.update(is_crawled=True).where(Test_Recursive.id == row.id)
            query.execute()
            total_json_data = resp_to_text(origin_mid, response)
            total_repost_data = split_the_text(repost_path, total_json_data)
            test_save(total_repost_data)
            return test_recursive()


    # for row in Test_Recursive.select().where(Test_Recursive.repost_num > 0):
    #     print('aaa')
    #     if not row.is_crawled:
    #         print('bbb')
    #         break
    # else:
    #     print('ccc')
    #     return
    #
    # for row in Test_Recursive.select().where(Test_Recursive.repost_num > 0):
    #     if not row.is_crawled:
    #         origin_mid = row.mid_id
    #         crawler.warning(origin_mid)
    #         crawler.warning('@@@@@@@')
    #         crawler.warning(row.repost_num)
    #         crawler.warning('@@@@@@@')
    #         repost_path = row.repost_path
    #         rnd = int(time.time() * 1000)
    #         repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
    #         response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
    #         """
    #         发过请求之后，立刻修改数据库状态
    #         """
    #         query = Test_Recursive.update(is_crawled=True).where(Test_Recursive.id == row.id)
    #         query.execute()
    #         total_json_data = resp_to_text(origin_mid, response)
    #         total_repost_data = split_the_text(repost_path, total_json_data)
    #         test_save(total_repost_data)
    #         return test_recursive()



    # target = Test_Recursive.get(Test_Recursive.id == '4152039828718852')
    # origin_mid = target.mid_id
    # crawler.warning(origin_mid)
    # crawler.warning(target.repost_num)
    # repost_path = target.repost_path
    # rnd = int(time.time() * 1000)
    # repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
    # response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
    # query = Test_Recursive.update(is_crawled=True).where(Test_Recursive.id == target.id)
    # query.execute()
    # total_json_data = resp_to_text(origin_mid, response)
    # total_repost_data = split_the_text(repost_path, total_json_data)
    # test_save(total_repost_data)

def test_right_save(total_repost_data):
    for item in total_repost_data:
        try:
            crawler.warning('saving %s' % item['id'])
            Test_Recursive.create(**item)
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


def test_right_or_not():
    target = Complete_Weibo.get(Complete_Weibo.id == '4152150483239700')
    origin_mid = target.mid_id
    crawler.warning(origin_mid)
    crawler.warning('@@@@@@@')
    crawler.warning(target.repost_num)
    crawler.warning('@@@@@@@')
    repost_path = target.repost_path
    rnd = int(time.time() * 1000)
    repost_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd={}'.format(origin_mid, rnd)
    # 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=4153983608441949&__rnd=1506391984010'
    response = s.get(repost_url, headers=headers, verify=False, cookies=cookie)
    time.sleep(2)
    total_json_data = resp_to_text(origin_mid, response)
    total_repost_data = split_the_text(repost_path, total_json_data)
    print(total_repost_data[0]['repost_content'])
    test_right_save(total_repost_data)


def combine():
    # test_right_or_not()
    # test_save()
    # test_recursive()
    pre_process()
    # recursive_fetch()


if __name__ == '__main__':
    combine()

"""
4152039828718852/4152043821902354/4152047614153047/4152052344671841/4152052693588418/


我觉得应该叫鄙婚鄙孕好不好 // @TSUYAYA : 肯定有啊 几亿美元的彩票也有人中啊// @ShojoS_HT沼 :不说信不信的问题，代表我自己表示，因为讨厌小孩子，对我来说的理想爱情和婚姻必须建立在男方全家都不想要下一代的基础上 参考国情，你们懂的
"""