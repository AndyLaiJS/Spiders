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

class GlassdoorUpdateSpider(CrawlSpider):
    name = 'glassdoor_update'
    allowed_domains = ['glassdoor.com.hk']
    start_urls = ['https://www.glassdoor.com.hk']
    rules = (
        Rule(LinkExtractor(allow=('Job/', )),
             callback='parse_item'),
    )

    # def parse_topLink(self, response):
    #     logging.debug('Parsing top page: {url}'.format(url=response.url))
    #     yield scrapy.Request(response.url, callback=self.parse_item)
    #     print("I am here")
    
    def parse_item(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="jlGrid hover"]//li/div[@class="jobContainer"]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))


        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            print("I am job ID:", job_id)
            job_url = "https://www.glassdoor.com.hk" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//li[@class="next"]/a/@href').get()
        if response.xpath('//*[@class="module marg"]//text()').get() == 'Help Us Keep Glassdoor Safe':
            print('Blocked by recaptcha')
            exit()
        print("I am before pages", pages)
        if(pages == None):
            try:
                if '_IP' not in response.url:
                    pages = response.url.replace('.htm', '_IP2.htm')
                else:
                    a = int(response.url.split('_IP')[1].split('.')[0])
                    pages = response.url.replace(f'_IP{a}.htm', f'_IP{a+1}.htm')
            except:
                print("ERRORRRRRRRRR on next page")
        print("I am pages:", pages, "under:",response.url, response)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse_item)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        jj = ''
        try:
            jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)
        except:
            print("this job is blocked by recaptcha")
        useful = dict()
        tmp = response.css('div.regToApplyArrowBoxContainer a::attr(data-job-url)').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = "https://www.glassdoor.com.hk" + tmp[0]
        else:
            useful['applyLink'] = "https://www.glassdoor.com.hk" + tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//*[@class="jobViewJobTitleWrap"]/h2/text()').extract())
        useful['salary'] = {
            'max': jj['estimatedSalary']['value']['maxValue'] if 'estimatedSalary' in jj and 'maxValue' in jj['estimatedSalary']['value'] else None,
            'min': jj['estimatedSalary']['value']['minValue'] if 'estimatedSalary' in jj and 'minValue' in jj['estimatedSalary']['value'] else None,
            'type': jj['estimatedSalary']['value']['unitText'] if 'estimatedSalary' in jj and 'unitText' in jj['estimatedSalary']['value'] else None,
            'extraInfo': None,
            'currency': jj['estimatedSalary']['currency'] if 'estimatedSalary' in jj and 'currency' in jj['estimatedSalary'] else None,
            'salaryOnDisplay': None
        }
        useful['jobRating'] = ';;;'.join(response.xpath('//*[@class="compactStars margRtSm"]/text()').extract())
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
                'lable': (jj['industry'] if 'industry' in jj else None)
            },
            'employmentType': (jj['employmentType'] if 'employmentType' in jj else None),
            'jobFunction[Id,Title]': None,
            'benefits': None
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': ';;;'.join(response.xpath('//*[@class="strong ib"]/text()').extract()),
                'companyWebsiteURL': (jj['hiringOrganization']['sameAs'] if 'hiringOrganization' in jj and 'sameAs' in jj['hiringOrganization'] else None),
                'companyOverview': None,
                'companyLogoUrls': (jj['hiringOrganization']['logo'] if  'hiringOrganization' in jj and 'logo' in jj['hiringOrganization'] else None)
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//*[@class="subtle ib"]/text()').extract())
        useful['postDate'] = jj['datePosted'] if 'datePosted' in jj else None
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = None
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//*[@class="jobDescriptionContent desc module pad noMargBot"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'Glassdoor'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # print((jj['industry'] if 'industry' in jj else None))
        # print(jj['hiringOrganization'])
        # print(jj['hiringOrganization']['sameAs'])
        # print(jj['hiringOrganization']['sameAs'])
        # print(jj['hiringOrganization']['logo'])
        # pprint.pprint(useful)
        # return
        return useful
