# -*- coding: utf-8 -*-
import math
import re
import time
import logging

import pymongo
import scrapy
from fontTools import unichr
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import FilesPipeline

from bank_spider import settings
from bank_spider.work_utils.filter_fact import cf_filter_fact
from bank_spider.work_utils.save_data import EsObject

logger = logging.getLogger(__name__)


class BankSpiderPipeline(object):
    """ 添加必要字段简单数据清洗 """

    def handle_other(self, time_date):
        """ 处理日期 """
        if time_date:
            time_date = re.sub(r'\n|\r|\t| |\s', '', time_date)
            return time_date
        else:
            return None

    def strQ2B(self, ustring):
        """全角转半角 """
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 12288:
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):
                inside_code -= 65248
            rstring += unichr(inside_code)
        return rstring

    def strB2Q(self, ustring):
        """ 半角转全角 """
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 32:
                inside_code = 12288
            elif inside_code >= 32 and inside_code <= 126:
                inside_code += 65248
            rstring += unichr(inside_code)
        return rstring

    def handle_date(self, _str: str):
        """ 时间格式转换 """
        if _str:
            _str = re.sub('(年|月)', '-', _str)
            _str = re.sub('日', '', _str)
            first = re.compile(r'(\d{4}-\d{2}-\d{2})')
            first = first.search(_str)
            second = re.compile(r'(\d{4}-\d{2}-\d{1})')
            second = second.search(_str)
            third = re.compile(r'(\d{4}-\d{1}-\d{2})')
            third = third.search(_str)
            fourth = re.compile(r'(\d{4}-\d{1}-\d{1})')
            fourth = fourth.search(_str)
            if first:
                return first.group()
            elif second:
                year = re.search(r'(\d{4})-', _str).group(1)
                month = re.search(r'\d{4}-(\d+)-', _str).group(1)
                day = _str.split('-')[-1]
                result = str(year) + '-' + str(month) + '-' + '0' + str(day)
                return result
            elif third:
                year = re.search(r'(\d{4})-', _str).group(1)
                month = re.search(r'\d{4}-(\d+)-', _str).group(1)
                day = _str.split('-')[-1]
                result = str(year) + '-' + '0' + str(month) + '-' + str(day)
                return result
            elif fourth:
                year = re.search(r'(\d{4})-', _str).group(1)
                month = re.search(r'\d{4}-(\d+)-', _str).group(1)
                day = _str.split('-')[-1]
                result = str(year) + '-' + '0' + str(month) + '-' + '0' + str(day)
                return result
            else:
                return None
        else:
            return None

    def process_item(self, item, spider):
        item['sj_ztxx'] = 1  # es显示数据专用
        # 添加分类标记
        # item['sj_type'] = '43'
        # 添加时间戳
        item['cj_sj'] = math.ceil(time.time())
        cf_jdrq = item.get('cf_jdrq')
        fb_rq = item.get('fb_rq')
        cf_jdrq = self.handle_date(cf_jdrq)
        cf_jdrq = self.strQ2B(cf_jdrq) if cf_jdrq else None
        cf_jdrq = self.handle_other(cf_jdrq) if cf_jdrq else None
        item['fb_rq'] = self.handle_date(fb_rq)
        item['cf_jdrq'] = cf_jdrq.replace("号", "") if cf_jdrq else None
        ws_pc_id = cf_filter_fact(item)
        if ws_pc_id:
            item['ws_pc_id'] = ws_pc_id
        else:
            DropItem(item)
        return item


class DownloadFilesPipeline(FilesPipeline):
    """ 文件下载，管道文件 """

    def get_media_requests(self, item, info):
        """ 文件下载 """
        sf = item.get('sf')
        cf_cfmc = item.get('cf_cfmc')
        img_url = item.get('img_url', '')  # 图片下载链接
        wbbz = item.get('wbbz', '')  # doc下载链接
        bz = item.get('bz', '')  # PDF下载链接
        meta_data = {'sf': sf, 'cf_cfmc': cf_cfmc}
        if img_url:
            yield scrapy.Request(url=img_url, meta=meta_data)
        if wbbz:
            yield scrapy.Request(url=wbbz, meta=meta_data)
        if wbbz:
            yield scrapy.Request(url=bz, meta=meta_data)

    def file_path(self, request, response=None, info=None):
        """ 重命名文件夹名称 """
        # 文件夹名称
        file_name = request.meta.get('sf')  # 根据省份名称保存到不同文件夹
        # 图片名称
        img_name = request.meta.get('cf_cfmc') + '.' + request.url.split('.')[-1]
        save_file_name = u'{0}/{1}'.format(file_name, img_name)
        return save_file_name

    def item_completed(self, results, item, info):
        # 获取省份信息--按照省份对文件夹进行命名
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['cf_file_name'] = image_paths[0]
            # print(item.get('img_url'))
        else:
            item['cf_file_name'] = ''
            # raise DropItem('Image Downloaded Failed')
        return item


class Save2eEsPipeline(object):
    """ 存储elasticsearch """
    def __init__(self):
        self.es = EsObject(index_name=settings.INDEX_NAME, index_type=settings.INDEX_TYPE, host=settings.ES_HOST, port=settings.ES_PORT)

    def process_item(self, item, spider):
        if item:
            # 获取唯一ID
            _id = item['ws_pc_id']
            res1 = self.es.get_data_by_id(_id)
            if res1.get('found') == True:
                logger.debug("该数据已存在%s" % _id)
                # self.es.update_data(dict(item), _id)
            else:
                self.es.insert_data(dict(item), _id)
                logger.debug("----------抓取成功,开始插入数据%s" % _id)
                return item


class MongodbIndexPipeline(object):
    """ 存储到mongodb数据库并且创建索引 """
    def __init__(self, mongo_uri, mongo_db):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATA_BASE')
        )

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.create_index([('oname', 1), ('spider_time', -1)])  # 1表示升序，-1降序
        try:
            collection.insert(dict(item))
        except:
            logger.debug('数据重复')
            # raise DropItem(item)
        return item