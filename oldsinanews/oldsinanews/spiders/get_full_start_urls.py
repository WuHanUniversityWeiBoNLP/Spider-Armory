#! python3
# -*- coding: utf-8 -*-
import re
import json
import logging
import requests
from datetime import date
from random import choice
from dateutil.rrule import rrule, DAILY

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()


class InitStartUrls(object):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN, zh;q=0.9',
        'Cookie': 'UOR=blog.csdn.net,v.t,; SINAGLOBAL=23.83.242.154_1499257711.55098; U_TRS1=0000009f.6d886c81.5964df78.72997f6a; SCF=ApucYxpy-3Lp1K-EbV3M1z443Y4qo_GWaQ7gV41HenSELKMm4ExByoSiFMoYB8QqV-lydd0clcR4DZSLkEGrvLo.; SGUID=1503112074483_86391559; sso_info=v02m6alo5qztYObh5W6mZeQpp2WpaSPk4yxjLOkuY2zlLiOg5zA; SUB=_2AkMtUiyif8NxqwJRmPoXzGjmbop0yAzEieKbDt15JRMyHRl-yD83qhQOtRDH3KD_J5THOZ5uvGvaw7OF4oJlTQ..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFOjEuWBXlLNVVpQ3a0fI1U; Apache=101.231.137.70_1511142404.499382; ULV=1511142501959:6:4:2:101.231.137.70_1511142404.499382:1511142406417; U_TRS2=00000046.42ce8cb2.5a128cf2.b06aa7a5; ; lxlrttp=1510717132',
        'Proxy-Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

    @staticmethod
    def get_proxy():
        five_fastest_proxy = requests.get(
            'http://127.0.0.1:5000/proxy?count=5&anonymity=anonymous&protocol=https').content
        five_fastest_proxy_list = json.loads(five_fastest_proxy)
        sample = choice(five_fastest_proxy_list)
        proxy_ip_address = 'https://' + sample[0] + ':' + sample[1]
        proxy = {"https": "{}".format(proxy_ip_address)}
        return proxy

    def single_year_date(self, version, year):
        if version == 'old':
            if year == 1999:
                single_year_start_date = date(1999, 5, 26)
                single_year_end_date = date(1999, 12, 31)
            elif year == 2010:
                single_year_start_date = date(2010, 1, 1)
                single_year_end_date = date(2010, 3, 29)
            else:
                single_year_start_date = date(year, 1, 1)
                single_year_end_date = date(year, 12, 31)
        single_year_format_date = []
        for dt in rrule(DAILY, dtstart=single_year_start_date, until=single_year_end_date):
            single_year_format_date.append(dt.strftime("%Y-%m-%d"))
        return single_year_format_date

    def arbitrary_date_range(self, version, year, start_date, end_date):
        start_index = self.single_year_date(version, year).index(start_date)
        end_index = self.single_year_date(version, year).index(end_date) + 1
        return self.single_year_date(version, year)[start_index:end_index]

    def decide(self, period):
        """
        分为三个阶段，不同阶段分为不同的策略
        1999-05-26至2007-01-19结束为最旧版本，发请求策略为http://news.sina.com.cn/old1000/news1000_19990528.shtml
        构造url,带着header以及proxy访问即可
        2007-01-20至2007-12-11结束为中间过渡阶段，发请求策略为http://news.sina.com.cn/old1000/news1000_20071210/data0.js
        构造url,js文件中有两个参数totalNews,JsFileNews，所以总的页数可以由totalNews/JsFileNews得到
        2007-12-12至2010-03-29为旧版的最新版本，发请求策略如下：
        http://rss.sina.com.cn/rollnews/news_gn/20071231.js
        http://rss.sina.com.cn/rollnews/news_gj/20071231.js
        http://rss.sina.com.cn/rollnews/news_sh/20071231.js
        http://rss.sina.com.cn/rollnews/jczs/20071231.js
        http://rss.sina.com.cn/rollnews/sports/20071231.js
        http://rss.sina.com.cn/rollnews/ent/20071231.js
        http://rss.sina.com.cn/rollnews/tech/20071231.js
        http://rss.sina.com.cn/rollnews/finance/20071231.js
        http://rss.sina.com.cn/rollnews/stock/20071231.js
        :return:
        """
        if period == 'first':
            all_date = self.arbitrary_date_range('old', 1999, '1999-05-26', '1999-12-31') + \
                       self.arbitrary_date_range('old', 2000, '2000-01-01', '2000-12-31') + \
                       self.arbitrary_date_range('old', 2001, '2001-01-01', '2001-12-31') + \
                       self.arbitrary_date_range('old', 2002, '2002-01-01', '2002-12-31') + \
                       self.arbitrary_date_range('old', 2003, '2003-01-01', '2003-12-31') + \
                       self.arbitrary_date_range('old', 2004, '2004-01-01', '2004-12-31') + \
                       self.arbitrary_date_range('old', 2005, '2005-01-01', '2005-12-31') + \
                       self.arbitrary_date_range('old', 2006, '2006-01-01', '2006-12-31') + \
                       self.arbitrary_date_range('old', 2007, '2007-01-01', '2007-01-19')
            first_period_urls = []
            for year_month_day in all_date:
                logging.info(year_month_day)
                param = ''.join(year_month_day.split('-'))
                start_url = 'http://news.sina.com.cn/old1000/news1000_{}.shtml'.format(param)
                first_period_urls.append(start_url)
                # break
            return first_period_urls
        elif period == 'second':
            all_date = self.arbitrary_date_range('old', 2007, '2007-01-20', '2007-12-11')
            second_period_urls = []
            for year_month_day in all_date:
                try:
                    logging.info(year_month_day)
                    param = ''.join(year_month_day.split('-'))
                    base_url = 'http://news.sina.com.cn/old1000/news1000_{}/data{}.js'
                    start_url = base_url.format(param, 0)
                    logging.info(start_url)
                    request = requests.get(url=start_url, headers=self.headers, proxies=InitStartUrls.get_proxy())
                    js_content = request.text.split(';')
                    total_news = int(re.findall(r'\d+', js_content[2])[0])
                    js_file_news = int(re.findall(r'\d+', js_content[4])[0])
                    total_page_num = int(total_news / js_file_news) + 1
                    logging.info(total_page_num)
                    rest_urls = [base_url.format(param, i) for i in range(1, total_page_num+1)]
                    second_period_urls.append(start_url)
                    second_period_urls.extend(rest_urls)
                    # break
                except Exception as err:
                    logging.info(err)
                    continue
            return second_period_urls
        elif period == 'third':
            all_date = self.arbitrary_date_range('old', 2007, '2007-12-12', '2007-12-31') + \
                       self.arbitrary_date_range('old', 2008, '2008-01-01', '2008-12-31') + \
                       self.arbitrary_date_range('old', 2009, '2009-01-01', '2009-12-31') + \
                       self.arbitrary_date_range('old', 2010, '2010-01-01', '2010-03-29')
            third_period_urls = []
            for year_month_day in all_date:
                logging.info(year_month_day)
                param = ''.join(year_month_day.split('_'))
                all_type_urls = ['http://rss.sina.com.cn/rollnews/news_gn/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/news_gj/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/news_sh/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/jczs/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/sports/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/ent/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/tech/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/finance/{}.js'.format(param),
                                 'http://rss.sina.com.cn/rollnews/stock/{}.js'.format(param)]
                third_period_urls.extend(all_type_urls)
                # break
            return third_period_urls

    def save(self):
        first_period_urls = self.decide('first')
        second_period_urls = self.decide('second')
        third_period_urls = self.decide('third')
        result = {'first_period': first_period_urls, 'second_period': second_period_urls,
                  'third_period': third_period_urls}
        with open('start_urls.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    init = InitStartUrls()
    init.save()