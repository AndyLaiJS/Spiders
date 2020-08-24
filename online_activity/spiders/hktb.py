import scrapy
import re
from datetime import datetime
from selenium import webdriver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import pymongo
#client = pymongo.MongoClient('127.0.0.1', 27017)
#db = client.event_crawlers
#collection = db.hktb

list_of_categories = [['date'],
                     ['event_type_eng', 'category(-ies)'],
                     ['event_type_chi', '類別'],
                     ['location_eng', 'venue'],
                     ['location_chi', '地點'],
                     ['fee', 'admission'],
                     ['organiser_eng', 'organiser'],
                     ['organiser_chi', '主辦機構']]
                     
class HKTBSpider(scrapy.Spider):
    name = 'HKTB'
    #allowed_domains = ['https://www.discoverhongkong.com/us/what-s-new/events/detail.id76393.metamorph-hong-kong-new-artist-series.html']
    start_urls = ['https://www.discoverhongkong.com/us/what-s-new/events.html']
    
    def cleanText(self, list_of_data):
        for i in range(len(list_of_data)):
            list_of_data[i] = list_of_data[i].replace('  ', '')
            list_of_data[i] = list_of_data[i].replace('\n', '')
            if len(list_of_data[i]) > 0 and list_of_data[i][0] == ' ':
                list_of_data[i] = list_of_data[i][1:]
        list_of_data = [i for i in list_of_data if i != '' and i != ' ']
        return list_of_data

    def parse(self, response):
        # urls = response.xpath("//*[@id='event-calendar']/div[2]//a/@href").extract()
        LOGGER.setLevel(logging.WARNING)
        PATH = 'C:/Users/Sun/chromedriver.exe'
        driver = webdriver.Chrome(PATH)
        driver.get(response.url)
        urls = driver.find_elements_by_xpath("//*[@id='event-calendar']/div[2]/div/div[4]/div/div/a")
        for url in urls:
            yield scrapy.Request(url.get_attribute('href'), callback=self.parse_en)

    def parse_en(self, response):

        new_data = {
            'event_name_chi': '',
            'event_name_eng': '',
            'start_date': 'N/A',
            'end_date': 'N/A',
            'fetch_date': '',
            'description_chi': 'N/A',
            'description_eng': 'N/A',
            'event_type_chi': 'N/A',
            'event_type_eng': 'N/A',
            'location_chi': 'N/A',
            'location_eng': 'N/A',
            'fee': 'N/A',
            'organiser_chi': 'N/A',
            'organiser_eng': 'N/A',
            'source': 'HKTB',
            'link_chi': 'N/A',
            'link_eng': 'N/A',
        }
        
        new_data['fetch_date'] = datetime.now()
        
        list_of_data = response.xpath('//*[@class="cmp-text"]//p//text()').extract()
        
        list_of_data = self.cleanText(list_of_data)

        new_data['event_name_eng'] = response.xpath('//title/text()').extract_first()

        new_data['link_eng'] = response.url

        new_data['description_eng'] = list_of_data[0]
        
        list_of_data_lower = []
        
        for i in list_of_data:
            list_of_data_lower.append(i.lower())
        
        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    if j == 'date':
                        date = list_of_data[list_of_data_lower.index(j) + 1]
                        if date.count('to') > 0:
                            start_date = date[:date.index('to') - 1]
                            end_date = date[date.index('to') + 3:]
                        elif date.count('–') > 0:
                            end_date = date[date.index('–') + 1:]
                            start_date = date[:date.index('–')] + ' ' + end_date.split()[1] + ' ' + end_date.split()[2]
                        else:
                            start_date = date
                            end_date = date
                        if not (start_date[-1] in '0123456789'):
                            start_date = start_date + ' ' + end_date.split()[2]
                        try:
                            new_data['start_date'] = datetime.strptime(start_date, "%d %b %Y")
                            new_data['end_date'] = datetime.strptime(end_date, "%d %b %Y")
                        except:
                            new_data['start_date'] = datetime.strptime(start_date, "%d %B %Y")
                            new_data['end_date'] = datetime.strptime(end_date, "%d %B %Y")
                    else:
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]
                        
        yield scrapy.Request(response.url.replace('/us/', '/tc/'), callback=self.parse_ch, meta=new_data)

    def parse_ch(self, response):

        new_data = response.meta
        
        list_of_data = response.xpath('//*[@class="cmp-text"]//p//text()').extract()
        
        list_of_data = self.cleanText(list_of_data)

        new_data['event_name_chi'] = response.xpath('//title/text()').extract_first()

        new_data['link_chi'] = response.url

        new_data['description_chi'] = list_of_data[0]
        
        list_of_data_lower = []
        
        for i in list_of_data:
            list_of_data_lower.append(i.lower())
        
        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]

        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        #collection.insert(new_data)
        yield new_data