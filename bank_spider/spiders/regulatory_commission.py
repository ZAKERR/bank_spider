# -*- coding: utf-8 -*-
import json
import logging
import re
from functools import reduce

import scrapy
from w3lib.html import remove_tags

from bank_spider.config import bank_custom_settings
from bank_spider.work_utils.clean_bank import get_cf_wsh, get_oname, get_cf_sy, get_cf_yj, get_cf_jg

logger = logging.getLogger(__name__)


class RegulatoryCommissionSpider(scrapy.Spider):
    name = 'regulatory_commission'
    allowed_domains = ['cbirc.gov.cn']
    start_urls = [
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1756&pageSize=18&pageIndex=1',  # 青岛
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1076&pageSize=18&pageIndex=1',  # 厦门
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1142&pageSize=18&pageIndex=1',  # 宁波
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1723&pageSize=18&pageIndex=1',  # 大连
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2124&pageSize=18&pageIndex=1',  # 新疆
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2190&pageSize=18&pageIndex=1',  # 宁夏
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2091&pageSize=18&pageIndex=1',  # 甘肃

        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1647&pageSize=18&pageIndex=1',  # 陕西
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2157&pageSize=18&pageIndex=1',  # 西藏
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1954&pageSize=18&pageIndex=1',  # 云南
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1921&pageSize=18&pageIndex=1',  # 贵州
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2025&pageSize=18&pageIndex=1',  # 四川
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1987&pageSize=18&pageIndex=1',  # 重庆
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1581&pageSize=18&pageIndex=1',  # 海南

        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1614&pageSize=18&pageIndex=1',  # 广西
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1548&pageSize=18&pageIndex=1',  # 广东
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1482&pageSize=18&pageIndex=1',  # 湖南
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1416&pageSize=18&pageIndex=1',  # 湖北
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1383&pageSize=18&pageIndex=1',  # 河南
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1515&pageSize=18&pageIndex=1',  # 江西
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1109&pageSize=18&pageIndex=1',  # 福建

        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1208&pageSize=18&pageIndex=1',  # 安徽
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1175&pageSize=18&pageIndex=1',  # 浙江
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1241&pageSize=18&pageIndex=1',  # 江苏
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1000&pageSize=18&pageIndex=1',  # 上海
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1307&pageSize=18&pageIndex=1',  # 黑龙江
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1449&pageSize=18&pageIndex=1',  # 吉林
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1690&pageSize=18&pageIndex=1',  # 辽宁
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1888&pageSize=18&pageIndex=1',  # 内蒙古
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1340&pageSize=18&pageIndex=1',  # 山西
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1822&pageSize=18&pageIndex=1',  # 河北
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1789&pageSize=18&pageIndex=1',  # 天津
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1855&pageSize=18&pageIndex=1',  # 北京
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=2058&pageSize=18&pageIndex=1',  # 青海
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1043&pageSize=18&pageIndex=1',  # 深圳
        'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocItemByItemPId?itemId=1274&pageSize=18&pageIndex=1',  # 山东
    ]
    custom_settings = bank_custom_settings
    base_item = {
        'sj_type': '43',
        'xxly': '中国银行保险监督管理委员会-行政处罚-代码采集-全国各地区',
        'site_id': 38346,
    }

    def parse(self, response):
        """ 列表数据解析 """
        # 列表解析以及详情页请求
        results = json.loads(response.text)
        rows_list = results.get('data').get('rows')
        if not rows_list:
            return
        for row in rows_list:
            docFileUrl = row.get('docFileUrl')  # doc下载链接
            pdfFileUrl = row.get('pdfFileUrl')  # pdf下载链接
            itemName = row.get('itemName')  # 处罚类别
            # docTitle = row.get('docTitle')  # 标题
            # publishDate = row.get('publishDate')  # 发布日期
            # publishDate = publishDate[:10] if publishDate else None
            docId = row.get('docId')  # 详情页参数
            xq_url = 'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectByDocId/data_docId={}.json'.format(docId)
            doc_url = 'http://www.cbirc.gov.cn' + docFileUrl
            pdf_url = 'http://www.cbirc.gov.cn' + pdfFileUrl
            meta_data = {'wbbz': doc_url, 'bz': pdf_url, 'cf_type': itemName}
            yield scrapy.Request(
                url=xq_url,
                callback=self.parse_details,
                meta={'item': meta_data},
                priority=5,
            )

        # 翻页请求
        is_first = response.meta.get("is_first", True)
        total = results.get('data').get('total')  # 数据总量
        pages = int(int(total) / 18) if int(total) % 18 == 0 else int(int(total) / 18) + 1
        if is_first:
            if pages > 1:
                for page in range(2, pages + 1):
                    url = response.url.replace('pageIndex=1', 'pageIndex={}'.format(page))
                    # print(f'翻页url:{url}')
                    yield scrapy.Request(url=url, meta={'is_first': False}, priority=3)

    def parse_details(self, response):
        """ 解析详情页 """
        re_com = re.compile(r'\r|\n|\t|\s')
        base_data = response.meta.get('item')
        # 正则提取规则
        dq_mc = re.compile(r'(地址：)(.*?)(主要负责人)')
        # 详情页解析
        results = json.loads(response.body.decode('utf-8'))
        base_item = results.get('data')
        docTitle = base_item.get('docTitle')  # 标题
        publishDate = base_item.get('publishDate')  # 发布日期
        publishDate = publishDate[:10] if publishDate else None
        docSource = base_item.get('docSource')  # 省份
        docClob = base_item.get('docClob').strip()  # 网页源码
        listTwoItem = base_item.get('listTwoItem')[0].get('ItemLvs')[0].get('itemName')  # 处罚机关
        cf_wsh_com = re.compile(r'((\(|（).*?\d{4}.*?\d+号)')
        cf_wsh = cf_wsh_com.search(docTitle)
        cf_wsh = cf_wsh.group() if cf_wsh else ''
        selector = scrapy.Selector(text=docClob)
        # 获取图片表格下载链接
        img_url_list = selector.xpath('//img/@src').getall()
        # 表格解析
        base_table = selector.css('table[class=MsoNormalTable]')
        second_table = selector.css('table[class=normal] tr td')
        # third_table = selector.css('table[class=ke-zeroborder]')
        # div后面带了一堆的p标签格式
        base_div = selector.xpath('//div[@class="Section0"]//text()')

        # 解析table结构的数据
        if base_table:
            for data in base_table:
                cf_wsh = data.xpath('string(./tr[1]/td[2]/p)').get('').replace('\r', '').replace('\n', '')  # 行政处罚决定书文号
                oname_first = data.xpath('string(./tr[2]/td[3]//p)').get('').replace('——', '').replace('--', '').replace('/', '').replace('—', '').replace('-', '').strip()  # 主体=个人姓名
                oname_second = data.xpath('string(./tr[3]/td[3]//p)').get()  # 主体=企业名称
                pname = data.xpath('string(./tr[4]/td[2]/p)').get('').replace('——', '').replace('--', '').strip()  # 法人
                cf_sy = data.xpath('string(./tr[5]/td[2]/p)').get().strip()  # 处罚事由
                cf_yj = data.xpath('string(./tr[6]/td[2]/p)').get().strip()  # 处罚依据
                cf_jg = data.xpath('string(./tr[7]/td[2]/p)').get().strip()  # 处罚结果
                cf_xzjg = data.xpath('string(./tr[8]/td[2]/p)').get().strip()  # 处罚决定机关
                cf_jdrq = data.xpath('string(./tr[last()]/td[2]/p)').get().strip()  # 处罚决定日期
                oname = oname_first if oname_first else oname_second

                table_item = dict(
                    oname=oname.replace('\r', '').replace('\n', '').replace('\xa0', ''), cf_wsh=cf_wsh, pname=pname, cf_sy=cf_sy,
                    cf_yj=cf_yj, cf_jg=cf_jg, cf_xzjg=cf_xzjg, cf_jdrq=cf_jdrq, cf_cfmc=docTitle,
                    fb_rq=publishDate, sf=docSource, ws_nr_txt=docClob, xq_url=response.url,
                )
                second_item = {**table_item, **base_data, **self.base_item}
                # print(f'table结构:{second_item}')
                yield second_item

        elif second_table:
            for p in second_table:
                cf_wsh = p.xpath('string(./p[2])').get('').strip()
                oname = p.xpath('string(./p[3])').get('').strip()
                cf_jg = p.xpath('string(./p[4])').get('').strip()

                table_item = dict(
                    oname=oname, cf_wsh=cf_wsh, cf_jg=cf_jg, cf_cfmc=docTitle,
                    fb_rq=publishDate, sf=docSource, ws_nr_txt=docClob, xq_url=response.url,
                )
                second_item = {**table_item, **base_data, **self.base_item}
                # print(f'table结构:{second_item}')
                yield second_item

        # HTML完整DIV下面带P结构
        elif base_div:
                data_list = base_div.getall()
                if data_list:
                    ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in data_list])
                else:
                    ws_nr_txt = ''
                dq_mc = dq_mc.search(ws_nr_txt)
                dq_mc = dq_mc.group(2) if dq_mc else ''
                oname = get_oname(ws_nr_txt)
                cf_wsh = cf_wsh if cf_wsh else get_cf_wsh(ws_nr_txt)
                cf_sy = get_cf_sy(ws_nr_txt)
                cf_yj = get_cf_yj(ws_nr_txt)
                cf_jg = get_cf_jg(ws_nr_txt)
                p_item = dict(
                    oname=oname, cf_wsh=cf_wsh, cf_sy=cf_sy, cf_yj=cf_yj,
                    cf_jg=cf_jg, dq_mc=dq_mc, xq_url=response.url, cf_cfmc=docTitle,
                    ws_nr_txt=ws_nr_txt, fb_rq=publishDate, sf=docSource, cf_xzjg=listTwoItem,
                )
                fourth_item = {**p_item, **base_data, **self.base_item}
                # print(f'DIV下P标签:{fourth_item}')
                yield fourth_item

        # 图片表格
        elif img_url_list:
            for img in img_url_list:
                img_url = 'http://www.cbirc.gov.cn' + img
                img_item = dict(
                    cf_cfmc=docTitle, fb_rq=publishDate, img_url=img_url,
                    sf=docSource, ws_nr_txt=docClob, xq_url=response.url,
                    cf_xzjg=listTwoItem,
                )
                first_item = {**img_item, **base_data, **self.base_item}
                # print(f'图片表格:{first_item}')
                yield first_item

        # 解析只有P或者p的数据，没有HTML
        elif docClob.startswith('<P') or docClob.startswith('<p') or docClob.startswith('<font') or docClob.startswith('<span') or docClob.startswith('&nbsp;') or docClob.startswith('<head') or docClob.startswith('<br') or docClob.startswith('<div') or docClob.startswith('<FONT') or docClob.startswith('<a') or docClob.startswith('<?xml') or docClob.startswith('<block') or docClob.startswith('<DIV') or docClob.startswith('<A') or docClob.startswith('<b') or docClob.startswith('</a>') or docClob.startswith('<strong') or docClob.startswith('<table') or docClob.startswith('<SPAN') or docClob.endswith('<br />') or docClob.endswith('</p>') or docClob.endswith('日') or docClob.endswith('。') or docClob.endswith('<br>'):
            ws_nr_content = remove_tags(docClob)
            if not ws_nr_content:
                ws_nr_content = ''
            else:
                ws_nr_content = reduce(lambda x, y: x+y, [re_com.sub('', i) for i in ws_nr_content])
            ws_nr_txt = ws_nr_content.replace('&nbsp;', '')
            dq_mc = dq_mc.search(ws_nr_txt)
            dq_mc = dq_mc.group(2) if dq_mc else ''
            oname = get_oname(ws_nr_txt)
            cf_wsh = cf_wsh if cf_wsh else get_cf_wsh(ws_nr_txt)
            cf_sy = get_cf_sy(ws_nr_txt)
            cf_yj = get_cf_yj(ws_nr_txt)
            cf_jg = get_cf_jg(ws_nr_txt)
            p_item = dict(
                oname=oname, cf_wsh=cf_wsh, cf_sy=cf_sy, cf_yj=cf_yj,
                cf_jg=cf_jg, dq_mc=dq_mc, xq_url=response.url, cf_cfmc=docTitle,
                ws_nr_txt=ws_nr_txt, fb_rq=publishDate, sf=docSource, cf_xzjg=listTwoItem,
            )
            third_item = {**p_item, **base_data, **self.base_item}
            # print(f'P标签数据:{third_item}')
            yield third_item

        else:
            logger.info(f'还有其他格式的内容需要解析:{docClob}--url:{response.url}')