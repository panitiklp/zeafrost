from ast import literal_eval
from bson.objectid import ObjectId

def redis_prepare_cache_data(data):
    result = {}
    
    for key, val in data.items():
        if val == None:
            val = ''

        if isinstance(val, dict):
            val = str(val)

        elif isinstance(val, list):
            val = str(val)

        elif isinstance(val, tuple):
            val = str(val) 

        elif isinstance(val, bool):
            val = str(val)

        elif isinstance(val, ObjectId):
            val = str(val)

        if key == 'id':
            val = int(val)
        
        result[key.lower()] = val

    return result

def redis_correct_data_from_cache(data):
    result   = []
    keys_str = [
        'code',
        'sg_short_name'
    ]

    for each_data in data:
        each_result = {}
        
        for key, val in each_data.items():
            try:
                each_result[key] = literal_eval(val)

            except:
                each_result[key] = val
            
            if key in keys_str:
                each_result[key] = str(val)
        
        result.append(each_result)

    return result