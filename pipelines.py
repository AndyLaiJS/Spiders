import pymongo
import logging


class MongoDBPipeline(object):
   def __init__(self):
       self.mongo_host = "localhost"
       self.mongo_port = 27017
       self.mongo_user = ""
       self.mongo_password = ""
       self.mongo_auth = "career_crawler"
#       self.mongo_uri = "{host}:{port}".format(host=self.mongo_host, port=self.mongo_port)
       self.mongo_db = "career_crawler"
       self.collection_name = 'jobs'

       self.connection = pymongo.MongoClient(
           self.mongo_host,
           self.mongo_port,
           username=self.mongo_user,
           password=self.mongo_password,
           authSource=self.mongo_auth,
       )
       self.db = self.connection[self.mongo_db]
       self.collection = self.db[self.collection_name]

#   def open_spider(self, spider):
#       self.client = pymongo.MongoClient(self.mongo_uri)
#       self.db = self.client[self.mongo_db]
#       self.collection = self.db[self.collection_name]
#
#       spider.collection = self.collection
#
   def close_spider(self, spider):
       self.connection.close()

   def process_item(self, item, spider):
       id = item['job_id']
       print("yeayeyaeyaeyeay")
       logging.debug('Storing {id} into DB'.format(id=id))
       item['head'] = self.collection.count_documents({"body": item['body'], "job_id": {"$ne": id}}) == 0
       result = self.collection.update({'job_id': id}, dict(item), upsert=True)
       logging.debug('Finished upsert: ' + str(result))
       return item
