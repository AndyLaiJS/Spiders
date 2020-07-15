# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime


class JoraUpdateSpider(scrapy.Spider):
    name = 'jora_update'
    allowed_domains = ['hk.jora.com']
    start_urls = ['https://hk.jora.com/j?l=Hong+Kong&q=&sp=homepage&st=date','https://hk.jora.com/Manager-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Sales-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Assistant-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Merchandiser-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Assistant-Manager-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Sales-Executive-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Marketing-Executive-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Accountant-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Officer-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Clerk-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Jpc-Texson-Ltd-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Hkpropertyjobs.com-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Hkmanagerjobs-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Hktutorjobs.com-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Hkcsjobs.com-jobs-in-Hong-Kong?st=date',
                  'https://hk.jora.com/Randstad-Hong-Kong-Limited-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Aia-International-Limited-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Easy-Job-Centre-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Hkrestaurantjobs.com-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/Page-Personnel-jobs-in-Hong-Kong?st=date', 'https://hk.jora.com/jobs-in-Kwun-Tong,-Kowloon-Peninsula?st=date', 'https://hk.jora.com/jobs-in-Wan-Chai,-Hong-Kong-Island?st=date', 'https://hk.jora.com/jobs-in-Tsim-Sha-Tsui,-Kowloon-Peninsula?st=date', 'https://hk.jora.com/jobs-in-Tsuen-Wan,-New-Territories?st=date', 'https://hk.jora.com/jobs-in-Sha-Tin,-New-Territories?st=date', 'https://hk.jora.com/jobs-in-Causeway-Bay,-Hong-Kong-Island?st=date', 'https://hk.jora.com/jobs-in-Kowloon,-Kowloon-Peninsula?st=date', 'https://hk.jora.com/jobs-in-Lai-Chi-Kok,-Kowloon-Peninsula?st=date', 'https://hk.jora.com/jobs-in-Quarry-Bay,-Hong-Kong-Island?st=date']

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@id="jobresults"]//li/div/div/h2/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            print("I am job ID:", job_id)
            job_url = "https://hk.jora.com" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="next_page next trackable"]/@href').get()
        print("I am pages:", pages)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse)

        # if pages:
        #     page = max(max(pages), max(pages, key=len), key=len)
        #     print("I am page:", page)
        #     logging.debug('Going to: ' + response.urljoin(page))
        #     yield scrapy.Request(response.urljoin(page), callback=self.parse)
        # else:
        #     split_url = response.url.split('=')
        #     try:
        #         page_num = int(split_url[-1])
        #     except:
        #         logging.debug('No next page: ' + response.url)
        #         return scrapy.Request('')
        #     else:
        #         page_num += 1
        #         split_url[-1] = str(page_num)
        #         next_url = '='.join(split_url)
        #         logging.debug('No next button, going to: ' + next_url)
        #         yield scrapy.Request(next_url, callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        useful = dict()
        tmp = response.css('a.button.apply_link::attr(href)').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = "https://hk.jora.com" + tmp[0]
        else:
            useful['applyLink'] = tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//div[@class="job_info"]/h1/text()').extract())
        useful['salary'] = {
            'max': None,
            'min': None,
            'type': None,
            'extraInfo': None,
            'currency': None,
            'salaryOnDisplay': None
        }
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = None
        jobFunc = []
        jobIndustry = []
        for i in response.xpath('//*[@class="summary"]/text()').extract():
            if "Job Specialization" in i:
                jobFunc.append(str(i))
        for i in response.xpath('//*[@class="summary"]/text()').extract():
            if "Company Industry" in i:
                jobIndustry.append(str(i))
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
                'lable': jobIndustry
            },
            'employmentType': ';;;'.join(response.xpath('//div[@class="job_info"]/p[@class="additional_info"]/text()').extract()),
            'jobFunction[Id,Title]': jobFunc,
            'benefits': response.xpath('//p/strong[contains(text(),"Benefits:")]/../following-sibling::ul//li/text()').extract()
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': ';;;'.join(response.xpath('//div[@class="job_info"]/span[@class="company"]/text()').extract()),
                'companyWebsiteURL': None,
                'companyOverview': None,
                'companyLogoUrls': None
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//div[@class="job_info"]/span[@class="location"]/text()').extract())
        useful['postDate'] = ';;;'.join(response.xpath('//*[@class="date"]/text()').extract())
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = None
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//*[@class="job_info"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'Jora'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # pprint.pprint(useful)
        return useful
