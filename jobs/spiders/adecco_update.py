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
atpage = 0
class AdeccoUpdateSpider(CrawlSpider):
    name = 'adecco_update'
    allowed_domains = ['www.adecco.com.hk']
    start_urls = ['https://www.adecco.com.hk']
    rules = (
        Rule(LinkExtractor(allow=('advancedsearch\.aspx\?', )),
             callback='parse_item'),
    )

    # def parse_topLink(self, response):
    #     logging.debug('Parsing top page: {url}'.format(url=response.url))
    #     yield scrapy.Request(response.url, callback=self.parse_item)

    def parse_item(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        try:
            print("I am cookie:", response.headers.getlist("Set-Cookie"))
            print("I am meta:", response.request.meta)
        except:
            pass
        jobs_urls = response.xpath('//*[@id="resultsList"]//div/div[1]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_urls)))
        for job_url in jobs_urls:
            job_id = job_url.split('/')[-1]
            print("I am job ID:", job_id)
            job_url = "https://www.adecco.com.hk" + job_url
            print("Now working on JobURL", job_url)

            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
            yield scrapy.Request(job_url, callback=self.parse_job)
        global atpage
        atpage += 1
        print("Next Page will be:", atpage)
        yield scrapy.http.FormRequest.from_response(response, formname="aspnetForm", dont_filter=True, meta={'hfPageIndex': str(atpage)},
                                                    formdata={'hfPageIndex': str(atpage), 'ctl00$ContentPlaceHolderLeftNav$ucJobSearchFilter1$hfPageIndex': str(atpage), 'hfSession': 'ngi43q0tehn4jv0irvlz2v42', '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ucSearchResults1$rptPaging$ctl11$lnkButtonNext', '__EVENTARGUMENT': ''}, callback=self.parse_item)

        

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        useful = dict()
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)
        tmp = response.xpath('//*[@class="apply-now-link"]/a/@href').extract()
        if tmp == []:
            useful['applyLink'] = response.url
        elif type(tmp) == list:
            useful['applyLink'] = "https://www.adecco.com.hk"+tmp[0]
        else:
            useful['applyLink'] = tmp
        useful['jobId'] = response.url
        useful['jobTitle'] = ';;;'.join(response.xpath('//*[@id="job-ad-title"]/h1/span/text()').extract())
        useful['salary'] = {
            'max': (jj['baseSalary']['value']['maxValue'] if'maxValue' in jj['baseSalary']['value'] else None),
            'min': (jj['baseSalary']['value']['minValue'] if'minValue' in jj['baseSalary']['value'] else None),
            'type': (jj['baseSalary']['value']['unitText'] if 'unitText' in jj['baseSalary']['value'] else None),
            'extraInfo': None,
            'currency': jj['baseSalary']['currency'],
            'salaryOnDisplay': ';;;'.join(response.xpath('//*[@class="job-details__header__info job-details__header__info--salary"]//span[@class="job-ad-optional-text"]/span/text()').extract())
        }
        
        useful['jobRating'] = None
        useful['numberOfAppliant(FromLinkedIn)'] = None
        useful['jobDetail'] = {
            'summary': None,
            'jobDescription': "",
            'jobRequirement': {
                'careerLevel': None,
                'yearsOfExperience': None,
                'educationLevel': None,
                'skills': jj['skills']
            },
            'industryValue': {
                'value': None,
                'lable': ';;;'.join(response.xpath('//*[contains(text(),"Client Industry")]/following-sibling::span/text()').extract())
            },
            'employmentType': ';;;'.join(response.xpath('//*[@class="job-details__header__info job-details__header__info--type"]/p/span/span/text()').extract()),
            'jobFunction[Id,Title]': ';;;'.join(response.xpath('//*[@class="job-details__header__info job-details__header__info--industry"]/p/span/span/text()').extract()),
            'benefits': response.xpath('//*[@class="job-desc-deal-wrapper"]/div/div/div//li/text()').extract()
        }
        useful['companyDetails']= {
            'companyId': None,
            'companyDetail': {
                'name': jj['hiringOrganization']['name'],
                'companyWebsiteURL': jj['hiringOrganization']['url'],
                'companyOverview': None,
                'companyLogoUrls': jj['hiringOrganization']['logo']
            }
        }
        # useful['companyName'] = response.xpath('//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()').extract()
        useful['location'] = ';;;'.join(response.xpath('//*[@class="job-details__header__info job-details__header__info--location"]/p/span//text()').extract())
        useful['postDate'] = jj['datePosted']
        useful['moreJobsFromThisCompany'] = None
        useful['relatedJobs'] = response.xpath('//*[@class="jxt-similar-jobs-holder"]//li/a/@href').extract()
        # useful['employmentTerm'] = response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()').extract()
        # useful['benefit'] = response.xpath('//*[contains(text(),"Benefits")]/text()').extract()
        useful['mainBody'] = ';;;'.join(response.xpath('//*[@id="job-ad-description"]//text()').extract())
        useful['pageUrl'] = response.url
        useful['source'] = 'Adecco'
        useful['dataFetchDate'] = str(datetime.datetime.now())
        # pprint.pprint(useful)
        return useful
