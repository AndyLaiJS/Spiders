# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime


class CtgoodjobsSpider(scrapy.Spider):
    name = 'ctgoodjobs'
    allowed_domains = ['www.ctgoodjobs.hk']
    start_urls = ['https://www.ctgoodjobs.hk/ctjob/listing/joblist.asp?page=1']

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="joblist content"]//div/div[@class="jl-title"]/h2/a/@href').extract()
        pages = response.url.split('=')[0] + "=" + str(int(response.url.split('=')[1]) + 1)
        print("I am pages:", pages)
        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('/')[-2]
            print("I am job ID:", job_id)
            job_url = "https://www.ctgoodjobs.hk" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.url.split('=')[0] + "=" + str(int(response.url.split('=')[1]) + 1)
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
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(), strict=False)
        useful = dict()
        tmp = response.xpath('//*[@id="page-top"]/div[2]/div[2]/div/div/div[2]/div/div/div[1]/a/@href').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = "https://www.ctgoodjobs.hk" + tmp[0]
        else:
            useful['applyLink'] = "https://www.ctgoodjobs.hk" + tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//h1[@class="job-title"]/text()').extract())
        useful['salary'] = {
            'max': (jj['baseSalary']['value']['maxValue'] if 'maxValue' in jj['baseSalary']['value'] else None),
            'min': (jj['baseSalary']['value']['minValue'] if 'minValue' in jj['baseSalary']['value'] else None),
            'type': (jj['baseSalary']['unitText'] if 'unitText' in jj['baseSalary'] else None),
            'extraInfo': None,
            'currency': jj['baseSalary']['currency'],
            'salaryOnDisplay': ';;;'.join(response.xpath('//td[contains(text(),"Salary")]/../td/ul/li/text()').extract())
        }
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = None
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': ';;;'.join(response.xpath('//td[contains(text(),"Career Level")]/../td/ul/li/text()').extract()),
                'yearsOfExperience': ';;;'.join(response.xpath('//td[contains(text(),"Experience")]/../td/ul/li/text()').extract()),
                'educationLevel': ';;;'.join(response.xpath('//td[contains(text(),"Education")]/../td/ul//li/text()').extract()),
                'skills': response.xpath('//*[@class="jd-sec skill-tag"]/ul//li/a/text()').extract()
            },
            'industryValue': {
                'value': None,
                'lable': ';;;'.join(response.xpath('//td[contains(text(),"Industry")]/../td/ul/li/a//text()').extract()).split('/')
            },
            'employmentType': ';;;'.join(response.xpath('//td[contains(text(),"Employment Term")]/../td/ul/li/text()').extract()),
            'jobFunction[Id,Title]': response.xpath('//td[contains(text(),"Job Function")]/../td/ul/li/a//text()').extract(),
            'benefits': [x for x in response.xpath('//*[@class="row benefit-list"]//text()').extract() if x!= "\r\n"]
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': ';;;'.join(response.xpath('//*[@id="company_name"]/text()').extract()),
                'companyWebsiteURL': None,
                'companyOverview': response.xpath('//*[@class="comp-desc"]//text()').extract(),
                'companyLogoUrls': (jj['hiringOrganization']['logo'] if 'logo' in jj['hiringOrganization'] else None)
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = response.xpath('//td[contains(text(),"Location")]/../td/ul/li/text()').extract()
        useful['postDate'] = jj['datePosted']
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = None
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//div[@class="jd-sec job-desc"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'ctgoodjobs'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        
        # pprint.pprint(jj)
        # pprint.pprint(useful)
        return useful
