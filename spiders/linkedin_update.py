# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class LinkedinUpdateSpider(CrawlSpider):
    times = 0
    name = 'linkedin_update'
    allowed_domains = ['linkedin.com']
    start_urls = ['https://www.linkedin.com/']
    rules = (
        Rule(LinkExtractor(allow=('jobs/', )),
             callback='parse_inter'),
    )

    def parse_inter(self, response):
        url = response.url
        print('url:',url)
        # tourlist = ['https://www.linkedin.com/jobs/search?keywords=','','&location=hk&sortBy=DD&pageNum=0&position=1&trk=jobs_jserp_pagination_1&start=0&count=25']
        tourlist = ['https://www.linkedin.com/jobs-guest/jobs/api/jobPostings/jobs?keywords=','','&location=hk&sortBy=DD&pageNum=0&position=1&trk=jobs_jserp_pagination_1&start=25&count=25&redirect=false']
        try:
            print("0000>", url.split('jobs/')[1].split('-jobs-')[0].split('?')[0])
            tourlist[1] = url.split('jobs/')[1].split('-jobs-')[0].split('?')[0]
        except:
            print("ERROR")
        tourl = ';;;'.join(tourlist).replace("&redirect=false", '').replace('?trk=homepage-basic_brand-discovery','')
        print("tourl:",tourl)
        if 'jobs-in' in tourl:
            return
        yield scrapy.Request(tourl, callback=self.parse_item)
        
    def getNextPage(self, cpage):
        cpage = cpage.split('&')
        for i in range(len(cpage)):
            # if "pageNum" in cpage[i]:
            #     # print("found pageNum")
            #     tmp = cpage[i].split('=')
            #     tmp[1] = int(tmp[1]) + 1
            #     cpage[i] = str(tmp[0]) + "=" + str(tmp[1])
            #     # print(cpage[i])
            if "=jobs_jserp_pagination_" in cpage[i]:
                # print("found jobs_jserp_pagination_")
                tmp = cpage[i].split('=jobs_jserp_pagination_')
                tmp[1] = int(tmp[1]) + 1
                cpage[i] = str(tmp[0]) + "=jobs_jserp_pagination_" + str(tmp[1])
                # print(cpage[i])

            if "start" in cpage[i]:
                # print("found start")
                tmp = cpage[i].split('=')
                tmp[1] = int(tmp[1]) + 25
                cpage[i] = str(tmp[0]) + "=" + str(tmp[1])
                # print(cpage[i])
        return '&'.join(cpage)

    def parse_item(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="result-card job-result-card result-card--with-hover-state"]/a/@href').getall()
        # print("I am jobs_url:", jobs_url)
        # print(response.body)
        # page = self.getNextPage(response.url)
        # print("I am pages:", page)
        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))
        if(len(jobs_url) == 0):
            print("No job found on", response.url)
            return
        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            # job_url = "https://www.indeed.hk" + job_url
            print("Now working on JobURL", job_url)
            yield scrapy.Request(job_url, callback=self.parse_job)

        # pages = response.xpath('//*[@class="np"]/../../@href').getall()
        print("current index page:", response.url)
        page = self.getNextPage(response.url)
        print("I am pages:", page)
        # self.times += 1
        # if (self.times > 3):
        #     exit()
        yield scrapy.Request(page, callback=self.parse_item)
        

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        useful = dict()
        try:
            jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)
            print("HAVE JSON FOUND")
        except:
            print("NO JSON FOUND")
        tmp = response.xpath('//a[@class="apply-button apply-button--link"]/@href').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = tmp[0]
        else:
            useful['applyLink'] = tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//h1[@class="topcard__title"]/text()').extract())
        useful['salary'] = {
            'max': None,
            'min': None,
            'type': None,
            'extraInfo': None,
            'currency': None,
            'salaryOnDisplay': None
        }
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = response.xpath('//*[@class="topcard__flavor--metadata topcard__flavor--bullet num-applicants__caption"]/text()').get()
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': ';;;'.join(response.xpath('//h3[contains(text(),"Seniority level")]/../span/text()').extract()),
                'yearsOfExperience': None,
                'educationLevel': None,
                'skills': (jj['skills'] if 'skills' in jj else None)
            },
            'industryValue': {
                'value': None,
                'lable': response.xpath('//h3[contains(text(),"Industries")]/../span/text()').extract()
            },
            'employmentType': ';;;'.join(response.xpath('//h3[contains(text(),"Employment type")]/../span/text()').extract()),
            'jobFunction[Id,Title]': response.xpath('//h3[contains(text(),"Job function")]/../span/text()').extract(),
            'benefits': response.xpath('//u[contains(text(),"Benefits")]/../following-sibling::ul//text()').extract()
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': ';;;'.join(response.xpath('//a[@class="topcard__org-name-link"]/text()').extract()),
                'companyWebsiteURL': None,
                'companyOverview': response.xpath('//div[@class="company-info__rich-text"]/text()').extract(),
                'companyLogoUrls': (jj['hiringOrganization']['logo'] if ('hiringOrganization' in jj) and ('logo' in jj['hiringOrganization']) else None)
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//span[@class="topcard__flavor topcard__flavor--bullet"]/text()').extract())
        useful['postDate'] = (jj['datePosted'] if 'datePosted' in jj else None)
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = response.xpath('//section[@class="similar-jobs"]/div/ul//a/@href').extract()
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//div[@class="description__text description__text--rich"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'LinkedIn'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # pprint.pprint(useful)
        return useful
