# -*- coding: utf-8 -*-
import re
import logging
from functools import reduce
from urllib.parse import urljoin

import scrapy

from bank_spider.config import hk_custom_settings
from bank_spider.work_utils.change_font import TraditionalToSimplified
from bank_spider.work_utils.clean_hk import get_cf_sy, get_cf_yj, get_cf_jg

logger = logging.getLogger(__name__)


class HkSfcSpider(scrapy.Spider):
    name = 'hk_sfc'
    allowed_domains = ['sfc.hk']
    custom_settings = hk_custom_settings

    base_item = {
        'sj_type': '15',
        'xxly': '香港-证券及期货事务监察委员会-执法消息',
        'site_id': 38701,
    }

    def start_requests(self):
        for year in range(1997, 2021):
            url = 'https://www.sfc.hk/edistributionWeb/gateway/TC/news-and-announcements/news/enforcement-news/?year={}&page=1'.format(year)
            yield scrapy.Request(url=url)

    def parse(self, response):
        """ 解析列表页+列表页翻页+请求详情页 """
        selector = scrapy.Selector(text=response.text)
        # 列表数据解析
        base_table = selector.css('table[class=datagrid] tr:not(:first-child)')
        # base_table = selector.xpath('//table[@class="datagrid"]/tr[position()>1]')
        for data in base_table:
            fb_rq = data.css('td:first-child::text').get('').strip()
            oname = data.xpath('string(./td[2])').get('').replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '').strip()
            cf_cfmc = data.xpath('string(./td[last()])').get('').replace(' ', '').strip()
            first_item = dict(oname=TraditionalToSimplified(oname), fb_rq=fb_rq, cf_cfmc=TraditionalToSimplified(cf_cfmc))
            xq_url = data.xpath('./td[last()]/a/@href').get('')
            url = urljoin(response.url, xq_url)  # 详情页url
            yield scrapy.Request(url=url, callback=self.parse_detail, meta={'first_item': first_item}, priority=5)
        # 列表翻页
        next_url = selector.css('a[class=next]::attr(href)').get('')
        if next_url:
            url = urljoin(response.url, next_url)
            yield scrapy.Request(url=url, priority=3)

    def parse_detail(self, response):
        """ 解析详情页 """
        re_com = re.compile(r'\r|\n|\t|\s')
        first_item = response.meta.get('first_item')
        selector = scrapy.Selector(text=response.text)
        # 详情页解析
        cf_jdrq = selector.xpath('//div[@id="content"]/div[3]/p/small/text()').get('').strip()
        content_list = selector.xpath('//div[@id="content"]//text()').getall()
        ws_nr_txt = reduce(lambda x, y: x + y, [re_com.sub('', i) for i in content_list])
        ws_nr_txt = TraditionalToSimplified(ws_nr_txt)
        cf_sy = get_cf_sy(ws_nr_txt)
        cf_yj = get_cf_yj(ws_nr_txt)
        cf_jg = get_cf_jg(ws_nr_txt)
        second_item = dict(
            cf_jdrq=cf_jdrq, cf_sy=cf_sy, cf_yj=cf_yj, cf_jg=cf_jg,
            xq_url=response.url, ws_nr_txt=ws_nr_txt,
        )
        item = {**first_item, **second_item, **self.base_item}
        yield item