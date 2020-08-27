import scrapy
from datetime import datetime

list_of_event_type = [['Performance', 'perform'],
                     ['Conversation', 'chat', 'conversation'],
                     ['Workshop', 'workshop', 'diy'],
                     ['Collection', 'collection']]

links = []

class HKTBSpider(scrapy.Spider):
    
    name = 'AsiaSociety'
    start_urls = ['https://asiasociety.org/hong-kong/events?page=']
    
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

    def parse(self, response):
        for i in range(0, 2):
            yield scrapy.Request(response.url + str(i), callback=self.parse_links)

    def parse_links(self, response):
        
        urls = response.xpath('//h4[@class="card-title"]/a/@href').extract()
        
        dates = response.xpath('//div[@class="datetime"]/text()').extract()
        dates = self.cleanText(dates)
        dates.append('1')

        i = 0

        for url in urls:
            
            new_data = {
                'event_name_chi': '',
                'event_name_eng': '',
                'start_date': '',
                'end_date': '',
                'fetch_date': datetime.now(),
                'description_chi': '',
                'description_eng': '',
                'event_type_chi': '',
                'event_type_eng': 'Conversation / Others',
                'location_chi': '',
                'location_eng': 'Online',
                'fee': 'Free admission',
                'organiser_chi': '',
                'organiser_eng': 'Asia Society Hong Kong Center',
                'source': 'Asia Society',
                'link_chi': '',
                'link_eng': 'https://asiasociety.org/' + url
            }

            date_list = dates[i].split()

            date = date_list[1] + ' ' + date_list[2] + ' ' + date_list[3]

            new_data['start_date'] = datetime.strptime(date, "%d %b %Y")
            new_data['end_date'] = datetime.strptime(date, "%d %b %Y")

            if dates[i + 1][0] in '0123456789':
                i += 2 
            else:
                i += 1
            
            yield scrapy.Request('https://asiasociety.org/' + url, callback=self.parse_events, meta=new_data)

    def parse_events(self, response):

        new_data = response.meta
        
        list_of_data = response.xpath('//p').extract()
        
        list_of_data = self.cleanText(list_of_data)
        
        #print(list_of_data)

        for i in list_of_data[:]:
            if i.count('$') > 0 and i.count('.') == 0:
                j = i.index('$')
                k = i.index('$')
                while i[j] != '>':
                    j -= 1
                while i[k] != '<':
                    k += 1
                new_data['fee'] = i[j + 1:k]
                break

        title = response.xpath('//meta[@property="og:title"]').extract_first()
        title = title.replace('\xa0', '')
        title = title[35:-2]
        new_data['event_name_eng'] = title

        description = response.xpath('//meta[@name="description"]').extract_first()
        description = description.replace('\xa0', '')
        description = description[34:-2]
        new_data['description_eng'] = description
        
        if title.count(' @ ') > 0:
            organiser = title.split(' @ ')[0]
            if organiser.count('] ') > 0:
                organiser = organiser[organiser.index('] ') + 2:]
            new_data['organiser_eng'] = organiser

        temp = title.lower()
        for i in list_of_event_type:
            for j in i:
                if temp.count(j) > 0:
                    new_data['event_type_eng'] = i[0]

        del new_data['depth']
        del new_data['download_timeout']
        del new_data['download_slot']
        del new_data['download_latency']
        del new_data['redirect_times']
        del new_data['redirect_ttl']
        del new_data['redirect_urls']
        del new_data['redirect_reasons']
        yield new_data