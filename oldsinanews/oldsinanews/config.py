#! python3
# -*- coding: utf-8 -*-
"""
这个文件主要是为了存放自定义的配置。例如：数据库的配置、Redis的配置、以及其他一些控制变量。
"""
import os


USE_PROXY = True

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

RESULT_PATH = os.path.join(BASE_PATH, 'result')

SPIDERS_START_URLS_PATH = os.path.join(BASE_PATH, 'spiders')

__all__ = [USE_PROXY, BASE_PATH]




