# Jobs Ads Crawler

Last update: 2020-06-18 14:58

(Here is `<repo_root>/JobSpider/jobs`)

These are web crawlers to collect job ads posts from different websites.

## Websites TO-DO
- [Hong Kong Convention and Exhibition Center](https://www.hkcec.com)
- [Hong Kong Tourism Board](https://www.discoverhongkong.com/us/index.html)
- [Hong Kong Trade Development Council](https://www.hktdc.com)
- [Leisure and Culture Services Development](https://www.lcsd.gov.hk/en/)
- [West Kowloon Cultural District Authority](https://www.westkowloon.hk/en)
- [Asia World Expo](https://www.asiaworld-expo.com)
- [Hong Kong Visual Arts Centre](https://www.lcsd.gov.hk/CE/Museum/APO/en_US/web/apo/va_main.html)
- [Hong Kong Cultural and Heritage Museum](https://www.heritagemuseum.gov.hk/en_US/web/hm/highlights.html)
- [Hong Kong Museum of History](https://hk.history.museum/en_US/web/mh/index.html)
- [Hong Kong Space Museum](https://www.lcsd.gov.hk/CE/Museum/Space/en_US/web/spm/whatsnew.html)
- [Hong Kong Flim Archive](https://www.filmarchive.gov.hk/en_US/web/hkfa/aboutus/openhl.html)
- [Hong Kong Museum of Art](https://hk.art.museum/en_US/web/ma/home.html)
- [Taikoo Place Artistree](https://www.taikooplace.com/en/artistree)
- [Tai Kuwn](https://www.taikwun.hk/en/)
- [The Mills](http://www.themills.com.hk/en/)
- [Jockey Club Creative Art Centre](https://www.jccac.org.hk/?lang=en)
- [PMQ](https://www.pmq.org.hk)
- [Asia Society](https://asiasociety.org/hong-kong)

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