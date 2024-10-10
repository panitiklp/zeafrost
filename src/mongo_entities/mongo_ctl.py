from collections import OrderedDict
from . import mongo_malicious
from ..redis_controllers import redis_ctl, redis_utils
from ast import literal_eval

def cache():
    malicious = mongo_malicious.ZeafrostMalicious()
    mal_result = [each for each in malicious.find()]

    for each_data in mal_result:
        redis_name = f'zs:malicious:{each_data.get("name")}:{each_data.get("id")}'.lower()
        redis_ctl.hset(redis_name, redis_utils.redis_prepare_cache_data(each_data))
    
    return True

def entity_search(redis_names):
    entity_result = redis_ctl.hgetall(redis_names[0])
    parsed_result = OrderedDict()

    for key, val in entity_result.items():
        try:
            parsed_result[key] = literal_eval(val)
        except:
            parsed_result[key] = val

    return parsed_result

def search(body):
    mal_name = body.get('name') or body.get('malicious')

    result = OrderedDict()
    result['code'] = ''
    result['message'] = ''
    result['data'] = []

    if mal_name:
        redis_names = redis_ctl.keys(f'zs:malicious:{mal_name}:*'.lower())
        
        if len(redis_names) > 0:
            search_result = entity_search(redis_names)
            search_result.pop('_id')

            result['data'] = [search_result]
            result['message'] = 'OK'
            result['code'] = 200

        else:
            cache()
            redis_names = redis_ctl.keys(f'zs:malicious:{mal_name}:*'.lower())

            if len(redis_names) > 0:
                search_result = entity_search(redis_names)

                result['data'] = [search_result]
                result['message'] = 'OK'
                result['code'] = 200
    else:
        malicious = mongo_malicious.ZeafrostMalicious()
        parsed_data = []

        for each_data in [each for each in malicious.find()]:
            each_data.pop('_id')
            parsed_data.append(each_data)

            result['data'] = [parsed_data]
            result['message'] = 'OK'
            result['code'] = 200

    return result 
