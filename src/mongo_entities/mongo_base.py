import os
import pymongo
from dotenv import load_dotenv

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class ZeafrostDb(object):
    def __init__(self):
        self.mongo_client = pymongo.MongoClient(
            f'mongodb://{os.environ.get("ZEAFROST_DB_HOST_IP")}:{os.environ.get("ZEAFROST_DB_PORT")}/',
            username=os.environ.get("ZEAFROST_DB_USERNAME"),
            password=os.environ.get("ZEAFROST_DB_PASSWORD"),
            authSource=os.environ.get("ZEAFROST_DB_AUTH_SOURCE"),
            authMechanism=os.environ.get("ZEAFROST_DB_AUTH_MECHANISM")
        )
        
        self.db = self.mongo_client['zeafrost']
        self.collection = ''
        
    def close(self):
        self.mongo_client.close()

    def find(self, *args, **kwargs):
        result = self.collection.find(*args, **kwargs)
        return result
    
    def find_one(self, *args, **kwargs):
        result = self.collection.find_one(*args, **kwargs)
        return result
    
    def insert(self, *args, **kwargs):
        result = self.collection.insert_many(*args, **kwargs)
        return result
    
    def insert_many(self, *args, **kwargs):
        result = self.collection.insert_many(*args, **kwargs)
        return result
    
    def update_one(self, *args, **kwargs):
        result = self.collection.update_one(*args, **kwargs)
        return result
    
    def update_many(self, *args, **kwargs):
        result = self.collection.update_many(*args, **kwargs)
        return result
    
    def delete_one(self, *args, **kwargs):
        result = self.collection.delete_one(*args, **kwargs)
        return result
    
    def delete_many(self, *args, **kwargs):
        result = self.collection.delete_many(*args, **kwargs)
        return result
