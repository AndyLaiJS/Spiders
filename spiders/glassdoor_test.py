# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

z = []
class JobsdbNotcrawlSpider(CrawlSpider):
    name = 'glassdoor_test'
    allowed_domains = ['glassdoor.com.hk']
    start_urls = ['https://www.glassdoor.com.hk']
    rules = (
        Rule(LinkExtractor(allow=('Job/', )),
             callback='parse_item'),
    )

    def parse_item(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        global z
        z.append(response.url)
        print(len(z))