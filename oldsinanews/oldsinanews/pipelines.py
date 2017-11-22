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
            dt = dparser.parse(item['news_time'], fuzzy=True).strptime("%Y-%m-%d")
            datetime_file_path = os.path.join(RESULT_PATH, dt)
            with open('%s/%s.json' % (datetime_file_path, item['news_id']), 'w') as f:
                f.write(json.dumps(item))
        else:
            raise DropItem("Missing title in %s" % item)

