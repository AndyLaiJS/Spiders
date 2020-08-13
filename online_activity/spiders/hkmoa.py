# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

data = {
    'event_name_chi': '',
    'event_name_eng': '',
    'start_date': '',
    'end_date': '',
    'fetch_date': '',
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

class HkmoaSpider(scrapy.Spider):
    name = 'hkmoa'
    # allowed_domains = ['https://hk.art.museum/en_US/web/ma/exhibitions-and-events.html']
    start_urls = ['http://hk.art.museum/en_US/web/ma/exhibitions-and-events.html']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        return string

    def parse(self, response):
        urls = response.xpath("//*[@class='journal-content-article']/div[2]/div/div[2]/ul/li/div/a/@href").extract()
        for url in urls:
            link = "http://hk.art.museum/en_US/web/ma/" + url
            yield scrapy.Request(link, callback=self.parse_events)

    def parse_events(self, response):
        name = response.xpath("//*[@id='single-exhibition-hero-banner']/div[1]/h1/text()").extract_first()
        description = response.xpath("//*[@id='single-exhibition-content']/div[1]/div/div[2]/div/p").extract_first()
        data_clusters = response.xpath("//*[@id='single-exhibition-content']/div/div/div[3]/ul//div").extract()
        date = ""
        location = ""
        fee = ""
        description = self.cleanText(description)

        # Clean up these data clusters
        for i in range(len(data_clusters)):
            data_clusters[i] = self.cleanText(data_clusters[i]).strip()

        for i in range(len(data_clusters)):
            if "Date" in data_clusters[i]:
                date = data_clusters[i+1]

            if "Venue" in data_clusters[i]:
                location = data_clusters[i+1]

            if "Fee" in data_clusters[i]:
                fee = data_clusters[i+1]

        # To handle the dates. It's always the dates
        if "From" in date:
            start_date = date.split()[1]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = ""
        elif "Until" in date:
            start_date = datetime.now()
            end_date = date.split()[1]
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        elif date != "":
            dates = date.split(" – ")
            start_date = dates[0]
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = dates[1]
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            start_date = ""
            end_date = "" 

        data["event_name_eng"] = name
        data["description_eng"] = description
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["fetch_date"] = datetime.now()
        data["location_eng"] = location
        data["fee"] = fee
        data["link_eng"] = response.url

        req1 = scrapy.Request(response.url.replace('/en_US/', '/zh_TW/'), callback=self.parse_cn, meta=data)
        yield req1

    def parse_cn(self, response):
        data = response.meta

        name_chi = response.xpath("//*[@id='single-exhibition-hero-banner']/div[1]/h1/text()").extract_first()
        description_chi = response.xpath("//*[@id='single-exhibition-content']/div[1]/div/div[2]/div/p").extract_first()
        description_chi = self.cleanText(description_chi)

        data_clusters = response.xpath("//*[@id='single-exhibition-content']/div/div/div[3]/ul//div").extract()
        location_chi = ""

        # Clean up these data clusters
        for i in range(len(data_clusters)):
            data_clusters[i] = self.cleanText(data_clusters[i]).strip()

        for i in range(len(data_clusters)):
            if "地點" in data_clusters[i]:
                location_chi = data_clusters[i+1]
        
        data["event_name_chi"] = name_chi
        data["description_chi"] = description_chi
        data["location_chi"] = location_chi
        data["event_type_chi"] = ""
        data["event_type_eng"] = ""
        data["organiser_chi"] = ""
        data["organiser_eng"] = ""
        data["source"] = "Hong Kong Museum of Arts"
        data["link_chi"] = response.url
        del data["depth"]
        del data["download_timeout"]
        del data["download_slot"]
        del data["download_latency"]
        
        yield data
