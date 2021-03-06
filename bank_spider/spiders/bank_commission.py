# -*- coding: utf-8 -*-
import json
import re
from functools import reduce

import scrapy
from w3lib.html import remove_tags

from bank_spider.config import bank_custom_settings
from bank_spider.work_utils.clean_bank import get_oname, get_cf_sy, get_cf_yj, get_cf_jg, get_cf_jdrq, handles_cf_jdrq


class BankCommissionSpider(scrapy.Spider):
    name = 'bank_commission'
    allowed_domains = ['cbirc.gov.cn']
    custom_settings = bank_custom_settings
    base_item = {
        'sj_type': '43',
        'xxly': '中国银行保险监督管理委员会-行政处罚-总站-代码采集',
        'site_id': 39224,
    }

    def start_requests(self):
        """ 爬虫入口 """
        data_list = [4113, 4114, 4115]
        for item_id in data_list:
            start_url = 'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectDocByItemIdAndChild/data_itemId={},pageIndex=1,pageSize=18.json'.format(item_id)
            yield scrapy.Request(url=start_url, meta={'item_id': item_id}, dont_filter=True)

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
            itemName = row.get('itemName', '')  # 处罚类别
            docTitle = row.get('docTitle', '').replace('\r', '').replace('\n', '').replace('\t', '').strip()  # 标题
            publishDate = row.get('publishDate')  # 发布日期
            publishDate = publishDate[:10] if publishDate else None
            docId = row.get('docId')  # 详情页参数
            xq_url = 'http://www.cbirc.gov.cn/cn/static/data/DocInfo/SelectByDocId/data_docId={}.json'.format(docId)
            doc_url = 'http://www.cbirc.gov.cn' + docFileUrl if docFileUrl else ''
            pdf_url = 'http://www.cbirc.gov.cn' + pdfFileUrl if pdfFileUrl else ''
            meta_data = {'cf_cfmc': docTitle, 'fb_rq': publishDate, 'cf_type': itemName, 'bz': str({'doc_url': doc_url, 'pdf_url': pdf_url})}
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
            item_id = response.meta.get("item_id")
            if pages > 1:
                for page in range(2, pages + 1):
                    url = 'http://www.cbirc.gov.cn/cbircweb/DocInfo/SelectDocByItemIdAndChild?itemId={}&pageSize=18&pageIndex={}'.format(
                        item_id, page)
                    yield scrapy.Request(url=url, meta={'is_first': False, 'item_id': item_id}, priority=3)

    def parse_details(self, response):
        """ 解析详情页 """
        re_com = re.compile(r'\r|\n|\t|\s')
        base_data = response.meta.get('item')
        # 详情页解析
        results = json.loads(response.body.decode('utf-8'))
        base_item = results.get('data')
        docSource = base_item.get('docSource')  # 省份
        listTwoItem = base_item.get('listTwoItem')[0].get('ItemLvs')[-1].get('itemName')  # 处罚机关
        docTitle = base_item.get('docTitle')  # 标题
        cf_wsh = self.get_cfwsh_cfmc(docTitle).strip()
        docClob = base_item.get('docClob').strip()  # 网页源码
        selector = scrapy.Selector(text=docClob)
        # 解析table tr结构
        first_table = selector.css('table[class=MsoNormalTable]')
        second_table = selector.xpath('//table[@align="center"]')
        third_table = selector.css('table[class=MsoTableGrid]')
        # 解析div p结构
        # second_div = selector.xpath('//div[@class="Section1"]//text()')
        # third_div = selector.xpath('//div[@class="Section0"]//text()')
        # 解析table结构的数据
        if docClob:
            if first_table:
                for data in first_table:
                    base = data.xpath('./tr').getall()
                    if len(base) == 7:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = ''
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 8:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        cf_yj = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_jg = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_xzjg = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 9:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 10:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        oname_third = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_third = self.handle_data(oname_third)
                        pname = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        if oname_first:
                            oname = oname_first
                        elif oname_second:
                            oname = oname_second
                        else:
                            oname = oname_third
                    elif len(base) == 11:
                        cf_wsh = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 12:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 13 or len(base) == 14 or len(base) == 15:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()-1]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first

                    elif len(base) == 1 or len(base) == 2:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        cf_wsh = re.search(r'处罚决定书文号(.*?罚.*?\d{4}.*?\d+号)', ws_nr_txt)
                        cf_wsh = cf_wsh.group(1) if cf_wsh else ''
                        oname = re.search(r'被处罚人姓名或名称(.*?)法定代表人姓名', ws_nr_txt)
                        oname = oname.group(1) if oname else ''
                        pname = re.search(r'法定代表人姓名(.*?)主要违法事实', ws_nr_txt)
                        pname = pname.group(1) if pname else ''
                        cf_sy = re.search(r'主要违法事实(.*?)行政处罚依据', ws_nr_txt)
                        cf_sy = cf_sy.group(1) if cf_sy else ''
                        cf_yj = re.search(r'行政处罚依据(.*?)行政处罚种类', ws_nr_txt)
                        cf_yj = cf_yj.group(1) if cf_yj else ''
                        cf_jg = re.search(r'行政处罚种类(.*?)行政处罚履行方式和期限', ws_nr_txt)
                        cf_jg = cf_jg.group(1) if cf_jg else ''
                        cf_xzjg = re.search(r'作出处罚的机关(.*?)作出处罚的日期', ws_nr_txt)
                        cf_xzjg = cf_xzjg.group(1) if cf_xzjg else ''
                        cf_jdrq = re.search(r'作出处罚的日期(.*?年.*?月.*?日)', ws_nr_txt)
                        cf_jdrq = cf_jdrq.group(1) if cf_jdrq else ''
                    elif len(base) == 0:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        oname = get_oname(ws_nr_txt)
                        cf_sy = get_cf_sy(ws_nr_txt)
                        cf_yj = get_cf_yj(ws_nr_txt)
                        cf_jg = get_cf_jg(ws_nr_txt)
                        cf_jdrq = get_cf_jdrq(ws_nr_txt)
                        cf_jdrq = handles_cf_jdrq(cf_jdrq)
                        pname = ''
                        cf_xzjg = listTwoItem
                    elif len(base) == 5:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = listTwoItem
                        oname = oname_second if oname_second else oname_first
                        cf_jdrq = None
                    elif len(base) == 3:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    else:
                        oname = ''
                        pname = ''
                        cf_sy = ''
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = ''
                        cf_jdrq = ''
                        print(f'还有其他格式表格--{response.url}------{len(base)}')
                    table_item = dict(
                        oname=self.handle_data(oname), cf_wsh=self.handle_data(cf_wsh), pname=self.handle_data(pname),
                        cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg, cf_xzjg=cf_xzjg, cf_jdrq=cf_jdrq,
                        sf=docSource, xq_url=response.url, ws_nr_txt=first_table.xpath('./tr').getall(),
                    )
                    item = {**table_item, **base_data, **self.base_item}
            elif second_table:
                for data in second_table:
                    base = data.xpath('./tr').getall()
                    if len(base) == 7:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = ''
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 8:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        cf_yj = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_jg = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_xzjg = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 9:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 10:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        oname_third = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_third = self.handle_data(oname_third)
                        pname = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        if oname_first:
                            oname = oname_first
                        elif oname_second:
                            oname = oname_second
                        else:
                            oname = oname_third
                    elif len(base) == 11:
                        cf_wsh = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 12:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 13 or len(base) == 14 or len(base) == 15:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()-1]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 1 or len(base) == 2:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        cf_wsh = re.search(r'处罚决定书文号(.*?罚.*?\d{4}.*?\d+号)', ws_nr_txt)
                        cf_wsh = cf_wsh.group(1) if cf_wsh else ''
                        oname = re.search(r'被处罚人姓名或名称(.*?)法定代表人姓名', ws_nr_txt)
                        oname = oname.group(1) if oname else ''
                        pname = re.search(r'法定代表人姓名(.*?)主要违法事实', ws_nr_txt)
                        pname = pname.group(1) if pname else ''
                        cf_sy = re.search(r'主要违法事实(.*?)行政处罚依据', ws_nr_txt)
                        cf_sy = cf_sy.group(1) if cf_sy else ''
                        cf_yj = re.search(r'行政处罚依据(.*?)行政处罚种类', ws_nr_txt)
                        cf_yj = cf_yj.group(1) if cf_yj else ''
                        cf_jg = re.search(r'行政处罚种类(.*?)行政处罚履行方式和期限', ws_nr_txt)
                        cf_jg = cf_jg.group(1) if cf_jg else ''
                        cf_xzjg = re.search(r'作出处罚的机关(.*?)作出处罚的日期', ws_nr_txt)
                        cf_xzjg = cf_xzjg.group(1) if cf_xzjg else ''
                        cf_jdrq = re.search(r'作出处罚的日期(.*?年.*?月.*?日)', ws_nr_txt)
                        cf_jdrq = cf_jdrq.group(1) if cf_jdrq else ''
                    elif len(base) == 0:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        oname = get_oname(ws_nr_txt)
                        cf_sy = get_cf_sy(ws_nr_txt)
                        cf_yj = get_cf_yj(ws_nr_txt)
                        cf_jg = get_cf_jg(ws_nr_txt)
                        cf_jdrq = get_cf_jdrq(ws_nr_txt)
                        cf_jdrq = handles_cf_jdrq(cf_jdrq)
                        pname = ''
                        cf_xzjg = listTwoItem
                    elif len(base) == 5:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = listTwoItem
                        oname = oname_second if oname_second else oname_first
                        cf_jdrq = None
                    elif len(base) == 3:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    else:
                        oname = ''
                        pname = ''
                        cf_sy = ''
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = ''
                        cf_jdrq = ''
                        print(f'还有其他格式表格--{response.url}--草泥马：{len(base)}')
                    table_item = dict(
                        oname=self.handle_data(oname), cf_wsh=self.handle_data(cf_wsh), pname=self.handle_data(pname),
                        cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg, cf_xzjg=cf_xzjg, cf_jdrq=cf_jdrq,
                        sf=docSource, xq_url=response.url, ws_nr_txt=second_table.xpath('./tr').getall(),
                    )
                    item = {**table_item, **base_data, **self.base_item}
            elif third_table:
                for data in third_table:
                    base = data.xpath('./tr').getall()
                    if len(base) == 7:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = ''
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 8:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        pname = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        cf_yj = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_jg = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_xzjg = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                    elif len(base) == 9:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 10:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        oname_third = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_third = self.handle_data(oname_third)
                        pname = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        if oname_first:
                            oname = oname_first
                        elif oname_second:
                            oname = oname_second
                        else:
                            oname = oname_third
                    elif len(base) == 11:
                        cf_wsh = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[7]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 12:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 13 or len(base) == 14 or len(base) == 15:
                        cf_wsh = data.xpath('string(./tr[4]/td[last()])').get('').strip()
                        oname_first = data.xpath('string(./tr[5]/td[last()])').get('').strip()
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[7]/td[last()])').get('').strip()
                        cf_sy = data.xpath('string(./tr[8]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = data.xpath('string(./tr[9]/td[last()])').get('').strip()  # 处罚依据
                        cf_jg = data.xpath('string(./tr[10]/td[last()])').get('').strip()  # 处罚结果
                        cf_xzjg = data.xpath('string(./tr[11]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()-1]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    elif len(base) == 1 or len(base) == 2:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        cf_wsh = re.search(r'处罚决定书文号(.*?罚.*?\d{4}.*?\d+号)', ws_nr_txt)
                        cf_wsh = cf_wsh.group(1) if cf_wsh else ''
                        oname = re.search(r'被处罚人姓名或名称(.*?)法定代表人姓名', ws_nr_txt)
                        oname = oname.group(1) if oname else ''
                        pname = re.search(r'法定代表人姓名(.*?)主要违法事实', ws_nr_txt)
                        pname = pname.group(1) if pname else ''
                        cf_sy = re.search(r'主要违法事实(.*?)行政处罚依据', ws_nr_txt)
                        cf_sy = cf_sy.group(1) if cf_sy else ''
                        cf_yj = re.search(r'行政处罚依据(.*?)行政处罚种类', ws_nr_txt)
                        cf_yj = cf_yj.group(1) if cf_yj else ''
                        cf_jg = re.search(r'行政处罚种类(.*?)行政处罚履行方式和期限', ws_nr_txt)
                        cf_jg = cf_jg.group(1) if cf_jg else ''
                        cf_xzjg = re.search(r'作出处罚的机关(.*?)作出处罚的日期', ws_nr_txt)
                        cf_xzjg = cf_xzjg.group(1) if cf_xzjg else ''
                        cf_jdrq = re.search(r'作出处罚的日期(.*?年.*?月.*?日)', ws_nr_txt)
                        cf_jdrq = cf_jdrq.group(1) if cf_jdrq else ''
                    elif len(base) == 0:
                        ws_nr_content = remove_tags(docClob)
                        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                        oname = get_oname(ws_nr_txt)
                        cf_sy = get_cf_sy(ws_nr_txt)
                        cf_yj = get_cf_yj(ws_nr_txt)
                        cf_jg = get_cf_jg(ws_nr_txt)
                        cf_jdrq = get_cf_jdrq(ws_nr_txt)
                        cf_jdrq = handles_cf_jdrq(cf_jdrq)
                        pname = ''
                        cf_xzjg = listTwoItem
                    elif len(base) == 5:
                        cf_wsh = data.xpath('string(./tr[1]/td[2])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 主体=个人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主体=企业名称
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 法人
                        cf_sy = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 处罚事由
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = listTwoItem
                        oname = oname_second if oname_second else oname_first
                        cf_jdrq = None
                    elif len(base) == 3:
                        cf_wsh = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 行政处罚决定书文号
                        oname_first = data.xpath('string(./tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_first = self.handle_data(oname_first)
                        oname_second = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[1]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        oname_second = self.handle_data(oname_second)
                        pname = data.xpath('string(./tr[2]/td[last()]/table/tr[2]/td[last()]/table/tr[2]/td[last()])').get('').strip()  # 被处罚当事人姓名
                        cf_sy = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 主要违法违规事实（案由）
                        cf_yj = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 行政处罚依据
                        cf_jg = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 行政处罚决定
                        cf_xzjg = data.xpath('string(./tr[6]/td[last()])').get('').strip()  # 处罚决定机关
                        cf_jdrq = data.xpath('string(./tr[last()]/td[last()])').get('').strip()  # 处罚决定日期
                        oname = oname_second if oname_second else oname_first
                    else:
                        oname = ''
                        pname = ''
                        cf_sy = ''
                        cf_yj = ''
                        cf_jg = ''
                        cf_xzjg = ''
                        cf_jdrq = ''
                        print(f'还有其他格式表格--{response.url}--草泥马')

                    table_item = dict(
                        oname=self.handle_data(oname), cf_wsh=self.handle_data(cf_wsh), pname=self.handle_data(pname),
                        cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg, cf_xzjg=cf_xzjg, cf_jdrq=cf_jdrq,
                        sf=docSource, xq_url=response.url, ws_nr_txt=third_table.xpath('./tr').getall(),
                    )
                    item = {**table_item, **base_data, **self.base_item}
            else:
                ws_nr_content = remove_tags(docClob)
                ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in ws_nr_content]).replace('&nbsp;', '')
                oname = get_oname(ws_nr_txt)
                cf_sy = get_cf_sy(ws_nr_txt)
                cf_yj = get_cf_yj(ws_nr_txt)
                cf_jg = get_cf_jg(ws_nr_txt)
                cf_jdrq = get_cf_jdrq(ws_nr_txt)
                cf_jdrq = handles_cf_jdrq(cf_jdrq).replace('号', '') if cf_jdrq else None
                second_item = dict(
                    oname=oname, cf_wsh=cf_wsh, cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg, sf=docSource,
                    cf_xzjg=listTwoItem, cf_jdrq=cf_jdrq, xq_url=response.url, ws_nr_txt=ws_nr_txt,
                )
                item = {**second_item, **base_data, **self.base_item}
        else:
            data = dict(xq_url=response.url)
            item = {**base_data, **self.base_item, **data}
        yield item

    @classmethod
    def get_cfwsh_cfmc(cls, txt):
        """ 从处罚名称获取文书号 """
        if txt:
            first = re.search(r'[\(（ ](.*?罚.*?\d{4}.*?\d+号)', txt)
            second = re.search(r'(行政处罚决定书.*?\d{4}.*?\d+号)', txt)
            third = re.search(r'(.*?保监罚\d{4}.*?\d+.*?号)', txt)
            four = re.search(r'(.*?保监罚.*?\d{4}.*?\d+.*?号)', txt)
            if first:
                wsh = first.group(1)
            elif second:
                wsh = second.group(1)
            elif third:
                wsh = third.group(1)
            elif four:
                wsh = four.group(1)
            else:
                wsh = ''
            return wsh
        else:
            return ''

    @classmethod
    def handle_data(cls, txt):
        """ 处理特殊符号 """
        if txt:
            txt = re.sub(r'\r|\n|\t|\s| |——|--|----|\xa0|—|/|---|-', '', txt)
            return txt
        return ''