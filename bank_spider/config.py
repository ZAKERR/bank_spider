# -*- coding: utf-8 -*-


# 银保监协会配置文件

bank_custom_settings = {
    "COOKIES_ENABLED": False,  # 禁用cookie
    # "CONCURRENT_REQUESTS": 8,   # 并发设置
    # "DOWNLOAD_DELAY": 0.3,  # 下载延迟
    "RETRY_ENABLED": True,
    "RETRY_TIMES": '9',
    "DOWNLOAD_TIMEOUT": '20',

    "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
    "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
    "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
    "SCHEDULER_PERSIST": True,

    "ITEM_PIPELINES": {
        "bank_spider.pipelines.BankSpiderPipeline": 300,
        "bank_spider.pipelines.DownloadFilesPipeline": 340,
        # "bank_spider.pipelines.Save2eEsPipeline": 380,
        "bank_spider.pipelines.MongodbIndexPipeline": 390,
    },

    "DOWNLOADER_MIDDLEWARES": {
        "bank_spider.middlewares.RandomUserAgentMiddleware": 400,
        # "bank_spider.middlewares.RandomProxyMiddlerware": 410,
        # "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        # "bank_spider.middlewares.GsxcxRetryMiddlerware": 420,
    },

    "DEFAULT_REQUEST_HEADERS": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "www.cbirc.gov.cn",
        "Pragma": "no-cache",
        "X-Requested-With": "XMLHttpRequest",
    }
}

# 香港-证券及期货事务监察委员会-执法信息
hk_custom_settings = {
    "RETRY_ENABLED": True,
    "RETRY_TIMES": '9',
    "DOWNLOAD_TIMEOUT": '20',

    "ITEM_PIPELINES": {
        "bank_spider.pipelines.BankSpiderPipeline": 300,
        # "bank_spider.pipelines.Save2eEsPipeline": 380,
        "bank_spider.pipelines.MongodbIndexPipeline": 390,
    },

    "DOWNLOADER_MIDDLEWARES": {
        "bank_spider.middlewares.RandomUserAgentMiddleware": 400,
        # "bank_spider.middlewares.RandomProxyMiddlerware": 410,
        # "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        # "bank_spider.middlewares.GsxcxRetryMiddlerware": 420,
    },
}