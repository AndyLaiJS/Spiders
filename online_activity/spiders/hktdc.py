import pymongo
import scrapy
from datetime import datetime
#client = pymongo.MongoClient('127.0.0.1', 27017)
#db = client.event_crawlers
#collection = db.hktdc

list_of_categories = [['date', 'date:'],
                     ['description_eng', 'description:'], 
                     ['description_chi', '詳細資料:'],
                     ['event_type_eng', 'format:'],
                     ['event_type_chi', '形式:'],
                     ['fee', 'participation fee:'],
                     ['organiser_eng', 'organiser:'],
                     ['organiser_chi', '主辦機構:']]

class HKTBSpider(scrapy.Spider):
    
    name = 'HKTDC'
    start_urls = ['http://www.hktdc.com/info/trade-events/i/CSD/tc/客戶服務.htm?PAGE=']
    
    def cleanText(self, list_of_data):
        for i in range(len(list_of_data)):
            list_of_data[i] = list_of_data[i].replace('\n', '')
            list_of_data[i] = list_of_data[i].replace('\t', '')
            list_of_data[i] = list_of_data[i].replace('  ', '')
            if len(list_of_data[i]) > 0 and list_of_data[i][0] == ' ':
                list_of_data[i] = list_of_data[i][1:]
        list_of_data = [i for i in list_of_data if i != '' and i != ' ']
        return list_of_data

    def parse(self, response):
        for i in range(1, 4):
            yield scrapy.Request(response.url + str(i), callback=self.parse_links)

    def parse_links(self, response):

        urls = response.xpath("//*[@class='content_black_middle padding_right_5px']/a/@href").extract()
        
        for url in urls:
            if url.count('www.hktdc.com') > 0:
                yield scrapy.Request(url, callback=self.parse_events)

    def parse_events(self, response):
        
        new_data = {
            'event_name_chi': '',
            'event_name_eng': '',
            'start_date': '',
            'end_date': '',
            'fetch_date': '',
            'description_chi': 'N/A',
            'description_eng': 'N/A',
            'event_type_chi': '',
            'event_type_eng': '',
            'location_chi': '網上直播',
            'location_eng': 'Online',
            'fee': 'N/A',
            'organiser_chi': 'N/A',
            'organiser_eng': 'N/A',
            'source': 'HKTDC',
            'link_chi': '',
            'link_eng': '',
        }

        new_data['fetch_date'] = datetime.now()
        
        list_of_data = response.xpath('//*[@class="background_white_padding_middle"]//text()').extract()
        
        list_of_data = self.cleanText(list_of_data)

        new_data['event_name_chi'] = response.xpath('//font[@color="black"]/text()').extract()[0]

        #print(new_data['event_name_chi'])

        new_data['link_chi'] = response.url

        #print(list_of_data)

        list_of_data_lower = []
        for i in list_of_data:
            list_of_data_lower.append(i.lower())

        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]
        
        yield scrapy.Request(response.url.replace('/tc/', '/en/'), callback=self.parse_events_en, meta=new_data)

    def parse_events_en(self, response):
        
        new_data = response.meta
        
        list_of_data = response.xpath('//*[@class="background_white_padding_middle"]//text()').extract()
        
        list_of_data = self.cleanText(list_of_data)

        new_data['event_name_eng'] = response.xpath('//font[@color="black"]/text()').extract()[0]

        #print(new_data['event_name_eng'])

        new_data['link_eng'] = response.url

        #print(list_of_data)

        list_of_data_lower = []
        for i in list_of_data:
            list_of_data_lower.append(i.lower())

        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    if j == 'date:':
                        date = list_of_data[list_of_data_lower.index(j) + 1]
                        date = date[:date.index('(') - 1]
                        try:
                            new_data['start_date'] = datetime.strptime(date, "%d %b %Y")
                            new_data['end_date'] = datetime.strptime(date, "%d %b %Y")
                        except:
                            new_data['start_date'] = datetime.strptime(date, "%d %B %Y")
                            new_data['end_date'] = datetime.strptime(date, "%d %B %Y")
                    else:
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]

        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        #collection.insert(new_data)
        yield new_data
