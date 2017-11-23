#! python3
# -*- coding: utf-8 -*-
import re
import json
import scrapy
import requests
from datetime import date, datetime
from dateutil.rrule import rrule, DAILY
from scrapy.http import Request
from pyquery import PyQuery as Pq
from fnvhash import fnv1a_64
from oldsinanews.items import OldsinanewsItem
from oldsinanews.settings import *
from oldsinanews.config import SPIDERS_START_URLS_PATH
from newspaper import Article


class OldSinaNews(scrapy.Spider):
    name = "oldsinanews"
    allowed_domains = ["news.sina.com.cn", "rss.sina.com.cn"]

    start_urls = []

    with open('%s/start_urls.json' % SPIDERS_START_URLS_PATH, 'r') as f:
        fixed_data = json.loads(f.read())

    all_urls = fixed_data['first_period']
    start_urls.extend(all_urls)
    """
    测试加入middlewares以及settings的headers后是否每个请求都会带着proxy以及header
    """
    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(start_url, callback=self.parse)
            break

    def parse(self, response):
        """
        试验证明加入middlewares后每个请求都有proxy
        header还需修改
        https://stackoverflow.com/questions/14220174/how-to-add-headers-to-scrapy-crawlspider-requests
        :param response:
        :return:
        """
        block = response.css('ul li')
        for element in block:
            press_title = element.css('a::text').extract()[-1]
            press_url = element.css('a::attr(href)').extract()[-1]
            absolute_press_url = response.urljoin(press_url)
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print(absolute_press_url)
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$')
            item = OldsinanewsItem(news_title=press_title, news_url=absolute_press_url)
            request = Request(url=absolute_press_url, callback=self.parse_article)
            request.meta['item'] = item
            yield request

    def parse_article(self, response):
        if response.status == 200:
            print('******************')
            print(response.url)
            print('******************')
            item = response.meta['item']
            press_content = response.body
            if not isinstance(response.url, bytes):
                response_url_byte = response.url.encode('utf8', 'ignore')
            press_id = fnv1a_64(response_url_byte)
            print(press_id)
            press_type = re.findall(r'http.+cn', response.url)[0].replace('http://', '')
            print(press_type)
            raw_press_time = re.findall(u'\d+年\d+月\d+日', response.text)[0]
            print('^^^^^^^^^^^^^^^^^^')
            press_time = '-'.join(re.findall(r'\d+', raw_press_time))
            print('^^^^^^^^^^^^^^^^^^')
            oldsinanewsitem = OldsinanewsItem(news_id=press_id, news_content=press_content, news_type=press_type, news_time=press_time)
            yield oldsinanewsitem






