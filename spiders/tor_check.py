# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime

class JobsdbNotcrawlSpider(scrapy.Spider):
    name = 'tor_check'
    start_urls = ['https://check.torproject.org/']

    def parse(self, response):
        logging.info("Check tor page:" + str(response.css('.content h1::text')))