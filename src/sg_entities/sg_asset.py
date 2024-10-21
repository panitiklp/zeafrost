import os
import re
import sys
import threading
# import logging

from . import sg_entity_utils, sg_project
from .. import dir_template, gen_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

# logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'type': 'sg_asset_type',
    'asset': 'code',
    'variation': 'sg_asset_variation',
    'group': 'sg_asset_group',
    'parents': 'parents',
    'assets': 'assets',
    'status': 'sg_status_list',
    'description': 'description',
    'momory_footprint': 'sg_memory_footprint',
    'geometry_cacheable_nodes': 'sg_geometry_cacheable_nodes',
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'asset']

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    project = ''
    redis_pattern = ''
    sg_result = []

    for arg in [each for each in args if isinstance(each, dict)]:
        for key, val in arg.items():
            if key == 'project':
                project = val.lower()
                break
    if kwargs:
        project = kwargs.get('project')
    
    if project:
        sg = sg_con.connect()
        sg_result = sg.find(
            'Asset', 
            filters = [['project', 'name_contains', project]],
            fields = list(SG_FIELD_MAPS.values()),
            order = [{'field_name': 'code', 'direction':'asc'}],
        )

        redis_pattern = f'sg:asset:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        sg_project = elem.get('project')
        
        redis_name =  'sg:asset:'
        redis_name += f'{sg_project.get("name")}:'
        redis_name += f'{elem.get("sg_asset_type")}:'
        redis_name += f'{elem.get("code")}:'
        redis_name += f'{elem.get("id")}'

        if redis_name:
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))

    return True

def sg_entity_single_type_search(project, asset_type, asset, variation, asset_id):
    result = []

    redis_name = ''
    if variation:
        redis_name = 'sg:asset:'
        redis_name += f'*{project}:' if project else '*:'
        redis_name += f'{asset_type}:' if asset_type else '*:'
        redis_name += f'{asset}' if asset else '*'
        redis_name += f'_{variation}:' if variation else '*:'
        redis_name += f'{asset_id}' if asset_id else '*'
    else:
        redis_name = 'sg:asset:'
        redis_name += f'*{project}:' if project else '*:'
        redis_name += f'{asset_type}:' if asset_type else '*:'
        redis_name += f'{asset}:' if asset else '*:'
        redis_name += f'{asset_id}' if asset_id else '*'
    
    redis_names = redis_ctl.keys(redis_name.lower())

    if len(redis_names) > 0:
        for redis_name in sorted(redis_names):
            asset_data = redis_ctl.hgetall(redis_name)
            result.append(asset_data)
    
    else:
        entity_cache({'project': project})
        redis_names = redis_ctl.keys(redis_name.lower())

        if len(redis_names) > 0:
            for redis_name in sorted(redis_names):
                asset_data = redis_ctl.hgetall(redis_name)
                result.append(asset_data)

    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    asset_type = body.get('type') or body.get('asset_type')
    asset_types = body.get('types') or body.get('asset_types')
    asset = body.get('asset')
    asset_id = body.get('id')
    asset_ids = body.get('ids')
    variation = body.get('variation')

    valid_keys = {
        'shotgrid',
        'project',
        'type',
        'asset_type',
        'types',
        'asset_types',
        'asset',
        'id',
        'ids',
        'variation'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []

    if asset_types:
        result = []

        for type_ in asset_types:
            asset_data = sg_entity_single_type_search(project, type_, asset, variation, asset_id)
            asset_result = sg_entity_utils.search_response(
                data=asset_data,
                shotgrid=shotgrid,
                sg_fields=SG_FIELD_MAPS_INVERT,
                str_fields=STR_FIELDS
            )
            result.append(asset_result)

        return result

    elif asset_ids:
        result = []

        for _id in asset_ids:
            asset_data = sg_entity_single_type_search(project, asset_type, asset, variation, _id)
            asset_result = sg_entity_utils.search_response(
                data=asset_data,
                shotgrid=shotgrid,
                sg_fields=SG_FIELD_MAPS_INVERT,
                str_fields=STR_FIELDS
            )

            result.append(asset_result)

        return result

    else:
        result = sg_entity_single_type_search(project, asset_type, asset, variation, asset_id)

        return sg_entity_utils.search_response(
            data=result,
            shotgrid=shotgrid,
            sg_fields=SG_FIELD_MAPS_INVERT,
            str_fields=STR_FIELDS
        )

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    result = []

    projects = sg_entity_utils.multi_project_union(data)
    
    # ----------------------------------------- #
    #       CACHE BEFORE EPISODE PROCESS        #
    # ----------------------------------------- #
    for project_name, project_data in projects.items():
        entity_cache(project_id=project_data.get('id'))

    sg_data = []
    for asset_dict in data:
        project = asset_dict.get('project')
        asset_type = asset_dict.get('type')
        asset = asset_dict.get('asset')
        variation = asset_dict.get('variation')
        redis_name = ''
        sg_asset = ''

        if variation:
            redis_name = 'sg:asset:'
            redis_name += f'*{project}:' if project else '*:'
            redis_name += f'{asset_type}:' if asset_type else '*:'
            redis_name += f'{asset}' if asset else '*'
            redis_name += f'_{variation}:*' if variation else '*:*'
            sg_asset = f'{asset}_{variation}'

        else:
            redis_name  =  'sg:asset:'
            redis_name += f'*{project}:' if project else '*:'
            redis_name += f'{asset_type}:' if asset_type else '*:'
            redis_name += f'{asset}:*' if asset else '*:*'
            sg_asset = asset
        
        redis_names = redis_ctl.keys(redis_name.lower())

        if len(redis_names) == 0 and projects.get(project):
            asset_data = {
                'request_type': 'create',
                'entity_type': 'Asset',
                'data':{
                    'project': {'type': 'Project', 'id': projects[project]['id']},
                    'code': sg_asset,
                    'sg_asset_type': asset_type,
                    'sg_asset_variation': variation if variation else 'default',
                    'sg_asset_group': asset,
                    'sg_status_list': 'wtg'
                }
            }
            sg_data.append(asset_data)

    if len(sg_data) > 0:
        sg = sg_con.connect()

        try:
            result = sg.batch(sg_data)

            thread_dir  = threading.Thread(target=create_directory, args=(projects, data,))
            thread_dir.start()

        except Exception as e:
            return {'error': e}

    # ---------------------------------------- #
    #       CACHE AFTER EPISODE PROCESS        #
    # ---------------------------------------- #
    for project_name, project_data in projects.items():
        thread_cache = threading.Thread(
            target = entity_cache, 
            kwargs = {'project': project_name}
        )

        thread_cache.start()

    return result

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data') or []
    project_id = 0

    sg_update_data = []
    result = []

    for each in data:
        filters = each.get('filters')
        values = each.get('values')

        project = filters.get('project')
        asset_type = filters.get('type')
        asset = filters.get('asset')
        variation = filters.get('variation')
        asset_id = filters.get('id')

        redis_project_data = sg_entity_utils.redis_get_project_data(project=project.lower())

        # ------------------------------------------------- #
        #       CHECK PROJECT, IF NOT EXISTS THEN CACHE     #
        # ------------------------------------------------- #
        if redis_project_data:
            project_id = redis_project_data.get('id')

        else:
            sg_project.entity_cache()
            redis_project_data = sg_entity_utils.redis_get_project_data(project=project.lower())
            project_id = redis_project_data.get('id')

        # ---------------------------- #
        #       GET ASSET REDIS        #
        # ---------------------------- #
        if project_id:
            redis_name = ''

            if variation:
                redis_name = 'sg:asset:'
                redis_name += f'*{project}:' if project else '*:'
                redis_name += f'{asset_type}:' if asset_type else '*:'
                redis_name += f'{asset}' if asset else '*'
                redis_name += f'_{variation}:' if variation else '*:'
                redis_name += f'{asset_id}' if asset_id else '*'
            else:
                redis_name = 'sg:asset:'
                redis_name += f'*{project}:' if project else '*:'
                redis_name += f'{asset_type}:' if asset_type else '*:'
                redis_name += f'{asset}:' if asset else '*:'
                redis_name += f'{asset_id}' if asset_id else '*'
            
            redis_names = redis_ctl.keys(redis_name.lower())             
            entity_id = int(redis_names[0].split(':')[-1]) if len(redis_names) > 0 else None
                    
            sg_data = {}
            for key, val in values.items():
                sg_data[SG_FIELD_MAPS[key]] = val
            
            if entity_id:
                sg_update_data.append(
                    {
                        'request_type': 'update',
                        'entity_type': 'Asset',
                        'entity_id': entity_id,
                        'data': sg_data
                    }
                )
    
    # ------------------------- #
    #       SHOTGRID UPDATE     #
    # ------------------------- #
    if len(sg_update_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_update_data)

        thread_redis_cache_update = threading.Thread(
            target  = entity_cache, 
            kwargs  = {'project_id': project_id}
        )
        thread_redis_cache_update.start()
                
    return result

# ================================= #
#       SHOT CREATE DIRECTORY       #
# ================================= #
def create_directory(projects, data):
    '''
    Parameters:
        projects (dict): project's data 
            projects = {
                "FOO": {
                    "id": 1,
                    "path": "path/to/project/FOO"
                }
            }

    Returns:
        dir_count (int): directories created count
    '''
    cur_platform = sys.platform

    for asset_dict in data:
        if asset_dict.get('directory') == True:
            project_path = projects[asset_dict.get('project')]['path']

            if cur_platform.lower() == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)
            
            if os.path.exists(project_path):
                for _dir in dir_template.ASSET_DIRECTORIES:
                    asset_type = asset_dict.get("type")
                    asset = asset_dict.get("asset")
                    
                    for step, dccs in dir_template.STEP_DCC_DIRECTORIES['asset'].items():        # STEP
                        # ----------------- #
                        #       WORK        #
                        # ----------------- #  
                        if _dir.startswith('work/'):
                            for dcc in dccs:                                                    # DCC
                                for elem in dir_template.DCC_ELEM_DIRECTORIES[dcc]:             # ELEMENTS
                                    dir_path = f'{project_path}/{_dir.format(type=asset_type, asset=asset, step=step, dcc=dcc, elem=elem)}'
                                    gen_utils.make_dirs(dir_path)

                        # ----------------------------- #
                        #       REVIEW / PUBLISH        #
                        # ----------------------------- # 
                        else:
                            dir_path = f'{project_path}/{_dir.format(type=asset_type, asset=asset, step=step)}'
                            gen_utils.make_dirs(dir_path)
    return True
