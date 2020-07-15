# -*-_blocked coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime
import re

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['www.indeed.hk']
    start_urls = ['https://www.indeed.hk/jobs?l=Hong+Kong&sort=date&start=0']

    def getSalary(self, ssalary):
        print("me:",ssalary)
        if (ssalary == []):
            return
        salary = str(ssalary).split('-')
        minn = ""
        maxx = ""
        extra = ""
        for i in salary[0]:
            if i.isdigit():
                minn = minn + i
        for i in salary[1]:
            if i.isdigit():
                maxx = maxx + i
            if i.isalpha():
                extra = extra + i
        print("I am Salary:",int(minn), int(maxx), extra)

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="title"]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            print("I am job ID:", job_id)
            job_url = "https://www.indeed.hk" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="np"]/../../@href').getall()
        print("I am pages:", pages)
        if pages:
            page = max(max(pages), max(pages, key=len), key=len)
            print("I am page:", page)
            logging.debug('Going to: ' + response.urljoin(page))
            yield scrapy.Request(response.urljoin(page), callback=self.parse)
        else:
            split_url = response.url.split('=')
            try:
                page_num = int(split_url[-1])
            except:
                logging.debug('No next page: ' + response.url)
                return scrapy.Request('')
            else:
                page_num += 1
                split_url[-1] = str(page_num)
                next_url = '='.join(split_url)
                logging.debug('No next button, going to: ' + next_url)
                yield scrapy.Request(next_url, callback=self.parse)

    def processSalary(self, salary):
        money = re.findall("[0-9,.]+[MKmk(\s?million)]?", salary)
        current = re.findall("[A-Z]{3}?", salary)
        mtype = re.findall("(?i)(month|year|hour|minute|yr|yrs|day|days|week|weeks|months|years|hours|minutes)", salary)
        maxx = 0
        minn = 0
        if (len(money) >= 2):
            maxx = money[1]
            minn = money[0]
        elif(len(money) == 1):
            maxx = money[0]
            minn = money[0]
        return {'moneymax': maxx, 'moneymin': minn, 'current': current, 'mtype': mtype}

    
    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        useful = dict()
        tmp = response.xpath('//*[@id="viewJobButtonLinkContainer"]//a/@href').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = tmp[0]
        else:
            useful['applyLink'] = tmp

        # Remove tracking part from the url
        joburl = re.search("([^\?]+\?).*?(jk=[^\&]+)", response.url)
        useful['jobId'] = joburl[1] + joburl[2]
        useful['jobTitle'] = ';;;'.join(response.xpath('//*[contains(@class,"jobsearch-JobInfoHeader-title")]/text()').extract())
        salaryDict = self.processSalary(str(response.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]/div[3]/div[1]/div//span[contains(text(), "$")]/text()').extract()))
        useful['salary'] = {
            'max': salaryDict['moneymax'],
            'min': salaryDict['moneymin'],
            'type': ';;;'.join(salaryDict['mtype']),
            'extraInfo': None,
            'currency': ';;;'.join(salaryDict['current']),
            'salaryOnDisplay': ';;;'.join(response.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]/div[3]/div[1]/div//span[contains(text(), "$")]/text()').extract())
        }
        # self.getSalary(response.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]/div[3]/div[1]/div//span[contains(text(), "$")]/text()').extract())
        useful['jobRating'] = response.xpath('//*[@class="icl-Ratings-starsCountWrapper"]/@aria-label').get()
        useful['numberOfAppliant(FromLinkedIn)'] = None
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': None,
                'yearsOfExperience': None,
                'educationLevel': None,
                'skills': None
            },
            'industryValue': {
                'value': None,
                'lable': ""
            },
            'employmentType': ';;;'.join(response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()),
            'jobFunction[Id,Title]': None,
            'benefits': response.xpath('//*[contains(text(),"Benefits")]/text()').extract() + response.xpath('//b[contains(text(),"Benefits")]/../following-sibling::ul//text()').extract()
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': ';;;'.join(response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()),
                'companyWebsiteURL': None,
                'companyOverview': None,
                'companyLogoUrls': None
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--location icl-IconFunctional--md")]/../span/text()').extract())
        useful['postDate'] = ';;;'.join(response.css('div.jobsearch-JobMetadataFooter::text').extract())
        try:
            useful['moreJobsFromThisCompany'] = "https://www.indeed.hk" + response.xpath('//a[@class="jobsearch-RelatedLinks-link"]/@href')[1].extract()
            useful['relatedJobs'] = "https://www.indeed.hk" + response.xpath('//a[@class="jobsearch-RelatedLinks-link"]/@href')[0].extract()
        except:
            print("cannot get related jobs on",response.url)
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//*[@id="jobDescriptionText"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'Indeed'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # pprint.pprint(useful)
        return useful
