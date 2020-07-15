# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
import logging
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.helpers import fill_location_item


class JoraSpider(scrapy.Spider):
    name = 'jora'
    allowed_domains = ['hk.jora.com']
    start_urls = ['https://hk.jora.com/j?l=Hong+Kong&q=&sp=homepage&st=date']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

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

            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="next_page next trackable"]/@href').get()
        print("I am pages:", pages)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)

        jobFunc = []
        jobIndustry = []
        for i in response.xpath('//*[@class="summary"]/text()').extract():
            if "Job Specialization" in i:
                jobFunc.append(str(i))
        for i in response.xpath('//*[@class="summary"]/text()').extract():
            if "Company Industry" in i:
                jobIndustry.append(str(i))

        job_item.add_value('job_id', response.url.split("?")[0])    # Remove tracking part from the url
        job_item.add_xpath('title', '//div[@class="job_info"]/h1/text()')
        job_item.add_value('job_rating', None)

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = '\n'.join(response.xpath('//div[@class="job_info"]/span[@class="location"]/text()').extract())
        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_xpath('post_date', '//*[@class="date"]/text()')
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'jora')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//*[@class="job_info"]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_value('industry', jobIndustry)
        job_item.add_xpath('employment_type', '//div[@class="job_info"]/p[@class="additional_info"]/text()')
        job_item.add_value('function', jobFunc)
        job_item.add_xpath('benefits', '//p/strong[contains(text(),"Benefits:")]/../following-sibling::ul//li/text()')
        job_item.add_value('related_jobs', None)
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
        company_item.add_xpath('name', '//div[@class="job_info"]/span[@class="company"]/text()')
        company_item.add_value('website_url', None)
        company_item.add_value('overview', None)
        company_item.add_value('logo_url', None)
        company_item.add_value('other_jobs_url', None)
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', None)
        salary_item.add_value('min', None)
        salary_item.add_value('salary_type', None)
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', None)
        salary_item.add_value('salary_on_display', None)
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
