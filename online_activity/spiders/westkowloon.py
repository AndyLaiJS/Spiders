# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from scrapy.http import HtmlResponse

data = {
    'event_name_chi': '',
    'event_name_eng': '',
    'start_date': '',
    'end_date': '',
    'description_chi': '',
    'description_eng': '',
    'event_type_chi': '',
    'event_type_eng': '',
    'location_chi': '',
    'location_eng': '',
    'fee': '',
    'organiser_chi': '',
    'organiser_eng': '',
    'source': '',
    'link_chi': '',
    'link_eng': '',
}

class WestkowloonSpider(scrapy.Spider):
    name = 'westkowloon'
    # allowed_domains = ['https://www.westkowloon.hk/en/']
    start_urls = ['https://www.westkowloon.hk/en/whats-on/current-forthcoming/event-type/all/']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        return string

    def parse(self, response):
        links = response.xpath("//*[@id='main']/div[4]/section/div/ul//h4/a/@href").extract()
        for i in range(len(links)):
            yield scrapy.Request(links[i], callback=self.parse_events)

    def parse_events(self, response):
        
        # TO-DO : Precaution mechanism

        name = response.xpath("//*[@id='main']/div[2]/div/header/div/h1/text()").extract()
        description = response.xpath("//*[@id='main']/section[1]/article/div/div/p[1]").extract()
        location = response.xpath("//*[@id='main']/section[1]/aside/div/dl[dt/text()='Venue']/dd").extract()
        dates = response.xpath("//*[@id='main']/section[1]/aside/div/dl[dt/text()='Date']/dd").extract()
        fee = response.xpath("//*[@id='main']/section[1]/article/div[1]/div/p[strong/text()[contains(., 'Tickets:') or contains(., 'Fee:') or contains(., 'Free')]]/text()").extract()
        description = self.cleanText(description)
        location = self.cleanText(location)
        dates = self.cleanText(dates)
        fee = self.cleanText(fee)
        
        if (dates != ""):
            dates = dates.split(" to ")
            start_date = datetime.strptime(str(dates[0]), "%d.%m.%Y")
            try:
                end_date = datetime.strptime(str(dates[1]), "%d.%m.%Y")
            except:
                end_date = ""
        else:
            start_date = ""
            end_date = ""

        data["event_name_eng"] = name[0]
        data["description_eng"] = description
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["location_eng"] = location
        data["fee"] = fee
        data["link_eng"] = response.url

        req1 = scrapy.Request(response.url.replace('/en/', '/tc/'), callback=self.parse_cn, meta=data)
        yield req1

    def parse_cn(self, response):
        data = response.meta

        name_chi = response.xpath("//*[@id='main']/div[2]/div/header/div/h1/text()").extract()
        description_chi = response.xpath("//*[@id='main']/section[1]/article/div/div/p[1]").extract()
        location_chi = response.xpath("//*[@id='main']/section[1]/aside/div/dl[dt/text()='地點']/dd").extract()
        description_chi = self.cleanText(description_chi)
        location_chi = self.cleanText(location_chi)
        data["event_name_chi"] = name_chi[0]
        data["description_chi"] = description_chi
        data["location_chi"] = location_chi
        data["event_type_chi"] = ""
        data["event_type_eng"] = ""
        data["organiser_chi"] = ""
        data["organiser_eng"] = ""
        data["source"] = ""
        data["link_chi"] = response.url
        del data["depth"]
        del data["download_timeout"]
        del data["download_slot"]
        del data["download_latency"]
        
        yield data
