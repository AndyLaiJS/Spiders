import pymongo
import scrapy
from datetime import datetime
import time
import re
#import nltk
#client = pymongo.MongoClient('127.0.0.1', 27017)
#db = client.event_crawlers
#collection = db.themills

list_of_event_type = [['Performance', '表演', 'perform', 'concert'],
                     ['Conversation', '座談會', 'talk', 'conversation'],
                     ['Workshop', '工作坊', 'workshop', 'diy'],
                     ['Exhibition', '展覽', 'collection', 'exhibition'],
                     ['Sale', '展銷會','sale'],
                     ['Class', '課程', 'class']]

unable_url = ['http://www.themills.com.hk/artymoment/',
              'https://www.mill6chat.org/zh-hant/co-learn/current-upcoming']

class HKTBSpider(scrapy.Spider):
    
    name = 'The Mills'
    start_urls = ['http://www.themills.com.hk/en/event/']
    
    def cleanText(self, list_of_data):
        for i in range(len(list_of_data)):
            list_of_data[i] = list_of_data[i].replace('  ', '')
            list_of_data[i] = list_of_data[i].replace('\n', '')
            list_of_data[i] = list_of_data[i].replace('\xa0', '')
            if len(list_of_data[i]) > 0 and list_of_data[i][0] == ' ':
                list_of_data[i] = list_of_data[i][1:]
            list_of_data[i] = list_of_data[i].replace('  ', '')
        list_of_data = [i for i in list_of_data if i != '']
        return list_of_data
    """
    def check_location(self, text):
        text_lower = text.lower()
        text_lower.replace(',', '')
        text_list = text_lower.split()
        matches = ['date', 'time', 'and', 'is', 'with', 'to', 'concept']
        for i in text_list:
            if i in matches:
                return False
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text))):
            if hasattr(chunk, "label"):
                if chunk.label() == "GPE" or chunk.label() == "GSP":
                    return True
        return False
    """
    def parse(self, response):
        for i in range(1, 20):
            yield scrapy.Request(response.url + 'page/' + str(i), callback=self.parse_links)

    def parse_links(self, response):
        
        info = response.xpath('//div[@class="col-xs-12 col-sm-6 pull-left"]').extract()

        urls = []
        for i in info:
            #print(i, '\n\n\n\n')
            if i.count('<div class="date">') > 0:
                while True:
                    #print(i, '\n\n')
                    #time.sleep(0.5)
                    j = i.index('http://www.themills.com.hk/')
                    k = j
                    while i[k] != '"':
                        k += 1
                    temp = i[j:k]
                    #print(temp, '\n\n')
                    if temp.count('.jpg') > 0 or temp in unable_url: 
                        i = i.replace(temp, '')
                    else:
                        urls.append(temp)
                        break

        for url in urls:
            
            new_data = {
                'event_name_chi': '',
                'event_name_eng': '',
                'start_date': '',
                'end_date': '',
                'fetch_date': datetime.now(),
                'description_chi': '',
                'description_eng': '',
                'event_type_chi': 'N/A',
                'event_type_eng': 'N/A',
                'location_chi': 'N/A',
                'location_eng': 'N/A',
                'fee': 'Free admission',
                'organiser_chi': '',
                'organiser_eng': '',
                'source': 'The Mills',
                'link_chi': '',
                'link_eng': ''
            }
            
            yield scrapy.Request(url, callback=self.parse_events, meta=new_data)

    def parse_events(self, response):

        #print('\n\n', response.url, '\n\n', sep='')

        new_data = response.meta
        
        header = response.xpath('//header//text()').extract()

        if len(header) > 2:

            header = self.cleanText(header)
            #print(header)
            new_data['event_name_eng'] = header[1]
            new_data['organiser_eng'] = header[2]

            dates = response.xpath('//div[@class="date"]/text()').extract_first()
            if dates.count(' - ') > 0:
                start_date = dates.split(' - ')[0]
                end_date = dates.split(' - ')[1]
                if end_date.count('.') == 0:
                    end_date = start_date[:8] + end_date
                elif end_date.count('.') == 1:
                    end_date = start_date[:5] + end_date
            else:
                start_date = dates
                end_date = dates
            
            new_data['start_date'] = datetime.strptime(start_date, '%Y.%m.%d')
            new_data['end_date'] = datetime.strptime(end_date, '%Y.%m.%d')

            content = response.xpath('//div[@class="content"]//text()').extract()
            content = self.cleanText(content)

            if len(header) > 3:
                content = header[3:] + content

            for i in content:
                new_data['description_eng'] = new_data['description_eng'] + i + '\n'

            for i in content:
                if i.count('$') > 0:
                    if i.count('.') == 0:
                        new_data['fee'] = i
                    break

            temp_content = []
            for i in content:
                if i.count('.') > 0 or i.count('!') > 0 or i.count('?') > 0:
                    temp = re.split('.!?', i)
                    temp_content = temp_content + temp
                else:
                    temp_content.append(i)
            matches = ['venue', 'Venue', 'venue:', 'Venue:']
            for i in temp_content:
                if any(j in i for j in matches):
                    new_data['location_eng'] = i
                    break                

            temp = new_data['event_name_eng'].lower()
            for i in list_of_event_type:
                for j in i:
                    if temp.count(j) > 0:
                        new_data['event_type_eng'] = i[0]
            
            new_data['link_eng'] = response.url

            yield scrapy.Request(response.url.replace('/en/', '/ch/'), callback=self.parse_events_ch, meta=new_data)

    def parse_events_ch(self, response):

        new_data = response.meta
        
        header = response.xpath('//header//text()').extract()

        if len(header) > 2:

            header = self.cleanText(header)
            new_data['event_name_chi'] = header[1]
            new_data['organiser_chi'] = header[2]

            content = response.xpath('//div[@class="content"]//text()').extract()
            content = self.cleanText(content)

            if len(header) > 3:
                content = header[3:] + content

            for i in content:
                new_data['description_chi'] = new_data['description_chi'] + i + '\n'

            temp_content = []
            for i in content:
                if i.count('.') > 0 or i.count('!') > 0 or i.count('?') > 0:
                    temp = re.split('.!?', i)
                    temp_content = temp_content + temp
                else:
                    temp_content.append(i)
            matches = ['地點', '地點：', '地點:']
            for i in temp_content:
                if any(j in i for j in matches):
                    new_data['location_chi'] = i
                    break
            if new_data['location_eng'] != 'N/A' and new_data['location_chi'] == 'N/A':
                new_data['location_chi'] = new_data['location_eng']
            if new_data['location_chi'] != 'N/A' and new_data['location_eng'] == 'N/A':
                new_data['location_eng'] = new_data['location_chi']

            for i in list_of_event_type:
                if new_data['event_type_eng'] == i[0]:
                    new_data['event_type_chi'] = i[1]
            
            new_data['link_chi'] = response.url

        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        del new_data['redirect_times']
        del new_data['redirect_ttl']
        del new_data['redirect_urls']
        del new_data['redirect_reasons']
        yield new_data
        #collection.insert(new_data)