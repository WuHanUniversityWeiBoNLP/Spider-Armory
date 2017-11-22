# -*- coding: utf-8 -*-

# Scrapy settings for oldsinanews project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
from oldsinanews.config import USE_PROXY

BOT_NAME = 'oldsinanews'

SPIDER_MODULES = ['oldsinanews.spiders']
NEWSPIDER_MODULE = 'oldsinanews.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'oldsinanews (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': '*/*',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN, zh;q=0.9',
  'Cookie': 'UOR=blog.csdn.net,v.t,; SINAGLOBAL=23.83.242.154_1499257711.55098; U_TRS1=0000009f.6d886c81.5964df78.72997f6a; SCF=ApucYxpy-3Lp1K-EbV3M1z443Y4qo_GWaQ7gV41HenSELKMm4ExByoSiFMoYB8QqV-lydd0clcR4DZSLkEGrvLo.; SGUID=1503112074483_86391559; sso_info=v02m6alo5qztYObh5W6mZeQpp2WpaSPk4yxjLOkuY2zlLiOg5zA; SUB=_2AkMtUiyif8NxqwJRmPoXzGjmbop0yAzEieKbDt15JRMyHRl-yD83qhQOtRDH3KD_J5THOZ5uvGvaw7OF4oJlTQ..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFOjEuWBXlLNVVpQ3a0fI1U; Apache=101.231.137.70_1511142404.499382; ULV=1511142501959:6:4:2:101.231.137.70_1511142404.499382:1511142406417; U_TRS2=00000046.42ce8cb2.5a128cf2.b06aa7a5; ; lxlrttp=1510717132',
  'Proxy-Connection': 'keep-alive',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'oldsinanews.middlewares.OldsinanewsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'oldsinanews.middlewares.CatchExceptionMiddleware': None,
}
if USE_PROXY:
    DOWNLOADER_MIDDLEWARES['oldsinanews.middlewares.CustomHttpProxyMiddleware'] = 1
# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'oldsinanews.pipelines.OldsinanewsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
