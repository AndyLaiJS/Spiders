# Jobs Ads Crawler

Last update: 2020-06-18 14:58

(Here is `<repo_root>/JobSpider/jobs`)

These are web crawlers to collect job ads posts from different websites.

## Websites supported

- [adecco](https://www.adecco.com.hk/)
- [cpjobs](https://www.cpjobs.com/hk/jobs/)
- [efc](https://www.efinancialcareers.hk/sitemap/html#jobsBySector)
- [glassdoor](https://www.glassdoor.com.hk/index.htm?countryRedirect=true)
- [indeed](https://www.indeed.ae/jobs?q=Islamic%20Finance&vjk=8db8f17434c93fa3)
- [jobsdb](https://hk.jobsdb.com/hk/jobs/banking-finance/1)
- [jora](https://hk.jora.com/j?q=&l=&sp=homepage)
- [michaelpage](https://www.michaelpage.com.hk/job-search)
- [pagepersonnel](https://www.pagepersonnel.com.hk/)

## 1. Start MongoDB by docker-Compose

It schedules daily to crawl job ads websites and also host a local MongoDB instance, with port: **9997** and host: **127.0.0.1** .

> docker-compose up --build


## 2. To run standalone crawler

Create virtual environement, and activate it

> python3 -m venv nenv

> source nenv/bin/activate

Update pip and install dependencies

> pip install -U pip

> pip install -r requirements.txt

Config about MongoDB for Scrapy, edit `/JobSpider/jobs/jobs/pipelines.py`


For **"schedule mode"**:

```python
    self.mongo_host = "mongodb"
    self.mongo_port = 27017
```

For **"standalone mode"**:

```python
    self.mongo_host = "127.0.0.1"
    self.mongo_port = 9997
```

## 3. Run Scrapy

> scrapy crawl adecco_update

> scrapy crawl cpjobs_update

> scrapy crawl efc_update

> scrapy crawl glassdoor_update

> scrapy crawl indeed_update

> scrapy crawl jobsdb

> scrapy crawl jora_update

> scrapy crawl michaelpage_update

> scrapy crawl pagepersonnel_update

# Query in MongoDB

> db.getCollection('jobs').find({}, {stdJobFunc:1, _id:0})
