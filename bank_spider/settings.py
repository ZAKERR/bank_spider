# -*- coding: utf-8 -*-
import os

BOT_NAME = 'bank_spider'

SPIDER_MODULES = ['bank_spider.spiders']
NEWSPIDER_MODULE = 'bank_spider.spiders'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
scrapy基本配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'INFO'
RANDOM_UA_TYPE = "random"

project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 文件存储
FILES_STORE = os.path.join(project_path, 'files')  # 存储路径
FILES_EXPIRES = 90  # 失效时间

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
数据存储 相关配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
ES_HOST = '49.4.22.216'
ES_PORT = 9999
ES_USERNAME = ''
ES_PASSWORD = ''
INDEX_NAME = 'cf_index_db'
INDEX_TYPE = 'xzcf'

# 存储到mongodb
MONGO_URI = '127.0.0.1'
MONGO_DATA_BASE = 'bank_spider'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
redis 相关配置
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# 缓存去重配置
REDIS_HOST = '127.0.0.1'
# REDIS_HOST = '114.115.201.98'
REDIS_PORT = 6379
# REDIS_PASSWORD = 'axy@2019'
REDIS_PASSWORD = ''
REDIS_DB = 3
REDIS_PARAMS = {
    # "password": "axy@2019",
    "password": "",
    "db": 3,
}

# redis 代理池配置
REDIS_PROXIES_HOST = '117.78.35.12'
REDIS_PROXIES_PORT = 6379
REDIS_PROXIES_PASSWORD = ''
REDIS_PROXIES_DB = 15