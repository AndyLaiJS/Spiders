# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re
from scrapy.http import HtmlResponse

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

class TaikwunSpider(scrapy.Spider):
    name = 'taikwun'
    # allowed_domains = ['https://www.taikwun.hk/en/programme']
    start_urls = ['https://www.taikwun.hk/en/programme/']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        string = string.replace("\\xa0", " ")
        string = string.replace("\\r", " ")
        string = string.replace("&amp", "")
        return string

    def parse(self, response):
        links = response.xpath("//*[@id='programme-list']/div[@class='container']/div/div/div/div//a/@href").extract()
        for url in links:
            url = "https://www.taikwun.hk/en/" + url
            print(url)
            yield scrapy.Request(url, callback=self.parse_events)

    def parse_events(self, response):
        name = response.xpath("//*[@id='programme-content']/div[2]/section[1]/div/div/div[1]/span/text()").extract_first()
        if (name == None):
            name = response.xpath("//*[@class='page-title-section container ']/div/span/text()").extract_first()
        dates = response.xpath("//*[@id='programme-content']/div[1]/div/div[1]/div[1]/div/div[2]/div[1]/label/text()").extract()
        location = response.xpath("//*[@id='programme-content']/div[1]/div/div[1]/div[2]/div/div[2]/div[1]/text()").extract()
        fee = response.xpath("//*[@id='programme-content']/div[1]/div/div[1]/div[3]/div/div[2]/div[1]/text()").extract()
        desc = response.xpath("//*[@id='programme-content']/div[2]/section/div/article[1]/div[2]").extract()

        if (len(dates) == 0):
            dates = ""
            start_date = ""
            end_date = ""
        else:
            dates = [dates[0]]
            dates = self.cleanText(str(dates))
            dates = dates.split(" - ")
            if (len(dates) != 1):
                # handle 17 Jun - 28 Jun, 2020
                if (len(dates[0].split()) == 2):
                    start_date = dates[0] + " " + dates[1][-4:]
                # handle like 5 - 26 Aug, 2020
                elif (len(dates[0].split()) == 1):
                    start_date = dates[0] + " " + dates[1].split()[1] + " " + dates[1][-4:]
                    start_date = start_date.replace(",", "")
                else:
                    start_date = dates[0].replace(",", "")
                end_date = dates[1].replace(",", "")
            else:
                start_date = dates[0].replace(",", "")
                end_date = ""
            if (start_date != "" and end_date != ""):
                start_date = datetime.strptime(start_date, "%d %b %Y")
                end_date = datetime.strptime(end_date, "%d %b %Y")
        
        desc = self.cleanText(desc)
        location = [location[0]] 
        fee = [fee[0]]
        location = self.cleanText(str(location))
        fee = self.cleanText(str(fee))
        
        data["event_name_eng"] = name
        data["description_eng"] = desc
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["fetch_date"] = datetime.now()
        data["location_eng"] = location
        data["fee"] = fee
        data["link_eng"] = response.url

        req1 = scrapy.Request(response.url.replace('/en/', '/zh/'), callback=self.parse_cn, meta=data)
        yield req1

    def parse_cn(self, response):
        data = response.meta

        name_chi = response.xpath("//*[@id='programme-content']/div[2]/section[1]/div/div/div[1]/span/text()").extract()
        if (len(name_chi) == 0):
            name_chi = response.xpath("//*[@class='page-title-section container ']/div/span/text()").extract()
        description_chi = response.xpath("//*[@id='programme-content']/div[2]/section/div/article[1]/div[2]").extract()
        location_chi = response.xpath("//*[@id='programme-content']/div[1]/div/div[1]/div[2]/div/div[2]/div[1]/text()").extract()
        location_chi = [location_chi[0]]
        description_chi = self.cleanText(description_chi)
        location_chi = self.cleanText(str(location_chi))
        data["event_name_chi"] = name_chi[0]
        data["description_chi"] = description_chi
        data["location_chi"] = location_chi
        data["event_type_chi"] = ""
        data["event_type_eng"] = ""
        data["organiser_chi"] = ""
        data["organiser_eng"] = ""
        data["source"] = "Tai Kwun"
        data["link_chi"] = response.url
        del data["depth"]
        del data["download_timeout"]
        del data["download_slot"]
        del data["download_latency"]
        
        yield data
