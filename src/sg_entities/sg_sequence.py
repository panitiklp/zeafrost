import os
import re
import sys
import threading

from . import sg_entity_utils, sg_project
from .. import dir_template, gen_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

CUR_PLATFORM = sys.platform.lower()
API_TIMEZONE = 'Asia/Bangkok'

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'episode': 'episode',
    'sequence': 'code',
    'short_name': 'sg_short_name',
    'status': 'sg_status_list',
    'description': 'description'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'name', 'sequence']

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
            'Sequence', 
            filters = [['project', 'name_contains', project]],
            fields  = list(SG_FIELD_MAPS.values()),
            order   = [{'field_name': 'code', 'direction':'asc'}]
        )

        redis_pattern = f'sg:sequence:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        sg_project = elem.get('project')
        sg_episode = elem.get('episode')

        if sg_project and sg_episode:
            redis_name =  'sg:sequence:'
            redis_name += f'{sg_project.get("name")}:'
            redis_name += f'{sg_episode.get("name")}:'
            redis_name += f'{elem.get("code")}:'
            redis_name += f'{elem.get("id")}'

            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))
 
    return True

def sg_entity_single_episode_search(project, episode, sequence, sequence_id):
    result = []

    redis_name =  f'sg:sequence:'
    redis_name += f'*{project}:'        if project      else '*:'
    redis_name += f'*{episode}:'        if episode      else '*:'
    redis_name += f'*_{sequence}:'      if sequence     else '*:'
    redis_name += f'{sequence_id}'      if sequence_id  else '*'
    
    redis_names = redis_ctl.keys(redis_name.lower())

    if len(redis_names) > 0:
        for redis_name in sorted(redis_names):
            sequence_data = redis_ctl.hgetall(redis_name)
            result.append(sequence_data)
    else:
        entity_cache({'project': project}) 
        redis_names = redis_ctl.keys(redis_name.lower())

        if len(redis_names) > 0:
            for redis_name in sorted(redis_names):
                sequence_data = redis_ctl.hgetall(redis_name)
                result.append(sequence_data)
    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid    = body.get('shotgrid') or False
    project     = body.get('project')
    episode     = body.get('episode')
    episodes    = body.get('episodes')
    sequence    = body.get('sequence')
    sequence_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'project',
        'episode',
        'episodes',
        'sequence',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []

    if episodes:
        result = []
        for ep in episodes:
            ep_data   = sg_entity_single_episode_search(project, ep, sequence, sequence_id)
            ep_result = sg_entity_utils.search_response(ep_data, shotgrid, SG_FIELD_MAPS_INVERT, STR_FIELDS)
            result.append(ep_result)
        
        return result

    else:
        result = sg_entity_single_episode_search(project, episode, sequence, sequence_id)
        return sg_entity_utils.search_response(result, shotgrid, SG_FIELD_MAPS_INVERT, STR_FIELDS)

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data    = body.get('data')
    result  = []

    # -------------------------------------- #
    #   CACHE SEQUENCES BASED ON PROJECT     #
    # -------------------------------------- #
    projects = {}
    project_result = {}

    for each_data in data:
        project = each_data.get('project')
        redis_project_names = redis_ctl.keys(f'sg:project:{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])
            
            projects[each_data.get('project')] = {
                'id':   int(project_result.get('id')),
                'code': project_result.get('code'),
                'path': project_result.get('sg_project_path')
            }
    
    if projects:
        # ------------------------------------------ #
        #       CACHE BEFORE SEQUENCE PROCESS        #
        # ------------------------------------------ #
        for project_name, project_data in projects.items():
            entity_cache(project_id=project_data.get('id'))

        sg_data = []
        for sequence_dict in data:
            project     = sequence_dict.get('project')
            episode     = sequence_dict.get('episode')
            sequence    = sequence_dict.get('sequence')
            sequence_id = sequence_dict.get('id')

            # ///// SEQUENCE REDIS ///// #
            redis_episode_name =  'sg:episode:'
            redis_episode_name += f'*{project}:'    if project else '*:'
            redis_episode_name += f'*{episode}:*'   if episode else '*:*'
            redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

            if episode and len(redis_episode_names) > 0:
                episode_result  = redis_ctl.hgetall(redis_episode_names[0])
                episode_name    = episode_result.get('sg_short_name')

                if project_result and episode_result:
                    redis_sequence_name =  'sg:sequence:'
                    redis_sequence_name += f'*{project}:'       if project      else '*:'
                    redis_sequence_name += f'*{episode_name}:'  if episode_name else '*:'
                    redis_sequence_name += f'*_{sequence}:'     if sequence     else '*:'
                    redis_sequence_name += f'{sequence_id}'     if sequence_id  else '*'
                    redis_sequence_names = redis_ctl.keys(redis_sequence_name.lower())

                    if len(redis_sequence_names) == 0 and projects.get(project):
                        seq_data = {
                            'request_type': 'create',
                            'entity_type':  'Sequence',
                            'data':{
                                'project':  {'type': 'Project', 'id': projects[project]['id']},
                                'episode':  {'type': 'Episode', 'id': int(episode_result.get('id'))},
                                'code':     f'{episode}_{sequence}',
                                'sg_short_name':    sequence,
                                'sg_status_list':   'wtg'
                            }
                        }
                        sg_data.append(seq_data)

        if len(sg_data) > 0:
            sg = sg_con.connect()
            result = sg.batch(sg_data)

            thread_dir  = threading.Thread(target=create_directory, args=(projects, data,))
            thread_dir.start()
        
        # ----------------------------------------- #
        #       CACHE AFTER SEQUENCE PROCESS        #
        # ----------------------------------------- #
        for project_name, project_data in projects.items():
            thread_cache = threading.Thread(
                target  = entity_cache, 
                kwargs  = {'project': project_name}
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

    for each_data in data:
        filters = each_data.get('filters')
        values  = each_data.get('values')

        project     = filters.get('project')
        episode     = filters.get('episode')
        sequence    = filters.get('sequence')
        sequence_id = filters.get('id')

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
        #       GET SEQUENCE ID        #
        # ---------------------------- #
        redis_episode_name =  'sg:episode:'
        redis_episode_name += f'*{project}:'    if project else '*:'
        redis_episode_name += f'*{episode}:*'   if episode else '*:*'
        redis_episode_names = redis_ctl.keys(redis_episode_name.lower())
        
        if len(redis_episode_names) > 0:
            # ---------------------------- #
            #       GET SEQUENCE ID        #
            # ---------------------------- #
            redis_sequence_name =  'sg:sequence:'
            redis_sequence_name += f'*{project}:'       if project      else '*:'
            redis_sequence_name += f'*{episode}:'       if episode      else '*:'
            redis_sequence_name += f'*_{sequence}:'     if sequence     else '*:'
            redis_sequence_name += f'{sequence_id}'     if sequence_id  else '*'
            redis_sequence_names = redis_ctl.keys(redis_sequence_name.lower())

            entity_id = int(redis_sequence_names[0].split(':')[-1]) if len(redis_sequence_names) > 0 else None

            sg_data = {}
            for key, val in values.items():
                sg_data[SG_FIELD_MAPS[key]] = val

            sg_update_data.append(
                {
                    'request_type': 'update',
                    'entity_type':  'Sequence',
                    'entity_id':    entity_id,
                    'data':         sg_data
                }
            )
    
    # ------------------------- #
    #       SHOTGRID UPDATE     #
    # ------------------------- #
    if len(sg_update_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_update_data)

        thread_redis_cache_update = threading.Thread(
            target=entity_cache, 
            kwargs={'project_id': project_id}
        )
        thread_redis_cache_update.start()
                
    return result

# ================================== #
#       SHOTGRID ENTITY DELETE       #
# ================================== #
def sg_entity_delete(body):
    data    = body.get('data')
    result  = []

    # -------------------------------------- #
    #   CACHE SEQUENCES BASED ON PROJECT     #
    # -------------------------------------- #
    projects = {}
    for each_data in data:
        project = each_data.get('project')
        redis_project_names = redis_ctl.keys(f'sg:project:{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])
            
            projects[each_data.get('project')] = {
                'id':   int(project_result.get('id')),
                'code': project_result.get('code'),
                'path': project_result.get('sg_project_path')
            }
    
    if projects:
        # ------------------------------------------ #
        #       CACHE BEFORE SEQUENCE PROCESS        #
        # ------------------------------------------ #
        for project_name, project_data in projects.items():
            entity_cache(project_id=project_data.get('id'))

        sg_data = []
        for sequence_dict in data:
            project     = sequence_dict.get('project')
            episode     = sequence_dict.get('episode')
            sequence    = sequence_dict.get('sequence')
            sequence_id = sequence_dict.get('id')

            # ///// SEQUENCE REDIS ///// #
            redis_episode_name =  'sg:episode:'
            redis_episode_name += f'*{project}:'    if project else '*:'
            redis_episode_name += f'*{episode}:*'   if episode else '*:*'

            redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

            if episode and len(redis_episode_names) > 0:
                episode_result = redis_ctl.hgetall(redis_episode_names[0])
                episode_name = episode_result.get("sg_short_name")
            
                if project_result and episode_result:
                    redis_sequence_name =  'sg:sequence:'
                    redis_sequence_name += f'*{project}:'       if project          else '*:'
                    redis_sequence_name += f'*{episode_name}:'  if episode_name     else '*:'
                    redis_sequence_name += f'*_{sequence}:'     if sequence         else '*:'
                    redis_sequence_name += f'{sequence_id}'     if sequence_id      else '*'

                    redis_sequence_names = redis_ctl.keys(redis_sequence_name.lower())

                    if len(redis_sequence_names) > 0 and projects.get(project):
                        seq_data = {
                            'request_type': 'delete',
                            'entity_type':  'Sequence',
                            'entity_id':    int(redis_sequence_names[0].split(':')[-1])
                        }
                        sg_data.append(seq_data)

        if len(sg_data) > 0:
            sg = sg_con.connect()
            result = sg.batch(sg_data)

            thread_dir  = threading.Thread(target=delete_directory, args=(projects, data,))
            thread_dir.start()

        # ----------------------------------------- #
        #       CACHE AFTER SEQUENCE PROCESS        #
        # ----------------------------------------- #
        for project_name, project_data in projects.items():
            thread_cache = threading.Thread(
                target  = entity_cache, 
                kwargs  = {'project_id': project_data.get('id')}
            )
            thread_cache.start()

    return result

# ===================================== #
#       SEQUENCE CREATE DIRECTORY       #
# ===================================== #
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
        True
    '''
    cur_platform = sys.platform

    for sequence_dict in data:
        if sequence_dict.get('directory') == True:
            project_path = projects[sequence_dict.get('project')]['path']

            if cur_platform.lower() == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if os.path.exists(project_path):
                for _dir in dir_template.SEQUENCE_DIRECTORIES:
                    dir_path = f'{project_path}/{_dir.format(ep=sequence_dict.get("episode"), seq=sequence_dict.get("sequence"))}'
                    gen_utils.make_dirs(dir_path)

    return True

# ===================================== #
#       SEQUENCE DELETE DIRECTORY       #
# ===================================== #
def delete_directory(projects, data):
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
        True
    '''
    cur_platform = sys.platform

    for sequence_dict in data:
        if sequence_dict.get('directory') == True:
            project_path = projects[sequence_dict.get('project')]['path']

            if cur_platform.lower() == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if os.path.exists(project_path):
                for _dir in dir_template.SEQUENCE_DIRECTORIES:
                    dir_path = f'{project_path}/{_dir.format(ep=sequence_dict.get("episode"), seq=sequence_dict.get("sequence"))}'

    return True
