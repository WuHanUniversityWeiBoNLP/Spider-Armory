#! python3
# -*- coding: utf-8 -*-
import scrapy
import requests
from datetime import date, datetime
from dateutil.rrule import rrule, DAILY
from scrapy.http import Request
from pyquery import PyQuery as Pq
# from oldsinanews.items import OldsinanewsItem
# from oldsinanews.settings import *


class OldSinaNews(scrapy.Spider):
    name = "oldsinanews"
    allowed_domains = ["news.sina.com.cn", "rss.sina.com.cn"]





    start_urls = []



    # def init_add(self, period):
    #     """
    #     由于decide方法为second或者third时，由于并不是所有的url,需要进行剩余页数的请求，
    #     获取完整的url，这样才能的到所有内容
    #     :return:
    #     """
    #     if period == 'second':

    def start_requests(self):
        print(Request('http://rss.sina.com.cn/rollnews/news_gn/20071231.js').headers)
        # print(self.decide('second'))
        # for start_url in self.start_urls:
            # yield Request(start_url, callback=self.parse)

    def parse(self, response):
        block = response.css('#NewsList ul li')
        for element in block:
            press_type = element.css('.liTi a::text').extract()
            press_title = element.css('.liLink a::text').extract()
            press_url = element.css('.liLink a::attr(href)').extract()[-1]
            press_time = element.css('.liData::text').extract()
            item = OldsinanewsItem(news_type=press_type, news_title=press_title, news_url=press_url,
                                   news_time=press_time)
            yield item

        next_page = response.css('#newsPages a:')


if __name__ == '__main__':
    test = OldSinaNews()
    test.decide('second')

