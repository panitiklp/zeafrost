import os
import pymongo
from dotenv import load_dotenv

from .redis_controllers import redis_ctl

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Rocketchat(object):
    def __init__(self, collection):
        self.collection = collection
        self.mongo_client = pymongo.MongoClient(f'mongodb://{os.environ.get("ROCKETCHAT_DB_HOST_IP")}:{os.environ.get("ROCKETCHAT_DB_PORT")}/')
        self.rocketchat_db = self.mongo_client['rocketchat']
        self.db_collection = self.rocketchat_db[self.collection]
    
    def close(self):
        self.mongo_client.close()
    
    def find(self, *args, **kwargs):
        result = self.db_collection.find(*args, **kwargs)
        return result
    
    def find_one(self, *args, **kwargs):
        result = self.db_collection.find_one(*args, **kwargs)
        return result

class RocketchatUser(Rocketchat):
    def __init__(self, *args, **kwargs):
        super(RocketchatUser, self).__init__(collection='users', *args, **kwargs)

class RocketchatRoom(Rocketchat):
    def __init__(self, *args, **kwargs):
        super(RocketchatRoom, self).__init__(collection='rocketchat_room', *args, **kwargs)

def rocketchat_user_room_cache():
    rocketchat_user = RocketchatUser()
    rocketchat_room = RocketchatRoom()

    redis_ctl.delete('rocketchat:*')

    for data in rocketchat_user.find():
        redis_name = f'rocketchat:user:{data.get("username")}'.lower()
        redis_ctl.hset(redis_name, {
            'id': data.get('_id'), 
            'username': data.get('username'), 
            'rooms': str(data.get('__rooms'))
        })
    
    for data in rocketchat_room.find({"fname": {"$exists": True}}):
        redis_name = f'rocketchat:room:{data.get("fname")}:{data.get("_id")}'.lower()
        redis_ctl.hset(redis_name, {
            'id': data.get('_id'), 
            'fname': data.get('fname'), 
            'name': data.get('name')
        })
    
    rocketchat_user.close()
    rocketchat_room.close()
    
    return True