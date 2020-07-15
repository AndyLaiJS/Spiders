# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
import json
import logging
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.spiders.util import nomalizeListJobFunction
from jobs.helpers import fill_location_item


class MichaelpageSpider(scrapy.Spider):
    name = 'michaelpage'
    allowed_domains = ['www.michaelpage.com.hk']
    start_urls = ['https://www.michaelpage.com.hk/jobs?sort_by=most_recent&page-index=0']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="view-content"]/ul//li//a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('/')[-1]
            print("I am job ID:", job_id)
            job_url = "https://www.michaelpage.com.hk" + job_url
            print("Now working on JobURL", job_url)

            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="pager-show-more-next first last"]/a/@href').get()
        print("I am pages:", pages)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)

        job_item.add_value('job_id', response.url)
        job_item.add_xpath('title', '//*[@class="job-header"]/h1/text()')
        job_item.add_value('job_rating', None)

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = '\n'.join(response.xpath('//span[contains(text(),"Location:")]/following-sibling::span/text()').extract())
        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_value('post_date', jj['datePosted'])
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'michaelpage')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//div[@id="content-area"]//*[not(@type="application/ld+json")]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_xpath('industry', '//span[contains(text(),"Industry:")]/following-sibling::span/a/text()')
        job_item.add_xpath('employment_type', '//span[contains(text(),"Contract Type:")]/following-sibling::span/a/text()')

        # Normalize Job Function
        main_cat = response.xpath('//span[contains(text(),"Function:")]/following-sibling::span/a/span/text()').extract()[0]
        sub_cat = " (" + response.xpath('//span[contains(text(),"Specialisation:")]/following-sibling::span/a/text()').extract()[0] + ")"
        jobFuncList = [main_cat + sub_cat]
        job_item.add_value('function', nomalizeListJobFunction(self.name, jobFuncList))

        job_item.add_xpath('benefits', '//*[@class="job-desc-deal-wrapper"]/div/div/div//li/text()')
        job_item.add_xpath('related_jobs', '//*[@class="suggested-job job-item"]//div[@class="job-view-link view-link"]/span/@data-url')
        job_item.add_value('fetch_date', datetime.now())

        duties = self.d_extractor.extract(body_lines)
        job_item.add_value('duties', duties)

        requirement_item = get_loader(RequirementItem(), response)
        # TODO: turn these into numeric value
        requirement_item.add_value('career_level', None)
        requirement_item.add_value('years_of_experience', None)
        requirement_item.add_value('education_level', None)
        skills = self.gs_extractor.extract(body_lines)
        requirement_item.add_value('hard_skills', skills['hardskill'])
        soft_skills = [skill.strip() for skill in self.ss_extractor.extract(body_lines).split(";")]
        requirement_item.add_value('soft_skills', list(set(soft_skills)))
        job_item.add_value('requirement', requirement_item.load_item())

        company_item = get_loader(CompanyItem(), response)
        company_item.add_value('name', jj['hiringOrganization']['name'])
        company_item.add_value('website_url', jj['hiringOrganization']['sameAs'])
        company_item.add_value('overview', None)
        company_item.add_value('logo_url', jj['hiringOrganization']['logo'])
        company_item.add_value('other_jobs_url', None)
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', (jj['baseSalary']['value']['maxValue'] if 'baseSalary' in jj else None))
        salary_item.add_value('min', (jj['baseSalary']['value']['minValue'] if 'baseSalary' in jj else None))
        salary_item.add_value('salary_type', (jj['baseSalary']['value']['unitText'] if 'baseSalary' in jj else None))
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', (jj['baseSalary']['currency'] if 'baseSalary' in jj else None))
        salary_item.add_xpath('salary_on_display', '//*[@id="block-mp-jobs-structure-mp-job-summary-block"]/div/div//span[contains(text(),"Salary")]/../span[2]/text()')
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
