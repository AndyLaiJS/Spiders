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


class CpjobsSpider(scrapy.Spider):
    name = 'cpjobs'
    allowed_domains = ['www.cpjobs.com']
    start_urls = ['https://www.cpjobs.com/hk/SearchJobs?sopt=2&c=1']
    # logging.info("Loading SoftSkillsExtractor")
    # ss_extractor = SoftSkillsExtractor()
    # logging.info("Loading GeneralSkillsExtractor")
    # gs_extractor = GeneralSkillsExtractor()
    # logging.info("Loading DutiesExtractor")
    # d_extractor = DutiesExtractor()

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="job_title"]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('/')[-1]
            print("I am job ID:", job_id)
            print("Now working on JobURL", job_url)

            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="next"]/a/@href').get()
        print("I am pages:", pages)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)
        job_item.add_value('job_id', response.url)
        job_item.add_value('title', jj['title'])
        job_item.add_value('job_rating', None)

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = '\n'.join(response.xpath('//th[contains(text(),"Location")]/../td/div/span/text()').extract())
        location = location.replace("Within ", "")
        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_value('post_date', jj['datePosted'])
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'cpjobs')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//div[@class="desc"]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_value('industry', jj['industry'] if 'industry' in jj else None)
        job_item.add_xpath('employment_type', '//th[contains(text(),"Employment type")]/../td/text()')
        job_item.add_value('function', nomalizeListJobFunction(self.name, jj['occupationalCategory'].split(", ")) if 'occupationalCategory' in jj else None)
        job_item.add_xpath('benefits', '//th[contains(text(),"Benefits")]/../td/text()')
        job_item.add_value('related_jobs', None)
        job_item.add_value('fetch_date', datetime.now())

        #duties = self.d_extractor.extract(body_lines)
        #job_item.add_value('duties', duties)

        requirement_item = get_loader(RequirementItem(), response)
        # TODO: turn these into numeric value
        requirement_item.add_xpath('career_level', '//th[contains(text(),"Job level")]/../td/text()')
        requirement_item.add_value('years_of_experience', (jj['experienceRequirements'] if 'experienceRequirements' in jj else None))
        requirement_item.add_value('education_level', (jj['educationRequirements'] if 'educationRequirements' in jj else None))
        #skills = self.gs_extractor.extract(body_lines)
        #requirement_item.add_value('hard_skills', skills['hardskill'])
        #soft_skills = [skill.strip() for skill in self.ss_extractor.extract(body_lines).split(";")]
        #requirement_item.add_value('soft_skills', list(set(soft_skills)))
        job_item.add_value('requirement', requirement_item.load_item())

        company_item = get_loader(CompanyItem(), response)
        company_item.add_value('name', jj['hiringOrganization']['name'])
        company_item.add_value('website_url', None)
        company_item.add_value('overview', (BeautifulSoup(jj['hiringOrganization']['description']).get_text().strip() if 'description' in jj['hiringOrganization'] else None))
        company_item.add_value('logo_url', (jj['hiringOrganization']['logo'] if 'logo' in jj['hiringOrganization']else None))
        company_item.add_xpath('other_jobs_url', '//*[@class="company"]/a/@href')
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', (jj['baseSalary']['maxvalue'] if 'baseSalary' in jj and 'maxvalue' in jj['baseSalary'] else None))
        salary_item.add_value('min', (jj['baseSalary']['minvalue'] if 'baseSalary' in jj and 'minvalue' in jj['baseSalary'] else None))
        salary_item.add_value('salary_type', (jj['baseSalary']['unitText'] if 'baseSalary' in jj and 'unitText' in jj['baseSalary'] else None))
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', (jj['baseSalary']['currency'] if 'baseSalary' in jj and 'currency' in jj['baseSalary'] else None))
        salary_item.add_xpath('salary_on_display', '//th[contains(text(),"Salary")]/../td/text()')
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()