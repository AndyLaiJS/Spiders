# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
import json
import logging
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.helpers import fill_location_item


class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['www.glassdoor.com.hk']
    start_urls = ['https://www.glassdoor.com.hk/Job/kon-hang-jobs-SRCH_IL.0,8_IC2308639_IP1.htm']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="jlGrid hover"]//li/div[@class="jobContainer"]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))


        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            print("I am job ID:", job_id)
            job_url = "https://www.glassdoor.com.hk" + job_url
            print("Now working on JobURL", job_url)

            yield scrapy.Request(job_url, callback=self.parse_job)

        if '_IP' not in response.url:
            pages = response.url.replace('.htm', '_IP2.htm')
        else:
            a = int(response.url.split('_IP')[1].split('.')[0])
            pages = response.url.replace(f'_IP{a}.htm', f'_IP{a+1}.htm')
        print("I am pages:", pages)
        yield scrapy.Request(response.urljoin(pages), callback=self.parse)

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(),strict=False)

        joburl = "JV.htm".join(
            [response.url.split("JV_")[0], response.url.split(".htm")[-1]])  # Remove tracking part from the url
        job_item.add_value('job_id', joburl)
        job_item.add_xpath('title', '//*[@class="jobViewJobTitleWrap"]/h2/text()')
        job_item.add_xpath('job_rating', '//*[@class="compactStars margRtSm"]/text()')

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = ', '.join(
            [jj['jobLocation']['address']['addressLocality'], jj['jobLocation']['address']['addressCountry']['name']])
        latitude, longitude = jj['jobLocation']["geo"] if 'jobLocation' in jj and 'geo' in jj['jobLocation'] else (None, None)
        if latitude and longitude:
            location_item.add_value("raw_location", location)
            location_item.add_value("latitude", latitude)
            location_item.add_value("longitude", longitude)
        elif location:
            fill_location_item(location_item, location, add_hk=False)
        job_item.add_value('location', location_item.load_item())

        job_item.add_value('post_date', jj['datePosted'])
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'glassdoor')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//div[@id="JobDescriptionContainer"]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode").split("\n")
        body_lines[0] = body_lines[0][body_lines[0].rfind(";}") + 2:]  # Somehow some css code made it to the front
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_value('industry', (jj['industry'] if 'industry' in jj else None))
        job_item.add_value('employment_type', (jj['employmentType'] if 'employmentType' in jj else None))
        job_item.add_value('function', None)
        job_item.add_value('benefits', None)
        job_item.add_value('related_jobs', None)
        job_item.add_value('fetch_date', datetime.now())

        duties = self.d_extractor.extract(body_lines)
        job_item.add_value('duties', duties)

        requirement_item = get_loader(RequirementItem(), response)
        # TODO: turn these into numeric value
        requirement_item.add_value('career_level', None)
        requirement_item.add_value('years_of_experience', None)
        requirement_item.add_value('education_level', None)
        skills = self.gs_extractor.extract("\n".join(body_lines))
        requirement_item.add_value('hard_skills', skills['hardskill'])
        soft_skills = [skill.strip() for skill in self.ss_extractor.extract("\n".join(body_lines)).split(";")]
        requirement_item.add_value('soft_skills', list(set(soft_skills)))
        job_item.add_value('requirement', requirement_item.load_item())

        company_item = get_loader(CompanyItem(), response)
        company_item.add_xpath('name', '//*[@class="strong ib"]/text()')
        company_item.add_value('website_url', (jj['hiringOrganization']['sameAs'] if 'sameAs' in jj['hiringOrganization'] else None))
        company_item.add_value('overview', None)
        company_item.add_value('logo_url', (jj['hiringOrganization']['logo'] if 'logo' in jj['hiringOrganization'] else None))
        company_item.add_value('other_jobs_url', None)
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', (jj['estimatedSalary']['value']['maxValue'] if 'estimatedSalary' in jj and 'maxValue' in jj['estimatedSalary']['value'] else None))
        salary_item.add_value('min', (jj['estimatedSalary']['value']['minValue'] if 'estimatedSalary' in jj and 'minValue' in jj['estimatedSalary']['value'] else None))
        salary_item.add_value('salary_type', (jj['estimatedSalary']['value']['unitText'] if 'estimatedSalary' in jj and 'unitText' in jj['estimatedSalary']['value'] else None))
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', (jj['estimatedSalary']['currency'] if 'estimatedSalary' in jj and 'currency' in jj['estimatedSalary'] else jj['salaryCurrency']))
        salary_item.add_value('salary_on_display', None)
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
