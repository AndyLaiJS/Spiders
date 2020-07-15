# -*- coding: utf-8 -*-
import scrapy
import lxml.html
from datetime import datetime
import logging
import re
from jobs.items import get_loader, JobItem, RequirementItem, SalaryItem, CompanyItem, LocationItem
from jobs.extraction import SoftSkillsExtractor, GeneralSkillsExtractor, DutiesExtractor
from jobs.helpers import fill_location_item


class IndeedUpdateSpider(scrapy.Spider):
    name = 'indeed_update'
    allowed_domains = ['indeed.hk']
    start_urls = ['https://www.indeed.hk/jobs?l=Hong+Kong&sort=date&start=0', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=fulltime&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=parttime&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=permanent&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=temporary&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=contract&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=internship&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=commission&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&jt=volunteer&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Kwun+Tong,+Kowloon&jlid=c84e584841d910fb&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Tsim+Sha+Tsui,+Kowloon&jlid=4d3ba1badd9958d9&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Kwai+Chung,+New+Territories&jlid=ea48113c1e3d7ae1&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Central,+Hong+Kong+Island&jlid=b41248b61bd5792b&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Wan+Chai,+Hong+Kong+Island&jlid=0782c69a0c67dfbf&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Eastern+District,+Hong+Kong+Island&jlid=d27dfed797ad2286&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Lai+Chi+Kok,+Kowloon&jlid=2c86b78eb921932b&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Kowloon+Bay,+Kowloon&jlid=4972ee2b043fadd8&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Causeway+Bay,+Hong+Kong+Island&jlid=ce471c5cf4425fbe&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Mong+Kok,+Kowloon&jlid=1b80cd239b06a540&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Yau+Tsim+Mong+District,+Kowloon&jlid=84d0e0e00c0826c2&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Ngau+Tau+Kok,+Kowloon&jlid=d72983e7623da887&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Hung+Hom,+Kowloon&jlid=fa07241262383e04&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=Sheung+Wan,+Hong+Kong+Island&jlid=42d3d38065198058&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbl=San+Po+Kong,+Kowloon&jlid=a3867a20cfa362e3&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Easy+Job+Centre&jcid=9569c3c2b5b79e0e&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Gold+Personnel&jcid=d0b4d96f179f9cce&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Ocean+Park&jcid=48abc16dbd98419d&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=HSBC&jcid=04c9b139c84ea1b5&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Page+Personnel&jcid=e5ea1ff710ce39ca&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Michael+Page&jcid=77087bd1709a8148&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Adecco&jcid=fa101182bd51b2ce&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=AGroup+Company&jcid=276fcd54c38341cb&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Adecco+Hong+Kong&jcid=9779d4bcb77cd347&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Reeracoen+Hong+Kong&jcid=abceaea097181e69&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Hong+Kong+University&jcid=4101b27de861d291&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=SUPER+Corporate+Consultancy+Group&jcid=970825c9e106a8c4&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=Hillman+Ross&jcid=a780f01b2e1efe2d&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=KOS+International+Limited&jcid=aa207b9300cdbd0f&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbc=TOPLINK+COMPANY&jcid=6a6d2eb47be062c3&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E6%96%87%E5%93%A1&jtid=48daf7ca06b9421f&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E5%80%89%E5%8B%99%E5%93%A1&jtid=88aed03ecebc6bd8&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E8%A1%8C%E6%94%BF%E5%8A%A9%E7%90%86&jtid=7b340afeea28e110&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E6%8E%A5%E5%BE%85%E5%93%A1&jtid=0f430f9c534745f9&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E6%9C%83%E8%A8%88%E6%96%87%E5%93%A1&jtid=d50574697254eca3&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=General+Office+Clerk&jtid=731676023f02e487&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=Clerk&jtid=af17707af0846f0f&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=Receptionist&jtid=4fdb4b7a0a689136&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E8%A1%8C%E6%94%BF%E6%96%87%E5%93%A1&jtid=2ef1798773b9d393&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E8%A8%BA%E6%89%80%E5%8A%A9%E7%90%86&jtid=b68c9fb8bef73668&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=Clinic+Assistant&jtid=1c700a18492c2706&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E5%80%89%E5%8B%99%E5%93%A1%2F%E7%90%86%E8%B2%A8%E5%93%A1&jtid=190b38af0aafc92e&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E5%AE%A2%E6%88%B6%E6%9C%8D%E5%8B%99%E4%B8%BB%E4%BB%BB&jtid=0dbabaff8dc2660c&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=Administrative+Assistant&jtid=a88d8af7a6e7120b&sort=date', 'https://www.indeed.hk/jobs?l=Central,+Hong+Kong+Island&rbt=%E4%BE%8D%E6%87%89&jtid=ab8a153eeb74667f&sort=date']
    logging.info("Loading SoftSkillsExtractor")
    ss_extractor = SoftSkillsExtractor()
    logging.info("Loading GeneralSkillsExtractor")
    gs_extractor = GeneralSkillsExtractor()
    logging.info("Loading DutiesExtractor")
    d_extractor = DutiesExtractor()

    def getSalary(self, ssalary):
        print("me:",ssalary)
        if (ssalary == []):
            return
        salary = str(ssalary).split('-')
        minn = ""
        maxx = ""
        extra = ""
        for i in salary[0]:
            if i.isdigit():
                minn = minn + i
        for i in salary[1]:
            if i.isdigit():
                maxx = maxx + i
            if i.isalpha():
                extra = extra + i
        print("I am Salary:",int(minn), int(maxx), extra)

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//*[@class="title"]/a/@href').getall()

        logging.debug('Number of jobs: {num_jobs}'.format(
            num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('=')[-2]
            print("I am job ID:", job_id)
            job_url = "https://www.indeed.hk" + job_url
            print("Now working on JobURL", job_url)

            yield scrapy.Request(job_url, callback=self.parse_job)

        pages = response.xpath('//*[@class="np"]/../../@href').getall()
        print("I am pages:", pages)
        if pages:
            page = max(max(pages), max(pages, key=len), key=len)
            print("I am page:", page)
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

    def processSalary(self, salary):
        money = re.findall("[0-9,.]+[MKmk(\s?million)]?", salary)
        current = re.findall("[A-Z]{3}?", salary)
        mtype = re.findall("(?i)(month|year|hour|minute|yr|yrs|day|days|week|weeks|months|years|hours|minutes)", salary)
        maxx = 0
        minn = 0
        if (len(money) >= 2):
            maxx = money[1]
            minn = money[0]
        elif(len(money) == 1):
            maxx = money[0]
            minn = money[0]
        return {'moneymax': maxx, 'moneymin': minn, 'current': current, 'mtype': mtype}

    
    def parse_job(self, response):
        logging.debug('Parsing job: {url}'.format(url=response.url))
        job_item = get_loader(JobItem(), response)

        joburl = re.search("([^\?]+\?).*?(jk=[^\&]+)", response.url)  # Remove tracking part from the url
        job_item.add_value('job_id', joburl[1] + joburl[2])
        job_item.add_xpath('title', '//*[contains(@class,"jobsearch-JobInfoHeader-title")]/text()')
        job_item.add_xpath('job_rating', '//*[@class="icl-Ratings-starsCountWrapper"]/@aria-label')

        # Get location (geocode)
        location_item = get_loader(LocationItem(), response)
        # location = '\n'.join(response.xpath('//div[contains(@class,"icl-IconFunctional icl-IconFunctional--location icl-IconFunctional--md")]/../span/text()').extract())
        location = ''.join(response.xpath('//div[@class="jobsearch-InlineCompanyRating icl-u-xs-mt--xs  jobsearch-DesktopStickyContainer-companyrating"]//div[not(@class) or not(@id)]/text()').extract())
        # location = '\n'.join(response.xpath('//div[contains(@class,"indeed-apply-widget")]/@data-indeed-apply-jobLocation').extract())
        # print("\n\n\nHEYYYY\n\n\n")
        # print(response)
        # 
        # Lai's (Intern) code, this part just separate the chinese and address
        # 
        getLocasi = location.split("-")
        # below gets just the address and not the company name
        location = getLocasi[1]
        # print(location)
        # print("\n\n\nHEYYYY\n\n\n")      

        job_item.add_value('location', fill_location_item(location_item, location))

        job_item.add_css('post_date', 'div.jobsearch-JobMetadataFooter::text')
        job_item.add_value('page_url', response.url)
        job_item.add_value('source', 'indeed')

        # Using lxml to parse the text to perserve the format
        body_root = response.xpath('//*[@id="jobDescriptionText"]').extract()[0]
        body_tree = lxml.html.fromstring(body_root)
        body_lines = lxml.html.tostring(body_tree, method="text", encoding="unicode")
        job_item.add_value('body', body_lines)

        job_item.add_value('summary', None)
        job_item.add_value('industry', None)
        job_item.add_xpath('employment_type', '//div[contains(@class,"icl-IconFunctional icl-IconFunctional--jobs icl-IconFunctional--md")]/../span/text()')
        job_item.add_value('function', None)
        job_item.add_xpath('benefits', '//b[contains(text(),"Benefits")]/../following-sibling::ul//text()')
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
        company_item.add_xpath('name', '//*[contains(@class,"jobsearch-InlineCompanyRating")]/div[1]//text()')
        company_item.add_value('website_url', None)
        company_item.add_value('overview', None)
        company_item.add_value('logo_url', None)
        company_item.add_value('other_jobs_url', None)
        job_item.add_value('company', company_item.load_item())

        salaryDict = self.processSalary(str(response.xpath('/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]/div[3]/div[1]/div//span[contains(text(), "$")]/text()').extract()))
        salary_item = get_loader(SalaryItem(), response)
        salary_item.add_value('max', salaryDict['moneymax'])
        salary_item.add_value('min', salaryDict['moneymin'])
        salary_item.add_value('salary_type', salaryDict['mtype'])
        salary_item.add_value('extra_info', None)
        salary_item.add_value('currency', salaryDict['current'])
        salary_item.add_xpath('salary_on_display', '/html/body/div[1]/div[2]/div[3]/div/div/div[1]/div[1]/div[3]/div[1]/div//span[contains(text(), "$")]/text()')
        job_item.add_value('salary', salary_item.load_item())

        return job_item.load_item()
