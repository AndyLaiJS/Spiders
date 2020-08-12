# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

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

class TaikooSpider(scrapy.Spider):
    name = 'taikoo'
    # allowed_domains = ['https://www.taikooplace.com/en/whatson']
    start_urls = ['http://www.taikooplace.com/en/whatson']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        string = string.replace("\\r", " ")
        string = string.replace("\\xa0", " ")
        return string

    def parse(self, response):
        urls = response.xpath("//*[@id='mainform']/div[5]/div/div[4]/div[1]/div/a/@href").extract()
        for url in urls:
            link = "http://www.taikooplace.com" + url
            yield scrapy.Request(link, callback=self.parse_events)

    def parse_events(self, response):
        name = response.xpath("//*[@id='mainform']/div[5]//h1//text()").extract()
        description = response.xpath("//*[@id='mainform']//div[@class='event-detail__copy body-copy']//text()").extract()
        location = ""
        fee = ""
        start_date = ""
        end_date = ""
        for i in range(len(description)):
            description[i] = self.cleanText(description[i]).strip()
                
        data_cluster = response.xpath("//*[@id='mainform']/div[5]/div/div[2]/div/div[1]/div/div/div/text()").extract()
        
        if (len(data_cluster) != 0):
            if "Free" in data_cluster[0]:
                fee = data_cluster[0]
            else:
                if (len(data_cluster) == 2):
                    location = data_cluster[0]
                    fee = data_cluster[1]
                if (len(data_cluster) == 1):
                    location = data_cluster[0]
                    fee = ""
        
        combined_desc = ""
        for word in description:
            combined_desc += word

        # description = self.cleanText(description)
        data["event_name_eng"] = name[0]
        data["description_eng"] = combined_desc
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["location_eng"] = location
        data["fee"] = fee
        data["link_eng"] = response.url

        req1 = scrapy.Request(response.url.replace('/en/', '/zh-hk/'), callback=self.parse_cn, meta=data)
        yield req1

    def parse_cn(self, response):
        data = response.meta

        name_chi = response.xpath("//*[@id='mainform']/div[5]//h1//text()").extract()
        description_chi = response.xpath("//*[@id='mainform']//div[@class='event-detail__copy body-copy']//text()").extract()

        for i in range(len(description_chi)):
            description_chi[i] = self.cleanText(description_chi[i]).strip()
                
        data_cluster = response.xpath("//*[@id='mainform']/div[5]/div/div[2]/div/div[1]/div/div/div/text()").extract()
        
        location_chi = ""
        if (len(data_cluster) != 0):
            if "Free" in data_cluster[0]:
                # copy pasted from above, does absolutely nothing here but as a buffer. Kept it cause it's still working perfectly fine
                fee = data_cluster[0] 
            else:
                if (len(data_cluster) == 2):
                    location_chi = data_cluster[0]
                if (len(data_cluster) == 1):
                    location_chi = data_cluster[0]

        combined_desc = ""
        for word in description_chi:
            combined_desc += word
            
        data["event_name_chi"] = name_chi[0]
        data["description_chi"] = combined_desc
        data["location_chi"] = location_chi
        data["event_type_chi"] = ""
        data["event_type_eng"] = ""
        data["organiser_chi"] = ""
        data["organiser_eng"] = ""
        data["source"] = "Tai Koo Place"
        data["link_chi"] = response.url
        del data["depth"]
        del data["download_timeout"]
        del data["download_slot"]
        del data["download_latency"]
        
        yield data
