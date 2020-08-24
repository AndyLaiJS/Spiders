import pymongo
import scrapy
from datetime import datetime
#client = pymongo.MongoClient('127.0.0.1', 27017)
#db = client.event_crawlers
#collection = db.pmq

list_of_categories = [['date'],
                     ['event_type_eng', 'back to monthly calendar'],
                     ['event_type_chi', '返回查看活動一覧'],
                     ['location_eng', 'venue'],
                     ['location_chi', '場地'],
                     ['fee', 'fee (hkd)'],
                     ['organiser_eng', 'presented & organized'],
                     ['organiser_chi', '主辦']]

links = []

class HKTBSpider(scrapy.Spider):
    
    name = 'PMQ'
    start_urls = ['https://www.pmq.org.hk/happenings/programmes-events/?lang=ch&past=1&date=']
    
    def cleanText(self, list_of_data):
        for i in range(len(list_of_data)):
            list_of_data[i] = list_of_data[i].replace('  ', ' ')
            list_of_data[i] = list_of_data[i].replace('  ', '')
            list_of_data[i] = list_of_data[i].replace('\n', '')
            if len(list_of_data[i]) > 0 and list_of_data[i][0] == ' ':
                list_of_data[i] = list_of_data[i][1:]
        list_of_data = [i for i in list_of_data if i != '' and i != ' ']
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
            'source': 'PMQ',
            'link_chi': 'N/A',
            'link_eng': 'N/A',
        }

        new_data['fetch_date'] = datetime.now()
        new_data['link_chi'] = response.url
        new_data['description_chi'] = event_description

        list_of_data_lower = []
        for i in list_of_data:
            list_of_data_lower.append(i.lower())

        for i in list_of_categories:
            for j in i:
                if list_of_data_lower.count(j) > 0:
                    if j == '返回查看活動一覧' and list_of_data[list_of_data_lower.index(j) + 2] == '日期':
                        new_data['event_name_chi'] = list_of_data[list_of_data_lower.index(j) + 1]
                    else:
                        if j == '返回查看活動一覧':
                            new_data['event_name_chi'] = list_of_data[list_of_data_lower.index(j) + 2]
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]
        
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
                        if date.count('–') > 0 or date.count('to') > 0:
                            if date.count('–') > 0:
                                start_date = date[:date.index('–')]
                                end_date = date[date.index('–') + 1:]
                            else:
                                start_date = date[:date.index('to')]
                                end_date = date[date.index('to') + 2:]
                            if start_date[0] == ' ':
                                start_date = start_date[1:]
                            if start_date[-1] == ' ':
                                start_date = start_date[:-1]
                            if end_date[0] == ' ':
                                end_date = end_date[1:]
                            if end_date[-1] == ' ':
                                end_date = end_date[:-1]
                        else:
                            start_date = date
                            end_date = date

                        temp = start_date.lower()
                        if temp.count('now') > 0:
                            new_data['start_date'] = datetime.now()
                        else:
                            if start_date.count('(') > 0:
                                start_date = start_date[:start_date.index('(') - 1]
                                if start_date[-1] == ' ':
                                    start_date = start_date[:-1]
                            else:
                                start_date = '1 ' + start_date
                            try:
                                new_data['start_date'] = datetime.strptime(start_date, "%d %b %Y")
                            except:
                                new_data['start_date'] = datetime.strptime(start_date, "%d %B %Y")

                        temp = end_date.lower()
                        if temp.count('now') > 0 or temp.count('onward') > 0:
                            new_data['end_date'] = ''
                        else:
                            if end_date.count('(') > 0:
                                end_date = end_date[:end_date.index('(') - 1]
                            else:
                                temp_mon = end_date.split()[0][:3].lower()
                                month_num = {
                                    'jan': '31',
                                    'feb': '28',
                                    'mar': '31',
                                    'apr': '30',
                                    'may': '31',
                                    'jun': '30',
                                    'jul': '31',
                                    'aug': '31',
                                    'sep': '30',
                                    'oct': '31',
                                    'nov': '30',
                                    'dec': '31'
                                }
                                end_date = month_num[temp_mon] + ' ' + end_date
                            try:
                                new_data['end_date'] = datetime.strptime(end_date, "%d %b %Y")
                            except:
                                new_data['end_date'] = datetime.strptime(end_date, "%d %B %Y")

                    elif j == 'back to monthly calendar' and list_of_data[list_of_data_lower.index(j) + 2] == 'DATE':
                        new_data['event_name_eng'] = list_of_data[list_of_data_lower.index(j) + 1]
                    else:
                        if j == 'back to monthly calendar':
                            new_data['event_name_eng'] = list_of_data[list_of_data_lower.index(j) + 2]
                        new_data[i[0]] = list_of_data[list_of_data_lower.index(j) + 1]

        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        #collection.insert(new_data)
        yield new_data
