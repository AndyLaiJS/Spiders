# Jobs Ads Crawler

Last update: 2020-06-18 14:58

(Here is `<repo_root>/JobSpider/jobs`)

These are web crawlers to collect job ads posts from different websites.

## Websites TO-DO
- [Hong Kong Convention and Exhibition Center](https://www.hkcec.com) (Unable to do because all of the event subpages are redirected to another domain)
- [Hong Kong Tourism Board](https://www.discoverhongkong.com/us/index.html) (In progress)
- [Hong Kong Trade Development Council](https://www.hktdc.com) (In progress)
- [Leisure and Culture Services Development](https://www.lcsd.gov.hk/en/)
- [West Kowloon Cultural District Authority](https://www.westkowloon.hk/en) (In progress)
- [Asia World Expo](https://www.asiaworld-expo.com)
- [Hong Kong Visual Arts Centre](https://www.lcsd.gov.hk/CE/Museum/APO/en_US/web/apo/va_main.html)
- [Hong Kong Cultural and Heritage Museum](https://www.heritagemuseum.gov.hk/en_US/web/hm/highlights.html)
- [Hong Kong Museum of History](https://hk.history.museum/en_US/web/mh/index.html)
- [Hong Kong Space Museum](https://www.lcsd.gov.hk/CE/Museum/Space/en_US/web/spm/whatsnew.html)
- [Hong Kong Flim Archive](https://www.filmarchive.gov.hk/en_US/web/hkfa/aboutus/openhl.html) (In progress)
- [Hong Kong Museum of Art](https://hk.art.museum/en_US/web/ma/home.html) (In progress)
- [Taikoo Place Artistree](https://www.taikooplace.com/en/artistree) (In progress)
- [Tai Kuwn](https://www.taikwun.hk/en/) (In progress)
- [The Mills](http://www.themills.com.hk/en/) (In progress)
- [Jockey Club Creative Art Centre](https://www.jccac.org.hk/?lang=en)
- [PMQ](https://www.pmq.org.hk) (In progress)
- [Asia Society](https://asiasociety.org/hong-kong) (In progress)

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

> scrapy crawl westkowloon

> scrapy crawl taikwun

> scrapy crawl taikoo

> scrapy crawl hkmoa

> scrapy crawl hkfa

# Query in MongoDB

> db.getCollection('jobs').find({}, {stdJobFunc:1, _id:0})
