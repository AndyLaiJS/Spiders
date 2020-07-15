# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import json
import logging
import re
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.spiders.util import nomalizeListJobFunction
from jobs.helpers import fill_location_item


class EfcSpider(scrapy.Spider):
    name = 'efc'
    logging.info("Loading SoftSkillsExtractor")
    # ss_extractor = SoftSkillsExtractor()
    # logging.info("Loading GeneralSkillsExtractor")
    # gs_extractor = GeneralSkillsExtractor()
    # logging.info("Loading DutiesExtractor")
    # d_extractor = DutiesExtractor()

    def start_requests(self):
        start_urls = 'https://job-search-api.svc.dhigroupinc.com/v1/efc/jobs/search?locationPrecision=Country&latitude=22.3193039&longitude=114.1693611&countryCode2=HK&radius=100&radiusUnit=mi&page=0&pageSize=20&searchId=22ecef65-eb61-43da-86ca-256fe5d12914&facets=*&currencyCode=HKD&culture=en&interactionId=0'
        urls = []
        # change the range to get till which page
        for i in range(1, 500):
            tmp = start_urls.split('&')
            for j in range(len(tmp)):
                if "page=" in tmp[j]:
                    tmp[j] = tmp[j].split('=')[0] + "=" + str(i)
                if "interactionId=" in tmp[j]:
                    tmp[j] = tmp[j].split('=')[0] + "=" + str(i)
            urls.append('&'.join(tmp))
        print(urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,
                                 headers={"x-api-key": "zvDFWwKGZ07cpXWV37lpO5MTEzXbHgyL4rKXb39C"})

    allowed_domains = ['www.efinancialcareers.hk']

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)

        jsonresponse = json.loads(response.body_as_unicode())
        # Retruive Job Function Display name.
        meta = jsonresponse["meta"]
        sectorsDict = {}
        facetQueryResults = [x for x in meta["facetQueryResults"] if x["facetName"] == "sectors"]
        for x in facetQueryResults:
            for main_cate in x["facetResults"]:
                sectorsDict[main_cate["value"]] = f'{main_cate["displayValue"]}'
                children = main_cate["children"] if "children" in main_cate else []
                for sub_cate in children:
                    sectorsDict[sub_cate["value"]] = f'{main_cate["displayValue"]} ({sub_cate["displayValue"]})'

        for jj in jsonresponse['data']:
            print("I am jj:", jj)

            job_item = get_loader(JobItem(), response)

            job_id = "https://www.efinancialcareers.hk" + jj['detailsPageUrl']
            job_item.add_value('job_id', job_id)
            job_item.add_value('title', jj['title'])
            job_item.add_value('job_rating', None)

            # Get location (geocode)
            location_item = get_loader(LocationItem(), response)
            location = jj['jobLocation']['displayName']
            job_item.add_value('location', fill_location_item(location_item, location))

            job_item.add_value('post_date', jj['postedDate'])
            job_item.add_value('page_url', "https://www.efinancialcareers.hk" + jj['detailsPageUrl'])
            job_item.add_value('source', 'efc')
            job_item.add_value('summary', None)
            job_item.add_value('employment_type', (jj['employmentType'] if 'employmentType' in jj else None))

            # Normalize Job Function
            jobFuncList = []
            originJobList = jj['sectors'] if 'sectors' in jj else []
            for main_cate in originJobList:
                jobFuncList.append(f'{sectorsDict[main_cate]}')
            job_item.add_value('function', nomalizeListJobFunction(self.name, jobFuncList))

            job_item.add_value('benefits', None)
            job_item.add_value('fetch_date', datetime.now())

            salary_item = get_loader(SalaryItem(), response)
            salary_item.add_value('salary_on_display', (jj['salary'] if 'salary' in jj else None))

            requirement_item = get_loader(RequirementItem(), response)
            # TODO: turn these into numeric value
            requirement_item.add_value('career_level', (jj['positionType'] if 'positionType' in jj else None))

            company_item = get_loader(CompanyItem(), response)
            company_item.add_value('name', (jj['companyName'] if 'companyName' in jj else None))
            company_item.add_value('website_url', None)
            company_item.add_value('overview', None)
            company_item.add_value('logo_url', (jj['companyLogoUrl'] if 'companyLogoUrl' in jj else None))
            company_item.add_value('other_jobs_url', None)
            job_item.add_value('company', company_item.load_item())

            yield scrapy.Request(job_id, callback=self.parse_job,
                                 meta={'job_item': job_item, 'salary_item': salary_item,
                                       'requirement_item': requirement_item})

    def processSalary(self, salary):
        money = re.findall("[0-9,.]+[MKmk(\s?million)]?", salary)
        current = re.findall("[A-Z]{3}?", salary)
        mtype = re.findall("(?i)(month|year|hour|minute|yr|yrs|day|days|week|weeks|months|years|hours|minutes)", salary)
        maxx = 0
        minn = 0
        if (len(money) >= 2):
            maxx = money[1]
            minn = money[0]
        elif (len(money) == 1):
            maxx = money[0]
            minn = money[0]
        return {'moneymax': maxx, 'moneymin': minn, 'current': current, 'mtype': mtype}

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = response.meta.get('job_item')
        requirement_item = response.meta.get('requirement_item')
        salary_item = response.meta.get('salary_item')
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(), strict=False)

        job_item.add_value('body', jj['description'])
        job_item.add_value('industry', (jj['industry'] if 'industry' in jj else None))
        job_item.add_xpath('related_jobs', '//ul[@id="related-job-like-this-links"]//a/@href')

        # duties = self.d_extractor.extract(jj['description'])
        # job_item.add_value('duties', duties)

        requirement_item.add_value('years_of_experience', jj['experienceRequirements'])
        requirement_item.add_value('education_level', jj['educationRequirements'])
        # skills = self.gs_extractor.extract(jj['description'])
        # requirement_item.add_value('hard_skills', skills['hardskill'])
        # soft_skills = [skill.strip() for skill in self.ss_extractor.extract(jj['description']).split(";")]
        # requirement_item.add_value('soft_skills', list(set(soft_skills)))
        job_item.add_value('requirement', requirement_item.load_item())

        salary = jj['baseSalary']['value']
        salaryDict = self.processSalary(str(salary))
        salary_item.add_value('max', salaryDict['moneymax'])
        salary_item.add_value('min', salaryDict['moneymin'])
        salary_item.add_value('salary_type', salaryDict['mtype'])
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', salaryDict['current'])
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
