# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
from oldsinanews.config import BASE_PATH, RESULT_PATH
from scrapy.exceptions import DropItem
import dateutil.parser as dparser


class OldsinanewsPipeline(object):
    def process_item(self, item, spider):
        if item['news_id']:
            datetime_file_path = os.path.join(RESULT_PATH, item['news_time'])
            if not os.path.exists(datetime_file_path):
                os.mkdir(datetime_file_path)
            with open('%s/%s.html' % (datetime_file_path, item['news_id']), 'wb') as f:
                f.write(item['news_html'])
            datetime_json_file_path = os.path.join(datetime_file_path, 'json_result')
            if not os.path.exists(datetime_json_file_path):
                os.mkdir(datetime_json_file_path)
            json_result = {'news_id': item['news_id'], 'news_type': item['news_type'],
                           'news_title': item['news_title'],
                           'news_url': item['news_url'], 'news_time': item['news_time'],
                           'news_content': item['news_content']}
            with open('%s/%s.json' % (datetime_json_file_path, item['news_id']), 'w', encoding='utf8') as f:
                f.write(json.dumps(json_result, sort_keys=True, indent=4, ensure_ascii=False))
        else:
            raise DropItem("Missing title in %s" % item)

