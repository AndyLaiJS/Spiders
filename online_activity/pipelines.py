# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class MongoDBPipeline(object):
    def __init__(self):
        self.mongo_host = "localhost"
        self.mongo_port = 27017
        self.mongo_user = ""
        self.mongo_password = ""
        self.mongo_auth = "event_crawler"
        # self.mongo_uri = "{host}:{port}".format(host=self.mongo_host, port=self.mongo_port)
        self.mongo_db = "event_crawler"
        self.collection_name = 'events'

        self.connection = pymongo.MongoClient(
            self.mongo_host,
            self.mongo_port,
            username=self.mongo_user,
            password=self.mongo_password,
            authSource=self.mongo_auth,
        )
        self.db = self.connection[self.mongo_db]
        self.collection = self.db[self.collection_name]
    
    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        return item
