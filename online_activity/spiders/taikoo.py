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

class TaikooSpider(scrapy.Spider):
    name = 'taikoo'
    # allowed_domains = ['https://www.taikooplace.com/en/whatson']
    start_urls = ['http://www.taikooplace.com/en/whatson']

    def cleanText(self, string):
        string = re.sub("</?[^>]*>", "", str(string))
        string = string.strip("[]").strip("'")
        string = string.replace("\\n", "")
        string = string.replace("\\t", "")
        string = string.replace("\\r", " ")
        string = string.replace("\\xa0", " ")
        return string

    def parse(self, response):
        urls = response.xpath("//*[@id='mainform']/div[5]/div/div[4]/div[1]/div/a/@href").extract()
        for url in urls:
            link = "http://www.taikooplace.com" + url
            yield scrapy.Request(link, callback=self.parse_events)

    def parse_events(self, response):
        date_pattern = r"\d{1,2}(?:st|nd|rd|th)\s+(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{4}|\d{1,2}(?:st|nd|rd|th)\s+(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)|\d{1,2}\s+(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{4}|\d{1,2}\s+(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)|((Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\s+\d{4})|(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)"
        name = response.xpath("//*[@id='mainform']/div[5]//h1//text()").extract()
        description = response.xpath("//*[@id='mainform']//div[@class='event-detail__copy body-copy']//text()").extract()
        location = ""
        fee = ""
        start_date = ""
        end_date = ""
        
        for i in range(len(description)):
            description[i] = self.cleanText(description[i]).strip()
                
        data_cluster = response.xpath("//*[@id='mainform']/div[5]/div/div[2]/div/div[1]/div/div/div/text()").extract()
        
        if (len(data_cluster) != 0):
            if "Free" in data_cluster[0]:
                fee = data_cluster[0]
            else:
                if (len(data_cluster) == 2):
                    location = data_cluster[0]
                    fee = data_cluster[1]
                if (len(data_cluster) == 1):
                    location = data_cluster[0]
                    fee = ""
        
        combined_desc = ""
        for word in description:
            combined_desc += word
        print("\n\n\n")
        print(response.url)
        print(combined_desc)
        matches = re.finditer(date_pattern, combined_desc, re.MULTILINE)
        year_from_link = re.finditer(r"\d{4}", response.url, re.MULTILINE)

        the_yr = re.findall(r"\d{4}", combined_desc)
        if (len(the_yr) == 0):
            pass
        else:
            the_yr = max(the_yr)
        # for i in range(len(dates)):
        #     the_yr = re.findall(r"\d{4}", dates[i])
        
        for l_yr in year_from_link:
            l_yr = l_yr.group()
        
            try:
                if (the_yr < l_yr):
                    the_yr = l_yr
            except:
                the_yr = l_yr

        print("the year is : ", end="")
        print(the_yr)

        dates = []
        for match in matches:
            match = match.group()
            # remove date ordinals
            match = re.sub(r'(\d)(st|nd|rd|th)', r'\1', match)
            dates.append(match)
            # print(match)

        for i in range(len(dates)):
            if (not re.match(r"\d{1,2}", dates[i])):
                dates[i] = "1 " + dates[i]
            if (not re.search(r"\d{4}", dates[i])):
                try:
                    dates[i] += " " + the_yr
                except:
                    dates[i] += " 2020"
        
        print("The dates are: ")
        for d in dates:
            print(d)
        
        for i in range(len(dates)):
            try:
                dates[i] = datetime.strptime(dates[i], "%d %b %Y")
            except:
                dates[i] = datetime.strptime(dates[i], "%d %B %Y")

        if (len(dates) == 1):
            start_date = dates[0]
        else:
            try:
                smol = dates[0]
                for d in dates:
                    if d <= smol:
                        smol = d
                start_date = smol
                larg = dates[0]
                for d in dates:
                    if d >= larg:
                        larg = d
                end_date = larg
            except:
                pass
        
        print("Start and end date are: ")
        print(start_date)
        print(end_date)

        print("\n\n\n")
        # description = self.cleanText(description)
        data["event_name_eng"] = name[0]
        data["description_eng"] = combined_desc
        data["start_date"] = start_date
        data["end_date"] = end_date
        data["fetch_date"] = datetime.now()
        data["location_eng"] = location
        data["fee"] = fee
        data["link_eng"] = response.url

        req1 = scrapy.Request(response.url.replace('/en/', '/zh-hk/'), callback=self.parse_cn, meta=data)
        yield req1

    def parse_cn(self, response):
        data = response.meta

        name_chi = response.xpath("//*[@id='mainform']/div[5]//h1//text()").extract()
        description_chi = response.xpath("//*[@id='mainform']//div[@class='event-detail__copy body-copy']//text()").extract()

        for i in range(len(description_chi)):
            description_chi[i] = self.cleanText(description_chi[i]).strip()
                
        data_cluster = response.xpath("//*[@id='mainform']/div[5]/div/div[2]/div/div[1]/div/div/div/text()").extract()
        
        location_chi = ""
        if (len(data_cluster) != 0):
            if "Free" in data_cluster[0]:
                # copy pasted from above, does absolutely nothing here but as a buffer. Kept it cause it's still working perfectly fine
                fee = data_cluster[0] 
            else:
                if (len(data_cluster) == 2):
                    location_chi = data_cluster[0]
                if (len(data_cluster) == 1):
                    location_chi = data_cluster[0]

        combined_desc = ""
        for word in description_chi:
            combined_desc += word
            
        data["event_name_chi"] = name_chi[0]
        data["description_chi"] = combined_desc
        data["location_chi"] = location_chi
        data["event_type_chi"] = ""
        data["event_type_eng"] = ""
        data["organiser_chi"] = ""
        data["organiser_eng"] = ""
        data["source"] = "Tai Koo Place"
        data["link_chi"] = response.url
        del data["depth"]
        del data["download_timeout"]
        del data["download_slot"]
        del data["download_latency"]
        
        # yield data
