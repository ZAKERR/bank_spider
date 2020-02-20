# -*- coding: utf-8 -*-
import re

import scrapy

from bank_spider.config import beijing_custom_settings


class TaxationBjSpider(scrapy.Spider):
    name = 'taxation_bj'
    allowed_domains = ['beijing.chinatax.gov.cn']
    start_urls = ['http://beijing.chinatax.gov.cn/']
    list_url = 'http://beijing.chinatax.gov.cn/bjsat/office/jsp/zdsswfaj/wwquery'
    custom_settings = beijing_custom_settings
    base_item = {
        'cf_xzjg': '国家税务总局北京市税务局',
        'sj_type': '10',
        'xxly': '国家税务总局北京市税务局-重大涉税企业名单-代码采集',
        'site_id': 39129,
    }

    def start_requests(self):
        """ 入口函数 """
        form_data = {
            "id": "",
            "dq": "null",
            "ajlx": "null",
            "ndjd": "null",
            "bz": "zh",
            "dqy": "1",  # 翻页
            "ymdx": "",
            "nsrmc": "",
            "nsrsbh": "",
            "zcdz": "",
            "zzjgdm": "",
            "fddbrmc": "",
            "fddbrsfzhm": "",
            "cwfzrmc": "",
            "cwfzrsfzhm": "",
            "orgCode": "11100000000",
        }
        yield scrapy.FormRequest(url=self.list_url, meta={'form_data': form_data}, formdata=form_data, dont_filter=True)

    def parse(self, response):
        """ 列表解析，翻页 """
        # 列表解析
        index_url = 'http://beijing.chinatax.gov.cn/bjsat/office/jsp/zdsswfaj/wwidquery'
        selector = scrapy.Selector(text=response.text)
        base_tr = selector.xpath('//table/tbody/tr/td/table[2]/tbody/tr[position()<last()]')
        for data in base_tr:
            sf = data.xpath('string(./td[1])').get('').strip()
            xq_id = data.xpath('./td[last()]/input/@onclick').re_first(r'\(\'(\d+)')
            meta_data = dict(sf=sf)
            # 请求详情页
            form_data = {
                "id": str(xq_id),
                "dq": "null",
                "ajlx": "null",
                "ndjd": "null",
                "bz": "zh",
                "dqy": "1",
                "ymdx": "",
                "nsrmc": "",
                "nsrsbh": "",
                "zcdz": "",
                "zzjgdm": "",
                "fddbrmc": "",
                "fddbrsfzhm": "",
                "cwfzrmc": "",
                "cwfzrsfzhm": "",
                "orgCode": "11100000000",
            }
            yield scrapy.FormRequest(url=index_url, formdata=form_data, meta={'item': meta_data}, callback=self.parse_detail, priority=5)
        # 列表翻页请求
        page_count = selector.xpath('//table/tbody/tr/td/table[2]/tbody/tr[last()]/td[2]//text()').re_first(r'查询结果.*?(\d+).*?页')
        is_first = response.meta.get('is_first', True)
        if is_first:
            form_data = response.meta.get('form_data')
            if int(page_count) > 1:
                for page in range(2, int(page_count) + 1):
                    form_data['dqy'] = str(page)
                    yield scrapy.FormRequest(
                        url=self.list_url,
                        formdata=form_data,
                        meta={'is_first': False, 'form_data': form_data},
                        priority=3,
                        dont_filter=True,
                    )

    def parse_detail(self, response):
        """ 解析详情页 """
        first_item = response.meta.get('item')
        selector = scrapy.Selector(text=response.text)
        # 详情解析
        base_data = selector.xpath('//table/tbody/tr/td/table/tbody')
        for data in base_data:
            oname = data.xpath('string(./tr[1]/td[last()])').get('').strip()  # 纳税人名称
            uccode = data.xpath('string(./tr[2]/td[last()])').get('').strip()  # 纳税人识别号或社会信用代码
            etcode = data.xpath('string(./tr[3]/td[last()])').get('').strip()  # 组织机构代码
            cf_r_dz = data.xpath('string(./tr[4]/td[last()])').get('').strip()  # 注册地址
            first = data.xpath('string(./tr[5]/td[last()])').get('').strip()  # 违法期间法人代表或者负责人姓名、性别及身份证号码（或其他证件号码）
            second = data.xpath('string(./tr[6]/td[last()])').get('').strip()
            third = data.xpath('string(./tr[7]/td[last()])').get('').strip()
            fourth = data.xpath('string(./tr[8]/td[last()])').get('').strip()
            bz = data.xpath('string(./tr[9]/td[last()])').get('').replace('\r', '').replace('\n', '').replace('\t', '').strip()  # 负有直接责任的中介机构信息
            cf_cfmc = data.xpath('string(./tr[10]/td[last()])').get('').replace('\r', '').replace('\n', '').replace('\t', '').strip()  # 案件性质
            contents = data.xpath('string(./tr[last()-1]/td[last()])').get('').replace('\r', '').replace('\n', '').replace('\t', '').strip()  # 事由依据结果
            if first:
                pname = re.search(r'姓名：(.*?)；', first)
                bzxr_xb = re.search(r'性别：(.*?)；', first)
                cf_r_id = re.search(r'证件号码：(\d+.*?\d+)', first)
                pname = pname.group(1) if pname else ''
                bzxr_xb = bzxr_xb.group(1) if bzxr_xb else ''
                cf_r_id = cf_r_id.group(1) if cf_r_id else ''
            elif second:
                pname = re.search(r'姓名：(.*?)；', second)
                bzxr_xb = re.search(r'性别：(.*?)；', second)
                cf_r_id = re.search(r'证件号码：(\d+.*?\d+)', second)
                pname = pname.group(1) if pname else ''
                bzxr_xb = bzxr_xb.group(1) if bzxr_xb else ''
                cf_r_id = cf_r_id.group(1) if cf_r_id else ''
            elif third:
                pname = re.search(r'姓名：(.*?)；', third)
                bzxr_xb = re.search(r'性别：(.*?)；', third)
                cf_r_id = re.search(r'证件号码：(\d+.*?\d+)', third)
                pname = pname.group(1) if pname else ''
                bzxr_xb = bzxr_xb.group(1) if bzxr_xb else ''
                cf_r_id = cf_r_id.group(1) if cf_r_id else ''
            else:
                pname = re.search(r'姓名：(.*?)；', fourth)
                bzxr_xb = re.search(r'性别：(.*?)；', fourth)
                cf_r_id = re.search(r'证件号码：(\d+.*?\d+)', fourth)
                pname = pname.group(1) if pname else ''
                bzxr_xb = bzxr_xb.group(1) if bzxr_xb else ''
                cf_r_id = cf_r_id.group(1) if cf_r_id else ''
            cf_sy = re.search(r'(.*?。)', contents)
            cf_sy = cf_sy.group(1) if cf_sy else ''
            cf_jg = re.search(r'(对其处.*?。)', contents)
            cf_jg = cf_jg.group(1) if cf_jg else ''
            cf_yj = re.search(r'(依照.*?规定)', contents)
            cf_yj = cf_yj.group(1) if cf_yj else ''

            second_item = dict(
                oname=oname, uccode=uccode, etcode=etcode, cf_r_dz=cf_r_dz,
                cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg, pname=pname,
                bzxr_xb=bzxr_xb, cf_r_id=cf_r_id, cf_cfmc=cf_cfmc,
                ws_nr_txt=contents, xq_url=response.url, bz=bz
            )
            item = {**first_item, **second_item, **self.base_item}
            yield item
