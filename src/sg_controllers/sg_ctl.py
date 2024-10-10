from ..sg_entities import sg_project
from ..sg_entities import sg_episode
from ..sg_entities import sg_sequence
from ..sg_entities import sg_shot
from ..sg_entities import sg_task
from ..sg_entities import sg_asset
from ..sg_entities import sg_version
from ..sg_entities import sg_publishedFile
from ..sg_entities import sg_timeLog
from ..sg_entities import sg_note
from ..sg_entities import sg_publishedFileType
from ..sg_entities import sg_assetShotConnnection
from ..sg_entities import sg_step
from ..sg_entities import sg_playlist
from ..sg_entities import sg_department
from ..sg_entities import sg_user
from ..sg_entities import sg_status
from ..sg_entities import sg_software
from ..sg_entities import sg_pipelineConfiguration
from ..sg_entities import sg_thumbnail
from ..sg_entities import sg_test
from collections import OrderedDict

entity_module_maps = {
    'project':      sg_project,
    'episode':      sg_episode,
    'sequence':     sg_sequence,
    'shot':         sg_shot,
    'task':         sg_task,
    'asset':        sg_asset,
    'version':      sg_version,
    'publishedfile':        sg_publishedFile,
    'timelog':      sg_timeLog,
    'note':         sg_note,
    'publishedfiletype':    sg_publishedFileType,
    'assetshotconnection':  sg_assetShotConnnection,
    'step':         sg_step,
    'playlist':     sg_playlist,
    'department':   sg_department,
    'user':         sg_user,
    'status':       sg_status,
    'software':     sg_software,
    'pipelineconfiguration':    sg_pipelineConfiguration,
    'thumbnail':    sg_thumbnail,
    'test':         sg_test
}

def search(entity, body={}):
    sg_entity = entity_module_maps.get(entity.lower())

    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []
    
    if sg_entity:
        entity_result = sg_entity.sg_entity_search(body)

        result['code'] = 200
        result['message'] = 'OK'
        result['data'] = entity_result
    
    else:
        result['code'] = 2000
        result['message'] = f'DATABASE_ERROR: [{entity.upper()}], An Error Occurred In The Database. // Entity Is Invalid.'
    
    return result

def task_search_by_user(body={}):
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    task_result = sg_task.sg_search_by_user(body)

    if task_result:
        result['code'] = 200
        result['message'] = 'OK'
        result['data'] = task_result
    
    else:
        result['code'] = 5000
        result['message'] = 'SHOTGRID_ERROR: [TASK], An Error Occurred In The ShotGrid.'
    
    return result

def create(entity, body={}):
    sg_entity = entity_module_maps.get(entity.lower())

    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []
    
    if sg_entity:
        entity_result = sg_entity.sg_entity_create(body)

        if entity_result: 
                result['code'] = 200
                result['message'] = 'OK'
                result['data'] = entity_result
        else:
            result['code'] = 5000
            result['message'] = f'SHOTGRID_ERROR: [{entity.upper()}], An Error Occurred In The ShotGrid. // Can Not Create Data.'
    
    else:
        result['code'] = 2000
        result['message'] = f'DATABASE_ERROR: [{entity.upper()}], An Error Occurred In The Database. // Entity Is Invalid.'
    
    return result

def cache(entity, body={}):
    sg_entity = entity_module_maps.get(entity.lower())

    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []
    
    if sg_entity:
        entity_result = sg_entity.entity_cache(**body)

        if entity_result:
            result['code'] = 200
            result['message'] = 'OK'
            result['data'] = entity_result
        
        else:
            result['code'] = 5000
            result['message'] = f'SHOTGRID_ERROR: [{entity.upper()}], An Error Occurred In The ShotGrid. // No Data From ShotGrid.'
    
    else:
        result['code'] = 2000
        result['message'] = f'DATABASE_ERROR: [{entity.upper()}], An Error Occurred In The Database. // Entity Is Invalid.'
    
    return result

def update(entity, body={}):
    sg_entity = entity_module_maps.get(entity.lower())
    
    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []

    if sg_entity:
        entity_result = sg_entity.sg_entity_update(body)
        
        if entity_result:

            if type(entity_result) == type({'check': 'type'}):
                result['code'] = entity_result.get('code')
                result['message'] = entity_result.get('message')
                result['data'] = entity_result.get('data')

            else:
                result['code'] = 200
                result['message'] = 'OK'
                result['data'] = entity_result
            
        
        else:
            result['code'] = 5000
            result['message'] = f'SHOTGRID_ERROR: [{entity.upper()}], An Error Occurred In The ShotGrid. // No Data From ShotGrid.' 
    
    else:
        result['code'] = 2000
        result['message'] = f'DATABASE_ERROR: [{entity.upper()}], An Error Occurred In The Database. // Entity Is Invalid.' 
    
    return result

def delete(entity, body={}):
    sg_entity = entity_module_maps.get(entity.lower())

    result = OrderedDict()
    result['code'] = None
    result['message'] = ''
    result['data'] = []
    
    if sg_entity:
        entity_result = sg_entity.sg_entity_delete(body)

        if entity_result == True:
            result['code'] = 200
            result['message'] = 'OK'
            result['data'] = entity_result

        elif entity_result == False:
            result['code'] = 5000
            result['message'] = f'SHOTGRID_ERROR: [{entity.upper()}], An Error Occurred In The ShotGrid. // Data Not Matched.'
            result['data'] = entity_result
    else:
        result['code'] = 2000
        result['message'] = f'DATABASE_ERROR: [{entity.upper()}], An Error Occurred In The Database. // Entity Is Invalid.'
    
    return result

def _test():
    entity_result = sg_test.fx_search_all_task()

    result = OrderedDict()
    result['code'] = 200
    result['message'] = 'OK'
    result['data'] = entity_result

    return result


if __name__ == '__main__':
    pass