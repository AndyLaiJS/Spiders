# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
import pymongo

data = {}

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
        names = response.xpath("//*[@id='main']/div[4]/section/div/ul//h4/a/text()").extract()
        desc = response.xpath("//*[@id='main']/div[4]/section/div/ul/li/div/div[2]/p[2]").extract()
        links = response.xpath("//*[@id='main']/div[4]/section/div/ul//h4/a/@href").extract()

        for i in range(len(names)):
            # Clean the text
            names[i] = " ".join(names[i].split())
            # data["event_name_eng"] = list_of_names[i]

        for i in range(len(desc)):
            desc[i] = re.sub("</?[^>]*>", "", desc[i])
            # data["description_end"] = word

        print(len(names), len(desc), len(links))
        print("\n\n\n\n\n\n\n\n")
        for i in range(len(links)):
            # data["link_eng"] = url
            data["event_name_eng"] = names[i]
            data["description_end"] = desc[i]
            yield scrapy.Request(links[i], callback=self.parse_events)
        # data.clear()

    def parse_events(self, response):
        location = response.xpath("//*[@id='main']/section[1]/aside/div/dl[dt/text()='Venue']/dd").extract()
        dates = response.xpath("//*[@id='main']/section[1]/aside/div/dl[dt/text()='Date']/dd").extract()
        location = self.cleanText(location)
        dates = self.cleanText(dates)
        if (dates != ""):
            dates = dates.split(" to ")
            start_date = datetime.strptime(str(dates[0]), "%d.%m.%Y")
            end_date = datetime.strptime(str(dates[1]), "%d.%m.%Y")
        else:
            start_date = ""
            end_date = ""
        data["link_eng"] = response.url
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["location_eng"] = location
        client = pymongo.MongoClient('127.0.0.1', 27017)
        db = client.event_crawlers
        collection = db.events
        collection.insert(data)
        data.clear()
        pass

# event_name_chi
# event_name_eng √ 
# start_date √
# end_date √
# description_chi
# description_eng √ 
# event_type_chi
# event_type_eng 
# location_chi
# location_eng √
# fee
# organiser_chi
# organiser_eng
# source √
# link_chi
# link_eng √