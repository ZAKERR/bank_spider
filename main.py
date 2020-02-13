# -*- coding: utf-8 -*-
from scrapy import cmdline


# 中国银行保险监督管理委员会-行政处罚-全国各地区数据
cmdline.execute('scrapy crawl regulatory_commission'.split())
# 香港-证券及期货事务监察委员会-执法信息
# cmdline.execute('scrapy crawl hk_sfc'.split())