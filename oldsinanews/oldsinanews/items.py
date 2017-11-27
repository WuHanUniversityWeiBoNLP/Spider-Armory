# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class OldsinanewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    news_id = scrapy.Field()  # 新闻id
    news_type = scrapy.Field()  # 新闻类别  e.g. 国际
    news_title = scrapy.Field()  # 新闻标题
    news_url = scrapy.Field()  # 新闻url
    news_time = scrapy.Field()  # 新闻时间
    news_content = scrapy.Field()  # 新闻内容
    news_html = scrapy.Field()  # 新闻原始html
