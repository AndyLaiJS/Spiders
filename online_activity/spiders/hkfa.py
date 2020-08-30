import scrapy
import re
from datetime import datetime
from selenium import webdriver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER   

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

count = 0
scrap_fee = False

class HkfaSpider(scrapy.Spider):
    name = 'hkfa'
    # allowed_domains = ['www.filmarchive.gov.hk/en_US/web/hkfa/programmesandexhibitions/evecal.html']
    start_urls = ['http://www.filmarchive.gov.hk/en_US/web/hkfa/programmesandexhibitions/evecal.html']

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
        string = string.replace("#", "")
        return string

    def parse(self, response):
        # LOGGER.setLevel(logging.WARNING)
        PATH = "/Users/andylai/chromedriver"
        driver = webdriver.Chrome(PATH)
        driver.get(response.url)

        # Get urls using Selenium due to the page being dynamically rendered instead of statically
        urls = driver.find_elements_by_xpath("//*[@id='article']/table[@class='table_main']//a")

        links = []
        for url in urls:
            links.append(url.get_attribute("href"))
        
        for i in range(len(links)-1):
            for j in range(i+1, len(links)):
                if (links[i] == links[j]):
                    links[j] = ""
                    # urls[j] = ""
        
        print("\n\n\n")
        print(links)
        print("\n\n\n")
        for link in links:
            if (link != ""):
                yield scrapy.Request(link, callback=self.parse_events)

    def parse_events(self, response):
        # global data, scrap_fee
        for keys in data.keys():
            data[keys] = ""

        # name handler
        name = response.xpath('//*[@id="title_bar_left"]/text()').extract_first()
        # //*[@id="article"]/div[2]/div/table/tbody/tr/th/p/span/strong
        if (name == "Film Screenings"):
            name = response.xpath('//*[@id="article"]//p/span/strong/text()').extract_first()
        
        if (name == None):
            name = response.xpath('//div[@class="application"]/h1/text()').extract()
            # cleaning up
            tmp = name
            name = ""
            for text in tmp:
                name += text
            name = self.cleanText(name)
        
        data["event_name_eng"] = name
        # End of handle of name
        
        # Handle description
        description = response.xpath("//*[@id='article']/div/div/div/div/p[position() >= 3]/text()").extract()

        if (len(description) == 0):
            description = response.xpath("//*[@id='article']/p[position() >= 2]/text()").extract()
            if (len(description) == 0):
                description = response.xpath("//article/div/div[3]/div[@class='span12 doppelTeaser']/text()[8]").extract()
        
        desc = ""
        for i in range(len(description)):
            desc += self.cleanText(description[i])

        data["description_eng"] = desc.strip() 
        # End of handle of description

        # Handle location
        location = response.xpath("//*[@id='article']/div/div/div/div/p[2]/strong/text()").extract()

        if (len(location) == 0):
            location = response.xpath("//*[@id='article']/table[@class='table_main']/tbody/tr[2]/td[3]/text()").extract_first()
            if (location == None):
                location = response.xpath("//div[@class='teaserBox']/h2/text()").extract_first().strip()
            else:
                location = location.strip()
        else:
            location = location[1].replace("Venue：", "").strip()
            
        data["location_eng"] = location
        # End of handle of location 

        # Handle date
        dates = response.xpath('//*[@id="article"]/div/div/div/div/p[2]/strong/text()[1]').extract()
        
        if (len(dates) == 0):
            dates = response.xpath('//*[@id="article"]/table[@class="table_main"]/tbody/tr[position() >= 2]/td[1]/text()').extract()
            if (len(dates) == 0):
                dates = response.xpath('/html/body/div[1]/div[3]/div[1]/div/article/div/div[1]/div/p[1]/text()').extract()
        
        for i in range(len(dates)):
            dates[i] = self.cleanText(dates[i])
            dates[i] = re.sub("\([^)]*\)", "", dates[i])
            dates[i] = dates[i].replace("Date：", "")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for d in days:
                replace_this = d + ", "
                dates[i] = dates[i].replace(replace_this, "")
            dates[i] = dates[i].strip()

        if " - " in dates[0]:
            dates = dates[0].split(" - ")
            start_date = datetime.strptime(dates[0], "%d/%m/%Y")
            end_date = datetime.strptime(dates[1], "%d/%m/%Y")
        else:
            if "." in dates[0]:
                start_date = datetime.strptime(dates[0], "%d.%m.%Y")
                end_date = ""
            else:
                start_date = []
                try:
                    for i in range(len(dates)):
                        start_date = datetime.strptime(dates[i], "%d/%m/%Y")
                except:
                    for i in range(len(dates)):
                        dates[i] += "/" + str(datetime.today().year)
                        
                        start_date.append(datetime.strptime(dates[i], "%d/%m/%Y"))
                end_date = ""

        data["start_date"] = start_date
        data["end_date"] = end_date
        data["fetch_date"] = datetime.now()
        # End of handle of date

        data["source"] = "Hong Kong Film Archive"
        data["link_eng"] = response.url

        if "goethe" in response.url:
            yield scrapy.Request(response.url.replace('/en/', '/cn/'), callback=self.parse_cn, meta=data)
        else:
            yield scrapy.Request(response.url.replace('/en_US/', '/zh_TW/'), callback=self.parse_cn, meta=data)

    def parse_cn(self, response):
        data = response.meta
        # name handler
        name = response.xpath('//*[@id="title_bar_left"]/text()').extract_first()
        # //*[@id="article"]/div[2]/div/table/tbody/tr/th/p/span/strong
        if (name == "電影放映"):
            name = response.xpath('//*[@id="article"]//span/strong/text()').extract_first()
        
        if (name == None):
            name = response.xpath('//div[@class="application"]/h1/text()').extract()
            # cleaning up
            tmp = name
            name = ""
            for text in tmp:
                name += text
            name = self.cleanText(name)
        
        data["event_name_chi"] = name
        # End of handle of name
        
        # Handle description
        description = response.xpath("//*[@id='article']/div/div/div/div/div/p/text()").extract()
        if (len(description) == 0):
            description = response.xpath('//*[@id="article"]/div/div/div/div/p[position() >= 3]/text()').extract()
            if (len(description) == 0):
                description = response.xpath("//*[@id='article']/p[position() >= 2]/text()").extract()
                if (len(description) == 0):
                    description = response.xpath("//article/div/div[3]/div[@class='span12 doppelTeaser']/text()[8]").extract()
            
        desc = ""
        for i in range(len(description)):
            desc += self.cleanText(description[i])

        data["description_chi"] = desc.strip() 
        # End of handle of description

        # Handle location
        location = response.xpath("//*[@id='article']/div/div/div/div/p[2]/strong/text()").extract()

        if (len(location) == 0):
            location = response.xpath("//*[@id='article']/table[@class='table_main']/tbody/tr[2]/td[3]/text()").extract_first()
            if (location == None):
                location = response.xpath("//div[@class='teaserBox']/h2/text()").extract_first().strip()
            else:
                location = location.strip()
        else:
            location = location[1].replace("地點：", "").strip()
            
        data["location_chi"] = location
        # End of handle of location 

        data["link_chi"] = response.url

        # Handle fee
        fee = response.xpath('//*[@id="article"]/div/div/div/div/p[2]/text()').extract()
        
        if (len(fee) == 0):
            if ("goethe" in response.url):
                # To handle goethe
                fee_list = response.xpath('//div[1]/div[3]/div[1]/div/article/div/div[3]/aside/p/text()').extract()
                fee_chunk = ""
                for stuff in fee_list:
                    fee_chunk += stuff
                new_fee = re.findall(r"[$]\d+", fee_chunk)[0]
                data["fee"] = new_fee

                try:
                    del data["depth"]
                    del data["download_timeout"]
                    del data["download_slot"]
                    del data["download_latency"]
                    del data["redirect_times"]
                    del data["redirect_ttl"]
                    del data["redirect_urls"]
                    del data["redirect_reasons"]
                except:
                    pass

                yield data

            else:
                fee_link = response.url.replace("https://", "").split("/")
                fee_link[len(fee_link)-1] = "ticketinfo.html"
                ticket_link = ""
                for link in fee_link:
                    ticket_link += link + "/"
                ticket_link = ticket_link.rstrip("/")
                ticket_link = "https://"+ticket_link
                yield scrapy.Request(ticket_link, callback=self.get_fee, meta=data, dont_filter=True)
            # yield scrapy.Request(ticket_link, callback=self.get_fee, meta=data, dont_filter=True)
        else:
            nfee = ""
            for f in fee:
                if re.search(r"\w", f):
                    nfee = f
                    break
            if "免費" in nfee:
                nfee = "Free Admission"
            data["fee"] = nfee

            try:
                del data["depth"]
                del data["download_timeout"]
                del data["download_slot"]
                del data["download_latency"]
                del data["redirect_times"]
                del data["redirect_ttl"]
                del data["redirect_urls"]
                del data["redirect_reasons"]
            except:
                pass

            yield data
            # yield data
        # End of handle of fee

    def get_fee(self, response):
        data = response.meta
        fee = response.xpath('//*[@id="article"]//p[span//strong//text()[contains(., "票價：" )]]//text()').extract()

        # if (len(fee) == 0):
        #     ggfee = response.xpath('//div[1]/div[3]/div[1]/div/article/div/div[3]/aside/p[1]/text()[2]').extract()
        #     # //div[1]/div[3]/div[1]/div/article/div/div[3]/aside/p[1]/text()[2]
        #     # div[3]/div[1]/div/article/div/div[3]/aside/p/text()
            
        #     print("\n\n\n\nGG FEE: ")
        #     print(ggfee)
        #     print("\n\n\n\n")
        # aside class=span6 artikelspalte doppelTeaser / p 
        # Regex r"[$]\d+"
        # /html/body/div[1]/div[3]/div[1]/div/article/div/div[3]/aside/p[1]/text()[2]

        nfee = ""

        for f in fee:
            if re.search(r"\w", f):
                nfee = f
                break

        data["fee"] = nfee.replace("票價：", "")

        try:
            del data["depth"]
            del data["download_timeout"]
            del data["download_slot"]
            del data["download_latency"]
            del data["redirect_times"]
            del data["redirect_ttl"]
            del data["redirect_urls"]
            del data["redirect_reasons"]
        except:
            pass

        yield data