# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging
import pprint
import datetime
import time

atpage = 0
class RecruithkSpider(scrapy.Spider):
    name = 'recruithk'
    allowed_domains = ['www.recruit.com.hk']
    start_urls = ['https://www.recruit.com.hk/job-category/會計-審計-accounting-auditing/11000',
                  'https://www.recruit.com.hk/job-category/行政-秘書-administration-secretary/12000',
                  'https://www.recruit.com.hk/job-category/航空-旅遊-觀光-airline-travel-tourism/47000',
                  'https://www.recruit.com.hk/job-category/銀行-金融-證券-banking-finance-securities/13000',
                  'https://www.recruit.com.hk/job-category/樓宇-建築-building-architectural/14000',
                  'https://www.recruit.com.hk/job-category/餐飲-catering/23000',
                  'https://www.recruit.com.hk/job-category/客戶服務-customer-service/17000',
                  'https://www.recruit.com.hk/job-category/設計-design/18000',
                  'https://www.recruit.com.hk/job-category/教育-education/19000',
                  'https://www.recruit.com.hk/job-category/工程-engineering/20000',
                  'https://www.recruit.com.hk/job-category/應屆畢業生-fresh-graduate/53450',
                  'https://www.recruit.com.hk/job-category/政府-government/53700',
                  'https://www.recruit.com.hk/jobseeker/JobSearchResult.aspx?searchPath=D&jobLocList=56243',
                  'https://www.recruit.com.hk/job-category/保健-美容-health-beauty/22000',
                  'https://www.recruit.com.hk/job-category/醫院-醫療-醫藥-hospital-medical-pharmaceutical/30000',
                  'https://www.recruit.com.hk/job-category/款待-酒店-hospitality-hotel/53460',
                  'https://www.recruit.com.hk/job-category/人力資源-human-resources/24000',
                  'https://www.recruit.com.hk/job-category/保險-insurance/25000',
                  'https://www.recruit.com.hk/job-category/資訊科技-it/26000',
                  'https://www.recruit.com.hk/job-category/物流-運輸-船務-logistics-transportation-shipping/28000',
                  'https://www.recruit.com.hk/job-category/管理-management/21000',
                  'https://www.recruit.com.hk/job-category/製造-manufacturing/29000',
                  'https://www.recruit.com.hk/job-category/市場營銷-公共關係-marketing-public-relations/41000',
                  'https://www.recruit.com.hk/job-category/媒體-media/15000',
                  'https://www.recruit.com.hk/job-category/採購-merchandising-purchasing/31000',
                  'https://www.recruit.com.hk/job-category/非政府組織-社會服務-ngo-social-services/53600',
                  'https://www.recruit.com.hk/job-category/其他-others/48000',
                  'https://www.recruit.com.hk/job-category/兼職-臨時工作-part-time-temporary-job-contract/53480',
                  'https://www.recruit.com.hk/job-category/專業服務-professional-services/27000',
                  'https://www.recruit.com.hk/job-category/物業-物業管理-保安-property-estate-management-security/32000',
                  'https://www.recruit.com.hk/job-category/出版-印刷-publishing-printing/33000',
                  'https://www.recruit.com.hk/job-category/質量保證-控制及測試-quality-assurance-control-testing/34000',
                  'https://www.recruit.com.hk/jobseeker/Recruitmentday.aspx',
                  'https://www.recruit.com.hk/job-category/零售-retail/43000',
                  'https://www.recruit.com.hk/job-category/銷售-sales/44000',
                  'https://www.recruit.com.hk/job-category/科學-實驗室-研究及開發-sciences-lab-r-d/54000',
                  'https://www.recruit.com.hk/jobseeker/JobSearchResult.aspx?searchPath=K&keyword=summer']


    def switch(self, a, b):
        if (a == []):
            return ';;;'.join(b)
        else:
            return ';;;'.join(a)

    def switchx(self, a, b):
        if (a == []):
            return b
        else:
            return a


    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="title-company-col"]/a[1]/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('/')[-1]
            print("I am job ID:", job_id)
            job_url = "https://www.recruit.com.hk" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)
        print("I am next Page:", response.xpath('//*[@class="next-page PageNumber"]/@href').get(), atpage)
        
        yield scrapy.http.FormRequest.from_response(response, formname="form1", dont_filter=True,
                                                    formdata={'__EVENTTARGET': 'pagerBottom$ctl02$ctl00', '__EVENTARGUMENT': ''}, callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        useful = dict()
        jj = dict()
        try:
            jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)
        except:
            print('NO json for this job')
        tmp = response.xpath('//*[@id="viewJobButtonLinkContainer"]//a/@href').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = tmp[0]
        else:
            useful['applyLink'] = tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = (jj['title'] if 'title' in jj else None)
        useful['salary'] = {
            'max': (jj['baseSalary']['value']['minValue'] if 'baseSalary' in jj and 'value' in jj['baseSalary'] and 'minValue' in jj['baseSalary']['value'] else None),
            'min': (jj['baseSalary']['value']['maxValue'] if 'baseSalary' in jj and 'value' in jj['baseSalary'] and 'maxValue' in jj['baseSalary']['value'] else None),
            'type': (jj['baseSalary']['value']['unitText'] if 'baseSalary' in jj and 'value' in jj['baseSalary'] and 'unitText' in jj['baseSalary']['value'] else None),
            'extraInfo': None,
            'currency': jj['baseSalary']['currency'] if 'baseSalary' in jj and 'currency' in jj['baseSalary'] else None,
            'salaryOnDisplay': self.switch(response.xpath('//*[@id="jobDetail_salaryLabel"]/text()').extract(), response.xpath('//*[@id="salaryLabel"]//text()').extract())
        }
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = None
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': self.switch(response.xpath('//*[@id="jobDetail_jobPosLvlLabel"]/text()').extract(), response.xpath('//*[@id="jobPosLevelLab"]//text()').extract()),
                'yearsOfExperience': self.switch(response.xpath('//*[@id="jobDetail_workExpLabel"]/text()').extract(), response.xpath('//*[@id="workExpLabel"]//text()').extract()),
                'educationLevel': self.switch(response.xpath('//*[@id="jobDetail_eduLevelLabel"]/text()').extract(), response.xpath('//*[@id="eduLevelLabel"]//text()').extract()),
                'skills': None
            },
            'industryValue': {
                'value': None,
                'lable': self.switch(response.xpath('//*[@id="jobDetail_jobIndustryLabel"]/text()').extract(), response.xpath('//*[@id="industryLab"]//text()').extract()).split('/')
            },
            'employmentType': self.switch(response.xpath('//*[@id="jobDetail_employmentTypeLabel"]/text()').extract(), response.xpath('//*[@id="employmentTermLab"]//text()').extract()),
            'jobFunction[Id,Title]': self.switch(response.xpath('//div[contains(@id,"jobDetail_jobCatFunc")]/div/a/text()').extract(), response.xpath('//li[contains(@id,"jobCatFunc")]/span/a/text()').extract()).split('/'),
            'benefits': self.switchx(response.xpath('//ul[@id="benefits_list"]//li/span/text()').extract(), response.xpath('//*[@class="jobad_benefits_list"]//li/span/text()').extract())
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': jj['hiringOrganization']['name'] if 'hiringOrganization' in jj and 'name' in jj['hiringOrganization'] else None,
                'companyWebsiteURL': None,
                'companyOverview': self.switch(response.xpath('//span[@id="jobDetail_companyProfileLabel"]/p//text()').extract(), response.xpath('//*[@id="aboutDiv"]//text()').extract()),
                'companyLogoUrls': jj['hiringOrganization']['logo'] if 'hiringOrganization' in jj and 'logo' in jj['hiringOrganization'] else None
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = jj['jobLocation'] if 'jobLocation' in jj else None
        useful['postDate'] = jj['datePosted'] if 'datePosted' in jj else None
        useful['moreJobsFromThisCompany'] = self.switchx(response.xpath(
            '//*[@id="jobOtherOpenning_jobOtherOpenningDiv"]/table//tr//a/@href').extract(), response.xpath('//*[@id="MoreJobs1_jobOtherOpenningDiv"]//a/@href').extract())
        useful['relatedJobs'] = None
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath("//div[@id='job_detail']//text()").extract().strip())
        useful['pageUrl'] = response.url
        useful['source'] = 'recuit.hk'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        print("\n\n\n")
        print(useful['location'])
        print("\n\n\n")
        # pprint.pprint(useful)
        return useful
