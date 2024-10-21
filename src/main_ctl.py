from collections import OrderedDict
from .sg_controllers import sg_ctl
from .mongo_entities import mongo_ctl

def search(entity, body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    if entity == 'malicious':
        entity_result = mongo_ctl.search(body)
    else:
        entity_result = sg_ctl.search(entity, body) or []

    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = f'API_ERROR: [{entity.upper()}], An Error Occurred In The API.'
    
    return result

def task_search_by_user(body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    task_result = sg_ctl.task_search_by_user(body)

    if task_result:
        result['code'] = task_result.get('code')
        result['message'] = task_result.get('message')
        result['data'] = task_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = 'API_ERROR: [TASK], An Error Occurred In The API.'
    
    return result

def task_search_basic(body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    task_result = sg_ctl.task_search_basic(body)

    if task_result:
        result['code'] = task_result.get('code')
        result['message'] = task_result.get('message')
        result['data'] = task_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = 'API_ERROR: [TASK], An Error Occurred In The API.'
    
    return result

def create(entity, body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    entity_result = sg_ctl.create(entity, body)

    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = f'API_ERROR: [{entity.upper()}], An Error Occurred In The API.'

    return result

def cache(entity, body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    entity_result = sg_ctl.cache(entity, body) or {}

    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = f'API_ERROR: [{entity.upper()}], An Error Occurred In The API.'

    return result


def update(entity, body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    entity_result = sg_ctl.update(entity, body)
    
    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = f'API_ERROR: [{entity.upper()}], An Error Occurred In The API.'
    
    return result

def delete(entity, body):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    entity_result = sg_ctl.delete(entity, body) or []

    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = f'API_ERROR: [{entity.upper()}], An Error Occurred In The API.'
    
    return result

def _test():
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    entity_result = sg_ctl._test()

    if entity_result:
        result['code'] = entity_result.get('code')
        result['message'] = entity_result.get('message')
        result['data'] = entity_result.get('data') or []
    
    else:
        result['code'] = 3000
        result['message'] = 'API_ERROR: [TEST], An Error Occurred In The API.'
    
    return result