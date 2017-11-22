# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json
import requests
from scrapy import signals
from scrapy import Spider
from random import choice


class ProxyPool(object):
    @staticmethod
    def get_proxy():
        five_fastest_proxy = requests.get(
            'http://127.0.0.1:5000/proxy?count=5&anonymity=anonymous&protocol=https').content
        five_fastest_proxy_list = json.loads(five_fastest_proxy)
        sample = choice(five_fastest_proxy_list)
        proxy_ip_address = 'https://' + sample[0] + ':' + sample[1]
        proxy = {"https": "{}".format(proxy_ip_address)}
        return proxy


class CustomHttpProxyMiddleware(object):
    def process_request(self, request, spider):
        try:
            request.meta['proxy'] = ProxyPool.get_proxy()
        except Exception as e:
            """
            如果爬虫代理挂了，可以在这里根据路径重新启动爬虫
            """
            pass


# class OldsinanewsSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Response, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
