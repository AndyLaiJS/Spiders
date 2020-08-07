import pymongo
import scrapy
client = pymongo.MongoClient('127.0.0.1', 27017)
db = client.event_crawlers
collection = db.pmq
list_of_categories = [['date'],
                     ['event_type_eng', 'back to monthly calendar'],
                     ['event_type_chi', '返回查看活動一覧'],
                     ['location_eng', 'venue'],
                     ['location_chi', '場地'],
                     ['fee', 'fee (hkd)'],
                     ['organiser_eng', 'presented & organized'],
                     ['organiser_chi', '主辦']]
links = []
class PMQSpider(scrapy.Spider):
    name = 'PMQ'
    start_urls = ['https://www.pmq.org.hk/happenings/programmes-events/?lang=ch&past=1&date=']
    def cleanText(self, list_of_data):
        for i in range(len(list_of_data)):
            list_of_data[i] = list_of_data[i].replace('  ', '')
            list_of_data[i] = list_of_data[i].replace('\n', '')
            if len(list_of_data[i]) > 0 and list_of_data[i][0] == ' ':
                list_of_data[i] = list_of_data[i][1:]
        list_of_data = [i for i in list_of_data if i != '']
        return list_of_data
    def parse(self, response):
        for i in range(202001, 202013):
            yield scrapy.Request(response.url + str(i), callback=self.parse_links)
    def parse_links(self, response):
        global links
        urls_temp = response.xpath("//*[@class='bgWhite container gapPaddingBtm40 gapBtm40']/*[@class='col-xs-6']/a/@href").extract()
        urls = urls_temp[::2]
        for url in urls:
            links.append(url)
            yield scrapy.Request(url, callback=self.parse_events)
    def parse_events(self, response):
        list_of_data = response.xpath('//*[@class="container"]//text()').extract()
        list_of_data = self.cleanText(list_of_data)
        list_description = response.xpath('//*[@class="container"]//*[@class="field2 pull-left gapPadding20 size18"]//p//text()').extract()
        list_description = self.cleanText(list_description)
        event_description = list_description[0]
        i = 1
        list_description_length = len(list_description)
        while i < list_description_length and list_description[i] != '有關 ':
            event_description = event_description + '\n' + list_description[i]
            i += 1
        #print(list_of_data)
        new_data = {
            'event_name_chi': '',
            'event_name_eng': '',
            'start_date': '',
            'end_date': '',
            'description_chi': '',
            'description_eng': '',
            'event_type_chi': '',
            'event_type_eng': '',
            'location_chi': 'N/A',
            'location_eng': 'N/A',
            'fee': 'N/A',
            'organiser_chi': 'N/A',
            'organiser_eng': 'N/A',
            'source': 'PMQ',
            'link_chi': '',
            'link_eng': '',
        }
        new_data['link_chi'] = response.url
        new_data['description_chi'] = event_description
        list_of_data_lower = []
        for i in list_of_data:
            list_of_data_lower.append(i.lower())
        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    if j == 'date':
                        date = list_of_data[list_of_data_lower.index(j) + 1]
                        if date.count('–') > 0:
                            new_data['start_date'] = date[:date.index('–') - 1]
                            new_data['end_date'] = date[date.index('–') + 2:]
                        else:
                            new_data['start_date'] = date
                            new_data['end_date'] = date
                    else:
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]
                    if j == '返回查看活動一覧':
                        new_data['event_name_chi'] = list_of_data[list_of_data_lower.index(j) + 2]
        yield scrapy.Request(response.url.replace('?lang=ch', '?lang=en'), callback=self.parse_events_en, meta=new_data)
    def parse_events_en(self, response):
        new_data = response.meta
        list_of_data = response.xpath('//*[@class="container"]//text()').extract()
        list_of_data = self.cleanText(list_of_data)
        list_description = response.xpath('//*[@class="container"]//*[@class="field2 pull-left gapPadding20 size18"]//p//text()').extract()
        list_description = self.cleanText(list_description)
        event_description = list_description[0]
        i = 1
        list_description_length = len(list_description)
        while i < list_description_length and list_description[i] != 'Know more about ':
            event_description = event_description + '\n' + list_description[i]
            i += 1
        new_data['link_eng'] = response.url
        new_data['description_eng'] = event_description
        list_of_data_lower = []
        for i in list_of_data:
            list_of_data_lower.append(i.lower())
        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    if j == 'date':
                        date = list_of_data[list_of_data_lower.index(j) + 1]
                        if date.count('–') > 0:
                            new_data['start_date'] = date[:date.index('–') - 1]
                            new_data['end_date'] = date[date.index('–') + 2:]
                        else:
                            new_data['start_date'] = date
                            new_data['end_date'] = date
                    else:
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]
                    if j == 'back to monthly calendar':
                        new_data['event_name_eng'] = list_of_data[list_of_data_lower.index(j) + 2]
        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        collection.insert(new_data)