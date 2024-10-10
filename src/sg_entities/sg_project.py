import os
import re
import sys
import threading
from ast import literal_eval
from collections import OrderedDict

from . import sg_entity_utils
from .. import dir_template, gen_utils
from ..sg_controllers import sg_con
from ..mongo_entities import mongo_project
from ..redis_controllers import redis_ctl, redis_utils

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'code',
    'name': 'name',
    'status': 'sg_status',
    'description': 'sg_description',
    'type': 'sg_type',
    'frame_rate': 'sg_frame_rate',
    'start_frame': 'sg_frame_to_start',
    'resolution': 'sg_resolution',
    'project_path': 'sg_project_path',
    'archived': 'archived',
    'renderers': 'sg_renderers',
    'grooms': 'sg_grooms',
    'softwares': 'sg_softwares',
    'frame_preroll': 'sg_frame_preroll',
    'frame_postroll': 'sg_frame_postroll'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'name']

PROJECT_TYPES = [
    'feature',
    'short',
    'series',
    'commercial',
    'rnd'
]

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    redis_project_pattern = f'sg:project:*'.lower()

    project = kwargs.get('project') or ''

    # get data from SG
    #-----------------
    filters = [
            ['sg_status', 'is', 'Active'],
            ['archived', 'is', False]
        ]

    if project:
        filters.append(['name', 'is', project])
        redis_project_pattern = f'sg:project:{project}:*'.lower()
    
    sg = sg_con.connect()
    sg_result = sg.find(
        'Project', 
        filters=filters, 
        fields=list(SG_FIELD_MAPS.values())
    )

    if sg_result:
        redis_ctl.delete(redis_project_pattern)

        for elem_data in sg_result:
            redis_name =  'sg:project:'
            redis_name += f'{elem_data.get("code")}:'
            redis_name += f'{elem_data.get("id")}'
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem_data))

    mongo_project.project_cache(project=project)
    
    if len(redis_ctl.keys(redis_project_pattern)) > 0:
        return True
    else:
        return False

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    project         = body.get('project')
    project_id      = body.get('id')
    project_type    = body.get('type')
    shotgrid        = body.get('shotgrid') or False

    valid_keys = {
        'project',
        'id',
        'type',
        'shotgrid'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    sg_result = []
    result = []
    sg_result_adapter = []

    redis_name =  'sg:project:'
    redis_name += f'*{project}:'    if project      else '*:'
    redis_name += f'{project_id}'   if project_id   else '*'

    redis_names = redis_ctl.keys(redis_name.lower())

    if len(redis_names) > 0:
        for redis_name in sorted(redis_names):
            project_data = redis_ctl.hgetall(redis_name)
            sg_result.append(project_data)
    
    else:
        entity_cache()
        redis_names = redis_ctl.keys(redis_name.lower())

        if len(redis_names) > 0:
            for redis_name in sorted(redis_names):
                project_data = redis_ctl.hgetall(redis_name)
                sg_result.append(project_data)

    if project_type and sg_result:
        sg_result = [each for each in sg_result if each.get('sg_type') == project_type]
    
    if sg_result:
        mongo_unuse_keys = [
            '_id',
            'id',
            'code',
            'shotgrid_id',
            'is_active',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by'
        ]

        if shotgrid:
            sg_result_adapter = sg_result
            
        else:
            sg_result_adapter = sg_entity_utils.entity_response_adapter(
                data        = sg_result, 
                sg_fields   = SG_FIELD_MAPS_INVERT, 
                str_fields  = STR_FIELDS
            )
            
        # ------------------------------------- #
        #       ADD PROJECT DATA FROM MONGO     #
        # ------------------------------------- #
        for each_data in sg_result_adapter:
            zs_name =  'zs:project:'
            zs_name += f'{each_data.get("name")}:'  if each_data.get('name')    else '*:'
            zs_name += f'{each_data.get("id")}'     if each_data.get('id')      else '*'
            zs_data = redis_ctl.hgetall(zs_name.lower())

            if zs_data:
                for key in mongo_unuse_keys:
                    zs_data.pop(key)
                    
                for key, val in zs_data.items():
                    try:
                        zs_data[key] = literal_eval(val)

                    except SyntaxError:
                        zs_data[key] = val

                each_data.update({'project_config': zs_data})
            else:
                each_data.update({'project_config': {}})
            
            result.append(each_data)
    
    return result

def mongo_project_insert(sg_create_result, username):
    # ------------------------------------- #
    #       INSERT PROJECT INTO MONGODB     #
    # ------------------------------------- #
    mongo_project_      = mongo_project.ZeafrostProject()
    mongo_project_data  = []
    resolution_data     = OrderedDict()

    if len(sg_create_result) > 0:
        project_ids = [each.get('id') if isinstance(each, dict) else [] for each in mongo_project_.find().sort('id', -1)]
        project_id  = project_ids[0] if len(project_ids) > 0 else 1

        redis_usernames = redis_ctl.keys(f'sg:user:{username}:*'.lower())
        
        for each_data in sg_create_result:
            project_id += 1
            project_code = each_data.get('code')
            project_resolution = each_data.get('sg_resolution')

            if project_resolution:
                if re.search('[0-9]+x[0-9]+', project_resolution):
                    resolution_split = [int(each) for each in project_resolution.split('x')]
                    resolution_data['preview']      = resolution_split
                    resolution_data['review']       = resolution_split
                    resolution_data['deliverable']  = resolution_split
            
            proj_data = mongo_project_.schema_to_document(
                project_code    = project_code,
                project_id      = project_id,
                shotgrid_id     = each_data.get('id'),
                resolution      = resolution_data if isinstance(resolution_data, OrderedDict) else {},
                project_path    = each_data.get('sg_project_path'),
                username        = int(redis_usernames[0].split(':')[-1]) if len(redis_usernames) > 0 else None
            )
            mongo_project_data.append(proj_data)
        mongo_project_.insert_many(mongo_project_data)
    mongo_project_.close()

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    result = []

    if data:
        entity_cache()

        sg_data = []
        username = None

        for project_dict in data:
            project = project_dict.get('project')
            project_type = project_dict.get('type') if project_dict.get('type') in PROJECT_TYPES else None
            project_path = project_dict.get('project_path')
            username = project_dict.get('username')

            if project and project_type:
                redis_names = redis_ctl.keys(f'sg:project:*{project}:*'.lower())

                if len(redis_names) == 0:
                    proj_data = {
                        'request_type': 'create',
                        'entity_type': 'Project',
                        'data':{
                            'sg_status': 'Active',
                            'code': project,
                            'name': project,
                            'sg_type': project_type,
                            'sg_frame_rate': str(project_dict.get('frame_rate')) if project_dict.get('frame_rate') else None,
                            'sg_frame_to_start': int(project_dict.get('start_frame')) if project_dict.get('start_frame') else None,
                            'sg_resolution': project_dict.get('resolution'),
                            'sg_resolution': project_dict.get('resolution'),
                            'sg_project_path': project_path
                        }
                    }
                    sg_data.append(proj_data)
        
        if len(sg_data) > 0:
            sg = sg_con.connect()
            result = sg.batch(sg_data)
            
            thread_project_mongo    = threading.Thread(
                target  = mongo_project_insert, 
                args    = (result, username,))

            thread_directory_create = threading.Thread(
                target  = create_directory, 
                args    = (data,)
            )

            thread_project_mongo.start()
            thread_directory_create.start()
        
        thread_cache = threading.Thread(target=entity_cache)
        thread_cache.start()    
    
    return result

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data')
    sg_update_data = []
    result = []

    for each in data:
        filters = each.get('filters')
        values  = each.get('values')

        project = filters.get('project')

        redis_names = redis_ctl.keys(f'sg:project:*{project}:*'.lower())
        entity_id = int(redis_names[0].split(':')[-1])
        
        if values:
            sg_data = {}
            for key, val in values.items():
                sg_data[SG_FIELD_MAPS[key]] = val

            sg_update_data.append(
                {
                    'request_type': 'update',
                    'entity_type': 'Project',
                    'entity_id': entity_id,
                    'data': sg_data
                }
            )
    
    if len(sg_update_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_update_data)

        thread_redis_cache_update = threading.Thread(target=entity_cache)
        thread_redis_cache_update.start()
        
    return result

# ================================== #
#       SHOTGRID ENTITY DELETE       #
# ================================== #
def sg_entity_delete(body):
    data = body.get('data')
    result = []

    if data:
        sg_data = []
        for project_dict in data:
            project = project_dict.get('project')
            project_id = project_dict.get('project_id')
            
            redis_name =  'sg:project:'
            redis_name += f'*{project}:'    if project      else '*:'
            redis_name += f'{project_id}'   if project_id   else '*'
            redis_names = redis_ctl.keys(redis_name.lower())
            
            if len(redis_names) > 0:
                shotgrid_ids = []
                
                for name in redis_names:
                    shotgrid_id = int(name.split(':')[-1])
                    shotgrid_ids.append(shotgrid_id)

                    project_dict = {
                        'request_type': 'delete', 
                        'entity_type':  'Project', 
                        'entity_id':    shotgrid_id
                    }

                    sg_data.append(project_dict)
        
        if len(sg_data) > 0:
            sg = sg_con.connect()

            result = sg.batch(sg_data)
            
            thread_archive = threading.Thread(target=mongo_change_project_to_archive, args=(shotgrid_ids,))
            thread_cache = threading.Thread(target=entity_cache)
            
            thread_archive.start()
            thread_cache.start()
            
    return result

def mongo_change_project_to_archive(shotgrid_ids):
    mongo_proj = mongo_project.ZeafrostProject()

    for shotgrid_id in shotgrid_ids:
        mongo_proj.update_one({'shotgrid_id': shotgrid_id}, {'$set': {'is_active': False}})

    return True

# ==================================== #
#       PROJECT CREATE DIRECTORY       #
# ==================================== #
def create_directory(data):
    cur_platform = sys.platform
    
    for project_dict in data:
        if project_dict.get('directory') == True:
            project_path = project_dict.get('project_path')

            if cur_platform.lower() == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if not os.path.exists(project_path):
                for _dir in dir_template.PROJECT_DIRECTORIES:
                    if 'asset/{type}' in _dir:
                        for asset_type in dir_template.DEFAULT_ASSET_TYPE_DIRECTORIES:
                            dir_path = f'{project_path}/{_dir.format(type=asset_type)}'
                            gen_utils.make_dirs(dir_path)

                    else:
                        dir_path = f'{project_path}/{_dir}'
                        gen_utils.make_dirs(dir_path)
    return True
