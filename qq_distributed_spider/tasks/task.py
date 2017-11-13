#! python3
# -*- coding: utf-8 -*-
"""
先掏粪掏出来，不要想着一口气优化到很完美的程度
1.先将所有代码写在一起，实现celery的功能
2.模块化
3.加入asyncio功能
"""
import re
import os
import time
import json
import requests
import logging
import chardet
from random import uniform
from dateutil.rrule import rrule, DAILY
from datetime import date
from celery import Celery
from kombu import Exchange, Queue
from celery import platforms
from workers import app
from proxy.start_proxy import Proxy
from header import header
from file_location import init_path, res_path
from pyquery import PyQuery as Pq


BASE_URL = 'http://roll.finance.qq.com/interface/roll.php?' \
           '{0}&cata=&site=finance&date={1}&page={2}&mode=1&of=json'


class UrlParam(object):
    @staticmethod
    def single_year_date(year):
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        former_date = []
        for dt in rrule(DAILY, dtstart=start_date, until=end_date):
            former_date.append(dt.strftime("%Y-%m-%d"))
        return former_date

    @staticmethod
    def single_year_date_range(year, start_date, end_date):
        start_index = UrlParam.single_year_date(year).index(start_date)
        end_index = UrlParam.single_year_date(year).index(end_date)
        return UrlParam.single_year_date(year)[start_index:end_index]

    @staticmethod
    def get_r_param():
        return "%.17f" % uniform(0, 1)


@app.task(ignore_result=True)
def init_fetch(year_month_day):
    """
    If you don’t use the results for a task, make sure you set the ignore_result option
    :param year_month_day:
    :return:
    """
    r_param = UrlParam.get_r_param()
    init_url = BASE_URL.format(r_param, year_month_day, 1)
    proxy = Proxy.get_proxy()
    r = requests.get(init_url, headers=header, proxies=proxy, timeout=11)
    time.sleep(uniform(2, 4))
    r.encoding = chardet.detect(r.content)['encoding']
    if r.status_code == 200:
        json_dict = json.loads(r.text)
        if json_dict['response']['code'] == '0':
            specific_date_init_path = os.path.join(init_path, year_month_day)
            if not os.path.exists(specific_date_init_path):
                os.makedirs(specific_date_init_path)
            with open('%s/%s.json' % (specific_date_init_path, 1), 'wb') as f:
                f.write(r.content)
            page_num = int(json_dict['data']['count'])
            if page_num != 1:
                return year_month_day, json_dict, page_num


@app.task(ignore_result=True)
def follow_fetch(year_month_day, page_num):
    for index in range(2, page_num+1):
        r_param = UrlParam.get_r_param()
        rest_url = BASE_URL.format(r_param, year_month_day, index)
        proxy = Proxy.get_proxy()
        r = requests.get(rest_url, headers=header, proxies=proxy, timeout=11)
        time.sleep(uniform(2, 4))
        r.encoding = chardet.detect(r.content)['encoding']
        if r.status_code == 200:
            specific_date_init_path = os.path.join(init_path, year_month_day)
            if not os.path.exists(specific_date_init_path):
                os.makedirs(specific_date_init_path)
            with open('%s/%s.json' % (specific_date_init_path, index), 'wb') as f:
                f.write(r.content)


@app.task
def parse(year_month_day):
    specific_date_init_path = os.path.join(init_path, year_month_day)
    specific_date_init_path_file = os.listdir(specific_date_init_path)
    for file in specific_date_init_path_file:
        with open('%s/%s' % (specific_date_init_path, file), 'r') as f:
            json_dict = json.loads(f.read())
            json_data = json_dict['data']
            article_info = json_data['article_info']
            d = Pq(article_info)
            block = d('ul li')
            for item in block.items():
                t_time = item('.t-time').text()
                t_tit = item('.t-tit').text()
                t_url = item('a').attr('href')
                t_title = item('a').text()
                save_id = ''.join(re.findall(r'\d+', t_url))
                proxy = Proxy.get_proxy()
                r = requests.get(t_url, headers=header, proxies=proxy, timeout=11)
                r.encoding = chardet.detect(r.content)['encoding']
                d = Pq(r.text).make_links_absolute(base_url=t_url)
                next_page_url = d('#ArtPLink #ArticlePageLinkB .next a').attr('href')
                if next_page_url:
                    d.remove('#ArtPLink #ArticlePageLinkB .next').remove()
                    total_page_num = int(re.findall(r'\d+', d('#ArtPLink #ArticlePageLinkB a').eq(-1).text())[0])
                    for index in range(1, total_page_num):
                        """
                        构造有多页的页面
                        e.g: finance.qq.com/a/20090109/000495.htm
                        url: /a/20090109/000495_1.html  [2]
                        url: /a/20090109/000495_2.html  [3]
                        """
                        proxy = Proxy.get_proxy()
                        rest_url = t_url.replace('.htm', '_%s.htm' % index)
                        rest_r = requests.get(rest_url, headers=header, proxies=proxy, timeout=11)
                        rest_r.encoding = chardet.detect(rest_r.content)['encoding']
                        rest_d = Pq(rest_r.text).make_links_absolute(base_url=rest_url)
                        rest_r_content = rest_d('#Cnt-Main-Article-QQ').html() or rest_d('#ArticleCnt').html()
                        html_save_path = os.path.join(res_path, year_month_day)
                        if not os.path.exists(html_save_path):
                            os.makedirs(html_save_path)
                        with open('', 'wb') as ff:
                            ff.write()
