# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime


class RandstadSpider(scrapy.Spider):
    name = 'randstad'
    allowed_domains = ['www.randstad.com']
    start_urls = ['https://www.randstad.com/jobs/']

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@id="ctl06_ctl05_JobResultsDiv"]/article/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('/')[-1]
            print("I am job ID:", job_id)
            job_url = "https://www.randstad.com" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//a[@id="ctl06_ctl05_NextPageHyperLink"]/@href').get()
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
        jj = dict()
        try:
            jj = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').extract()[1],strict=False)
        except:
            print("No json for this Job")
        pprint.pprint(jj) 
        tmp = response.xpath('//*[@id="ctl06_ctl05_ApplyBottomHyperLink"]/@href').extract()
        if tmp == []:
            useful['applyLink'] =  response.url
        elif type(tmp) == list:
            useful['applyLink'] = "https://www.randstad.com" + tmp[0]
        else:
            useful['applyLink'] = tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//*[@id="js_jobTitle"]/text()').extract())
        useful['salary'] = {
            'max': (jj['baseSalary']['value']['maxValue'] if ('baseSalary' in jj and 'maxValue' in jj['baseSalary']['value']) else None),
            'min': (jj['baseSalary']['value']['minValue'] if ('baseSalary' in jj and 'minValue' in jj['baseSalary']['value']) else None),
            'type': (jj['baseSalary']['value']['unitText'] if ('baseSalary' in jj and 'unitText' in jj['baseSalary']['value']) else None),
            'extraInfo': None,
            'currency': (jj['baseSalary']['currency'] if 'baseSalary' in jj else None),
            'salaryOnDisplay': ';;;'.join(response.xpath('//*[@id="js_jobSalary"]/text()').extract())
        }
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = None
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': None,
                'yearsOfExperience': (jj['experienceRequirements'] if 'experienceRequirements' in jj else None),
                'educationLevel': (jj['educationRequirements'] if 'educationRequirements' in jj else None),
                'skills': [(jj['skills'] if 'skills' in jj else None)]+ [(jj['qualifications'] if 'qualifications' in jj else None)]
            },
            'industryValue': {
                'value': None,
                'lable': response.xpath('//*[@id="ctl06_ctl05_SectorLabel"]/text()').extract()
            },
            'employmentType': response.xpath('//*[@id="js_jobType"]/text()').extract()[0],
            'jobFunction[Id,Title]': ';;;'.join(response.xpath('//*[@id="ctl06_ctl05_SectorLabel"]/text()').extract()).split(','),
            'benefits': None
        }
        useful['companyDetails']: {
            'companyId': None,
            'companyDetail': {
                'name': None,
                'companyWebsiteURL': None,
                'companyOverview': None,
                'companyLogoUrls': None
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//*[@class="js_locationLabel"]/text()').extract())
        useful['postDate'] = jj['datePosted'] if 'datePosted' in jj else None
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = response.xpath('//*[@class="job-search-jobs-listing-more"]/div/ul//li/a/@href').extract()
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//*[@id="js_description"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'randstad'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # pprint.pprint(useful)
        return useful
