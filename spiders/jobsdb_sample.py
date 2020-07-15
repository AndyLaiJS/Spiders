# -*- coding: utf-8 -*-
import scrapy
import datetime
from bs4 import BeautifulSoup
import json
import logging


class JobsdbSampleSpider(scrapy.Spider):
    name = 'jobsdb_sample'
    allowed_domains = ['hk.jobsdb.com']
    start_urls = ['https://hk.jobsdb.com/hk/en/Search/FindJobs?JSRV=1&page=1']

    def parse(self, response):
        logging.debug('Parsing index: {url}'.format(url=response.url))
        jobs_url = response.xpath('//div[@data-automation="job-title"]//a/@href').getall()
        logging.debug('Number of jobs: {num_jobs}'.format(num_jobs=len(jobs_url)))
        for job_url in jobs_url:
            job_id = job_url.split('-')[-1]
            # if self.collection.find({'id': job_id}).count() > 0:
            #     logging.debug('Job {id} already in DB, skipping'.format(id=job_id))
            #     continue
            # else:
            #     yield scrapy.Request(job_url, callback=self.parse_job)
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
        jobsdb_meta = json.loads(response.xpath('//body/script[not(@*)]/text()').get().split(' = ')[1][:-1])['details']
        unwanted_fields = ['fetching', 'error', 'subAccount', 'showMoreJobs', 'adType', 'relatedJobFetching',
                           'relatedJobError', 'relatedJobsQuery']
        for unwanted_field in unwanted_fields:
            if unwanted_field in jobsdb_meta:
                del jobsdb_meta[unwanted_field]
        if 'header' in jobsdb_meta and 'banner' in jobsdb_meta['header']:
            del jobsdb_meta['header']['banner']
        item = jobsdb_meta
        print("this ->-------------------------------\n", item['jobDetail']['jobDescription']['html'], 'html.parser')
        print("become this ->-------------------------------\n",
              item['jobDetail']['jobDescription'])
        item['jobDetail']['jobDescription'] = BeautifulSoup(item['jobDetail']['jobDescription']['html'],
                                                            'html.parser').get_text().strip()
        item['companyDetail']['companyOverview'] = BeautifulSoup(item['companyDetail']['companyOverview']['html'],
                                                                 'html.parser').get_text().strip()
        item['datetime'] = datetime.datetime.now()
        return item
