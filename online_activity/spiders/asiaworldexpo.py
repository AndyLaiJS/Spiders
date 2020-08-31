import scrapy
from scrapy.selector import Selector
import re
from datetime import datetime

list_data = []

class AsiaworldexpoSpider(scrapy.Spider):
    name = 'asiaworldexpo'
    # allowed_domains = ['www.asiaworld-expo.com/events/']
    start_urls = ['http://www.asiaworld-expo.com/events']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        string = string.replace("\\r", " ")
        string = string.replace("\n", "")
        string = string.replace("\t", "")
        string = string.replace("\r", " ")
        string = string.replace("\\xa0", "")
        string = string.replace("\xa0", "")
        return string

    def parse(self, response):
        _ids = []
        the_id = response.xpath('//*[@id="content"]/div[4]/div/dl/dt').extract()
        for i in the_id:
            _ids.append(re.findall(r'id=".+\d{4}"', i)[0].strip('id="'))

        name = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//h3/text()').extract()
        location = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//div[@class="title-wrapper"]/span/text()[not(contains(., "\n"))]').extract()
        description_clusters = response.xpath('//*[@id="content"]/div[4]/div/dl/dd').extract()

        descriptions = []
        # Cleaning up and handling for description
        for element in description_clusters:
            # print(element)
            description = ""
            description_list = Selector(text=element).xpath('//div[@class="info clearfix"]//p[position() >= 2]//text()').extract()
            for el in description_list:
                description += el
            description = self.cleanText(description)
            descriptions.append(description)

        # Organizer handling
        organisers = []
        for element in description_clusters:
            # print(element)
            organiser = ""
            organiser_list = Selector(text=element).xpath('//div[@class="info clearfix"]//p[@class="organiser-list"]//a/text()').extract()
            for el in organiser_list:
                organiser += el
            organiser = self.cleanText(organiser)
            organisers.append(organiser)
        
        # Date handling
        data_clusters = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//div[@class="date big-date is-single-date " or @class="date big-date is-range-date "]').extract()
        
        dates = []
        for element in data_clusters:
            date_list = Selector(text=element).xpath('//span//text()').extract()
            the_month = Selector(text=element).xpath('//span[@class="m-date__month"]//text()').extract()
            the_year = Selector(text=element).xpath('//span[@class="m-date__year"]//text()').extract()
            date = ""
            start_date = ""
            end_date = ""

            indx = 0

            for i in range(len(date_list)):
                date += " " + date_list[i].strip()
            
            if "-" in date:
                datesss = date.split(" - ")
                start_date = (datesss[0] + " " + the_month[indx] + the_year[indx]).strip()
                end_date = datesss[1].strip()
                indx += 1
                start_date = datetime.strptime(start_date, "%d %b %Y")
                end_date = datetime.strptime(end_date, "%d %b %Y")
                date_container = [start_date, end_date]
                dates.append(date_container)
            else:
                start_date = date.strip()
                start_date = datetime.strptime(start_date, "%d %b %Y")
                date_container = [start_date, end_date]
                dates.append(date_container)

        # Fee handling
        # fee_clusters = response.xpath('//*[@id="content"]/div[4]/div/dl/dd').extract()
        # fees = []
        # for element in fee_clusters:
        #     print(element)
        #     fees.append(Selector(text=element).xpath('//div[@class="buttons clearfix "]//a[@class="tickets "]/@href').extract())
        # print(fees)
        data = {
            '_id': '',
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

        global list_data

        for i in range(len(name)):
            data = {
                '_id': _ids[i],
                'event_name_chi': '',
                'event_name_eng': name[i],
                'start_date': dates[i][0],
                'end_date': dates[i][1],
                'fetch_date': datetime.now(),
                'description_chi': '',
                'description_eng': descriptions[i],
                'event_type_chi': '',
                'event_type_eng': '',
                'location_chi': '',
                'location_eng': location[i],
                'fee': '',
                'organiser_chi': '',
                'organiser_eng': organisers[i],
                'source': "Asia World Expo",
                'link_chi': '',
                'link_eng': response.url,
            }
            list_data.append(data)

        next_page = response.xpath('//*[@id="content"]/div[4]/div/div/div/div[2]/a[@class="next"]/@href').extract()
        if (len(next_page) > 0):
            yield scrapy.Request(next_page[0], callback=self.parse)
        else:
            yield scrapy.Request("https://www.asiaworld-expo.com/zh-tc/events/", callback=self.parse_cn)
        # print(name)
            # yield data
        

        # the next button
        # //*[@id="content"]/div[4]/div/div/div/div[2]/a[2]/@href
    
    def parse_cn(self, response):
        _ids = []
        the_id = response.xpath('//*[@id="content"]/div[4]/div/dl/dt').extract()
        for i in the_id:
            _ids.append(re.findall(r'id=".+\d{4}"', i)[0].strip('id="'))

        names_chi = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//h3/text()').extract()
        location_chi = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//div[@class="title-wrapper"]/span/text()[not(contains(., "\n"))]').extract()
        description_clusters = response.xpath('//*[@id="content"]/div[4]/div/dl/dd').extract()

        desc_chi = []
        # Cleaning up and handling for description
        for element in description_clusters:
            # print(element)
            description = ""
            description_list = Selector(text=element).xpath('//div[@class="info clearfix"]//p[position() >= 2]//text()').extract()
            for el in description_list:
                description += el
            description = self.cleanText(description)
            desc_chi.append(description)

        # Organizer handling
        org_chi = []
        for element in description_clusters:
            # print(element)
            organiser = ""
            organiser_list = Selector(text=element).xpath('//div[@class="info clearfix"]//p[@class="organiser-list"]//a/text()').extract()
            for el in organiser_list:
                organiser += el
            organiser = self.cleanText(organiser)
            org_chi.append(organiser)

        # print(list_data)

        for i in range(len(names_chi)):
            for j in range(len(list_data)):
                if (list_data[j]["_id"] == _ids[i]):
                    # print(f"Ids of {_ids[i]} matched!")
                    list_data[j]["event_name_chi"] = names_chi[i]
                    list_data[j]["description_chi"] = desc_chi[i]
                    list_data[j]["location_chi"] = location_chi[i]
                    list_data[j]["organiser_chi"] = org_chi[i]
                    list_data[j]["link_chi"] = response.url
                    break
                elif (j == len(list_data) - 1):
                    # Let's handle this chinese date. Surprisingly it's easier!!
                    data_clusters = response.xpath('//*[@id="content"]/div[4]/div/dl/dt//div[@class="date big-date is-single-date " or @class="date big-date is-range-date "]').extract()
                    date_list = Selector(text=data_clusters[i]).xpath('//span//text()').extract()

                    dates = ""
                    start_date = ""
                    end_date = ""

                    for d in date_list:
                        dates += " " + d.strip()
                    dates = dates.strip()

                    if "-" in dates:
                        start_date = datetime.strptime(dates.split(" - ")[0], "%Y年 %m月 %d日")
                        end_date = datetime.strptime(dates.split(" - ")[1], "%Y年 %m月 %d日")
                    else:
                        start_date = datetime.strptime(dates, "%Y年 %m月 %d日")
                    
                    # Then we slap it into the dictionary
                    data = {
                        '_id': _ids[i],
                        'event_name_chi': names_chi[i],
                        'event_name_eng': '',
                        'start_date': start_date,
                        'end_date': end_date,
                        'fetch_date': datetime.now(),
                        'description_chi': desc_chi[i],
                        'description_eng': '',
                        'event_type_chi': '',
                        'event_type_eng': '',
                        'location_chi': location_chi[i],
                        'location_eng': '',
                        'fee': '',
                        'organiser_chi': org_chi[i],
                        'organiser_eng': '',
                        'source': "Asia World Expo",
                        'link_chi': response.url,
                        'link_eng': '',
                    }
                    list_data.append(data)
        
        next_page = response.xpath('//*[@id="content"]/div[4]/div/div/div/div[2]/a[@class="next"]/@href').extract()
        if (len(next_page) > 0):
            yield scrapy.Request(next_page[0], callback=self.parse_cn)
        else:
            for data in list_data:
                yield data

        # print(names_chi)