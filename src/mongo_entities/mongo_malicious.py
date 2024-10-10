from collections import OrderedDict

from . import mongo_base
from .. import gen_utils
from ..redis_controllers import redis_ctl, redis_utils

PROJECT_AREAS = [
    'work',
    'review',
    'publish',
    'deliverable'
]

API_TIMEZONE = 'Asia/Bangkok'

class ZeafrostMalicious(mongo_base.ZeafrostDb):
    def __init__(self, *args, **kwargs):
        super(ZeafrostMalicious, self).__init__(*args, **kwargs)
        self.collection = self.db['malicious']
    
    def schema_to_document(self):
        schema = OrderedDict()
        schema['id'] = None
        schema['name'] = ""
        schema['keyword'] = ""
        schema['description'] = ""
        schema['dccs'] = []
        schema['created_by'] = None
        schema['created_at'] = ""
        schema['updated_by'] = None
        schema['updated_at'] = ""

        return schema

def malicious_cache():
    malicious_db = ZeafrostMalicious()
    malicious_data = [each for each in malicious_db.find()]
    malicious_db.close()

    redis_ctl.delete('zs:malicious:*')  

    redis_names = []
    for each_data in malicious_data:
        redis_name = f'zs:malicious:{each_data.get("name")}:{each_data.get("id")}'.lower()       # DEFINE REDIS NAME
        redis_ctl.delete(redis_name)  
        data_parse = redis_utils.redis_prepare_cache_data(each_data)
        redis_ctl.hset(redis_name, data_parse)                                  # REDIS CACHE - CMD: HSET

        redis_names.append(redis_name)
    
    return redis_names

def entity_search():
    pass