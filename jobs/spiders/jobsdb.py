# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
from bs4 import BeautifulSoup
import json
import logging
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.spiders.util import nomalizeListJobFunction
from jobs.helpers import fill_location_item


class JobsdbSpider(scrapy.Spider):
    name = 'jobsdb'
    allowed_domains = ['hk.jobsdb.com']
    start_urls = ['https://hk.jobsdb.com/hk/en/Search/FindJobs?JSRV=1&page=1']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//h1[contains(@id, "jobCardHeading")]//a/@href').getall()
        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            print("I am job_URL", job_url)
            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//div[@data-automation="pagination"]//a/@href').getall()
        if pages:
            page = max(max(pages), max(pages, key=len), key=len)
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

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))

        job_item = get_loader(JobItem(), response)

        item = json.loads(response.xpath('//body/script[not(@*)]/text()').get().split(' = ')[1][:-1])['details']
        print('--------------------------------')
        print(item)

        job_item.add_value('job_id', response.url.split("?")[0]) # Remove tracking part from the url
        job_item.add_value('title', item['header']['jobTitle'])
        job_item.add_value('job_rating', item['header']['review']['rating'])

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = item['location'][0]['location']
        location = location.replace(" Area", "District")
        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_value('post_date', item['header']['postedDate'])
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'jobsdb')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//*[contains(text(),"Job Description")]/../following-sibling::div').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', item['jobDetail']['summary'])
        job_item.add_value('industry', item['jobDetail']['jobRequirement']['industryValue']['label'])
        job_item.add_value('employment_type', item['jobDetail']['jobRequirement']['employmentType'])

        # Normalize Job Function
        jobFuncList = []
        for main_cate in item['jobDetail']['jobRequirement']['jobFunctionValue']:
            for sub_cate in main_cate["children"]:
                jobFuncList.append(f'{main_cate["name"]} ({sub_cate["name"]})')
        job_item.add_value('function', nomalizeListJobFunction(self.name, jobFuncList))

        job_item.add_value('benefits', item['jobDetail']['jobRequirement']['benefits'])
        job_item.add_value('related_jobs', None)
        job_item.add_value('fetch_date', datetime.now())

        duties = self.d_extractor.extract(body_lines)
        job_item.add_value('duties', duties)

        requirement_item = get_loader(RequirementItem(), response)
        # TODO: turn these into numeric value
        requirement_item.add_value('career_level', item['jobDetail']['jobRequirement']['careerLevel'])
        requirement_item.add_value('years_of_experience', item['jobDetail']['jobRequirement']['yearsOfExperience'])
        requirement_item.add_value('education_level', item['jobDetail']['jobRequirement']['qualification'])
        skills = self.gs_extractor.extract(body_lines)
        requirement_item.add_value('hard_skills', skills['hardskill'])
        soft_skills = [skill.strip() for skill in self.ss_extractor.extract(body_lines).split(";")]
        requirement_item.add_value('soft_skills', list(set(soft_skills)))
        job_item.add_value('requirement', requirement_item.load_item())

        company_item = get_loader(CompanyItem(), response)
        company_item.add_value('name', item['header']['company']['name'])
        company_item.add_value('website_url', item['companyDetail']['companyWebsite'],)
        company_item.add_value('overview', BeautifulSoup(item['companyDetail']['companyOverview']['html']).get_text().strip())
        company_item.add_value('logo_url', item['header']['company']['url'])
        company_item.add_value('other_jobs_url', [x['jobUrl'] for x in item['relatedJobs']])
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', item['header']['salary']['max'],)
        salary_item.add_value('min', item['header']['salary']['min'],)
        salary_item.add_value('salary_type', item['header']['salary']['type'],)
        salary_item.add_value('extra_info', item['header']['salary']['extraInfo'],)
        salary_item.add_value('currency', item['header']['salary']['currency'],)
        salary_item.add_value('salary_on_display', item['header']['salary']['salaryOnDisplay'])
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
