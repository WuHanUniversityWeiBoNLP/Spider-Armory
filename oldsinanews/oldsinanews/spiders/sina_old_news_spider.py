#! python3
# -*- coding: utf-8 -*-
import re
import json
import scrapy
import logging
import requests
import chardet
from datetime import date, datetime
from dateutil.rrule import rrule, DAILY
from scrapy.http import Request
from pyquery import PyQuery as Pq
from fnvhash import fnv1a_64
from oldsinanews.items import OldsinanewsItem
from oldsinanews.settings import *
from oldsinanews.config import SPIDERS_START_URLS_PATH
from newspaper import Article


logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()


class OldSinaNews(scrapy.Spider):
    name = "oldsinanews"
    allowed_domains = ["news.sina.com.cn", "rss.sina.com.cn"]

    start_urls = []

    with open('%s/start_urls.json' % SPIDERS_START_URLS_PATH, 'r') as f:
        fixed_data = json.loads(f.read())

    all_urls = fixed_data['first_period']
    start_urls.extend(all_urls)

    headers = {
      'Accept': '*/*',
      'Accept-Encoding': 'gzip, deflate',
      'Accept-Language': 'zh-CN, zh;q=0.9',
      'Cookie': 'UOR=blog.csdn.net,v.t,; SINAGLOBAL=23.83.242.154_1499257711.55098; U_TRS1=0000009f.6d886c81.5964df78.72997f6a; SCF=ApucYxpy-3Lp1K-EbV3M1z443Y4qo_GWaQ7gV41HenSELKMm4ExByoSiFMoYB8QqV-lydd0clcR4DZSLkEGrvLo.; SGUID=1503112074483_86391559; sso_info=v02m6alo5qztYObh5W6mZeQpp2WpaSPk4yxjLOkuY2zlLiOg5zA; SUB=_2AkMtUiyif8NxqwJRmPoXzGjmbop0yAzEieKbDt15JRMyHRl-yD83qhQOtRDH3KD_J5THOZ5uvGvaw7OF4oJlTQ..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFOjEuWBXlLNVVpQ3a0fI1U; Apache=101.231.137.70_1511142404.499382; ULV=1511142501959:6:4:2:101.231.137.70_1511142404.499382:1511142406417; U_TRS2=00000046.42ce8cb2.5a128cf2.b06aa7a5; ; lxlrttp=1510717132',
      'Proxy-Connection': 'keep-alive',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

    """
    测试加入middlewares以及settings的headers后是否每个请求都会带着proxy以及header
    """
    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(start_url, headers=self.headers, callback=self.parse)
            break

    def parse(self, response):
        """
        试验证明加入middlewares后每个请求都有proxy
        header还需修改
        https://stackoverflow.com/questions/14220174/how-to-add-headers-to-scrapy-crawlspider-requests
        :param response:
        :return:
        """
        if response.status == 200:
            text = response.body
            content_type = chardet.detect(text)
            print('$$$$$$$$$$$$$$$$$$$$$')
            print(content_type)
            print('$$$$$$$$$$$$$$$$$$$$$')
            block = response.css('ul li')
            for element in block:
                print('@@@@@@@@@@@@@@@@@@@@@@')
                press_title = element.css('a::text').extract()[-1].encode('gb2312', 'ignore').decode('gb2312', 'ignore')
                print(press_title)
                print('@@@@@@@@@@@@@@@@@@@@@@')
                press_url = element.css('a::attr(href)').extract()[-1]
                absolute_press_url = response.urljoin(press_url)
                logger.info(absolute_press_url)
                item = OldsinanewsItem(news_title=press_title, news_url=absolute_press_url)
                request = Request(url=absolute_press_url, headers=self.headers, callback=self.parse_article)
                request.meta['item'] = item
                yield request

    def parse_article(self, response):
        if response.status == 200:
            logger.info(response.url)
            item = response.meta['item']  # 上一级中暂存的包含url, 文章内容
            press_content = response.text
            if not isinstance(response.url, bytes):
                response_url_byte = response.url.encode('utf8', 'ignore')
            press_id = fnv1a_64(response_url_byte)
            logger.info(press_id)
            press_type = re.findall(r'http.+cn', response.url)[0].replace('http://', '')
            logger.info(press_type)
            raw_press_time = re.findall(u'\d+年\d+月\d+日', response.text)[0]
            press_time = '-'.join(re.findall(r'\d+', raw_press_time))
            logger.info(press_time)
            item['news_id'] = press_id
            item['news_content'] = press_content
            item['news_type'] = press_type
            item['news_time'] = press_time
            item['news_html'] = response.body
            yield item






