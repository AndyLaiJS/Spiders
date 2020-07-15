# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
import json
import logging
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.helpers import fill_location_item


atpage = 0
class AdeccoSpider(scrapy.Spider):
    name = 'adecco'
    allowed_domains = ['www.adecco.com.hk']
    start_urls = ['https://www.adecco.com.hk/advancedsearch.aspx?search=1']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

    def parse(self, response):
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
                                                    formdata={'hfPageIndex': str(atpage), 'ctl00$ContentPlaceHolderLeftNav$ucJobSearchFilter1$hfPageIndex': str(atpage), 'hfSession': 'ngi43q0tehn4jv0irvlz2v42', '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$ucSearchResults1$rptPaging$ctl11$lnkButtonNext', '__EVENTARGUMENT': ''}, callback=self.parse)

        

    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)
        jj = json.loads(response.xpath('//script[@type="application/ld+json"]//text()').extract_first(), strict=False)

        job_item.add_value('job_id', response.url)
        job_item.add_xpath('title', '//*[@id="job-ad-title"]/h1/span/text()')
        job_item.add_value('job_rating', None)

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        location = '\n'.join(response.xpath('//*[@class="job-details__header__info job-details__header__info--location"]/p/span//text()').extract())
        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_value('post_date', jj['datePosted'])
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'adecco')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//*[@id="job-ad-description"]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_xpath('industry', '//*[contains(text(),"Client Industry")]/following-sibling::span/text()')
        job_item.add_xpath('employment_type', '//*[@class="job-details__header__info job-details__header__info--type"]/p/span/span/text()')
        job_item.add_xpath('function', '//*[@class="job-details__header__info job-details__header__info--industry"]/p/span/span/text()')
        job_item.add_xpath('benefits', '//*[@class="job-desc-deal-wrapper"]/div/div/div//li/text()')
        job_item.add_xpath('related_jobs', '//*[@class="jxt-similar-jobs-holder"]//li/a/@href')
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
        company_item.add_value('website_url', jj['hiringOrganization']['url'])
        company_item.add_value('overview', None)
        company_item.add_value('logo_url', jj['hiringOrganization']['logo'])
        company_item.add_value('other_jobs_url', None)
        job_item.add_value('company', company_item.load_item())

        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', (jj['baseSalary']['value']['maxValue'] if'maxValue' in jj['baseSalary']['value'] else None))
        salary_item.add_value('min', (jj['baseSalary']['value']['minValue'] if'minValue' in jj['baseSalary']['value'] else None))
        salary_item.add_value('salary_type', (jj['baseSalary']['value']['unitText'] if 'unitText' in jj['baseSalary']['value'] else None))
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', jj['baseSalary']['currency'])
        salary_item.add_xpath('salary_on_display', '//*[@class="job-details__header__info job-details__header__info--salary"]//span[@class="job-ad-optional-text"]/span/text()')
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
