import os
import re
import sys
import threading

from . import sg_entity_utils, sg_project
from .. import dir_template, gen_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'episode_id': 'sg_episode.Episode.id',
    'episode_code': 'sg_episode.Episode.code',
    'episode_short_name': 'sg_episode.Episode.sg_short_name',
    'sequence_id': 'sg_sequence.Sequence.id',
    'sequence_code': 'sg_sequence.Sequence.code',
    'sequence_short_name': 'sg_sequence.Sequence.sg_short_name',
    'shot': 'code',
    'short_name': 'sg_short_name',
    'status': 'sg_status_list',
    'description': 'description',
    'cut_in': 'sg_cut_in',
    'cut_out': 'sg_cut_out',
    'cut_duration': 'sg_cut_duration',
    'frame_start': 'sg_frame_start',
    'frame_end': 'sg_frame_end',
    'frame_duration': 'sg_frame_duration',
    'master': 'sg_master',
    'assets': 'assets',
    'parent_shots': 'parent_shots',
    'sub_shots': 'shots',
    'sg_short_name': 'short_name'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = [
    'code', 
    'name', 
    'shot', 
    'short_name'
]
NESTED_ENTITY_FOR_REDIS_FIELDS = {
    'episode':{
        'sg_episode.episode.id': 'sg_episode.Episode.id',
        'sg_episode.episode.code': 'sg_episode.Episode.code',
        'sg_episode.episode.sg_short_name': 'sg_episode.Episode.sg_short_name'
    },
    'sequence':{
        'sg_sequence.sequence.id': 'sg_sequence.Sequence.id',
        'sg_sequence.sequence.code': 'sg_sequence.Sequence.code',
        'sg_sequence.sequence.sg_short_name': 'sg_sequence.Sequence.sg_short_name'
    }
}

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    project = ''
    redis_pattern = ''
    sg_result = []

    if kwargs.get('project') == None:
        return []

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
            'Shot', 
            filters = [['project', 'name_contains', project]],
            fields  = list(SG_FIELD_MAPS.values()),
            order   = [{'field_name': 'code', 'direction':'asc'}]
        )

        redis_pattern = f'sg:shot:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        _sg_project  = elem.get('project')
        _sg_episode  = elem.get('sg_episode.Episode.code')
        _sg_sequence = elem.get('sg_sequence.Sequence.code')
        
        if _sg_project and _sg_episode and _sg_sequence:
            redis_name =  'sg:shot:'
            redis_name += f'{_sg_project.get("name")}:'
            redis_name += f'{_sg_episode}:'
            redis_name += f'{_sg_sequence}:'
            redis_name += f'{elem.get("code")}:'
            redis_name += f'{elem.get("id")}'
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))

    return True

def sg_entity_single_sequence_search(project, episode, sequence, shot, shot_id, longname=False):
    result = []
    redis_names = []

    if longname:
        redis_names = redis_ctl.keys(f'sg:shot:*{shot.lower()}:*')

    else:
        redis_name =  'sg:shot:'
        redis_name += f'*{project}:'    if project  else '*:'
        redis_name += f'*{episode}:'    if episode  else '*:'
        redis_name += f'*_{sequence}:'  if sequence else '*:'
        redis_name += f'*_{shot}:'      if shot     else '*:'
        redis_name += f'{shot_id}'      if shot_id  else '*'
        redis_names = redis_ctl.keys(redis_name.lower())

    if len(redis_names) > 0:
        for redis_name in sorted(redis_names):
            shot_data = redis_ctl.hgetall(redis_name)
            result.append(shot_data)
        
        return result
    
    else:
        if project:
            entity_cache({'project': project})
            redis_names = redis_ctl.keys(redis_name.lower())

            if len(redis_names) > 0:
                for redis_name in sorted(redis_names):
                    shot_data = redis_ctl.hgetall(redis_name)
                    result.append(shot_data)
            return result
            
        else:
            return []

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    episode = body.get('episode')
    sequence = body.get('sequence')
    sequences = body.get('sequences')
    shot = body.get('shot')
    shots = body.get('shots')
    shot_id = body.get('id')
    shot_ids = body.get('ids')
    longname = body.get('longname') or False

    valid_keys = {
        'shotgrid',
        'project',
        'episode',
        'sequence',
        'sequences',
        'shot',
        'shots',
        'id',
        'ids',
        'longname'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    if sequences:
        result = []
        for seq in sequences:
            seq_data   = sg_entity_single_sequence_search(project, episode, seq, shot, shot_id)
            seq_result = sg_entity_utils.search_response(
                data        = seq_data, 
                shotgrid    = shotgrid, 
                sg_fields   = SG_FIELD_MAPS_INVERT, 
                str_fields  = STR_FIELDS,
                nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
            )

            result.append(seq_result)
        
        return result
    
    if shots:
        result = []
        for _shot in shots:
            shot_data   = sg_entity_single_sequence_search(project, episode, sequence, _shot, shot_id)
            shot_result = sg_entity_utils.search_response(
                data        = shot_data, 
                shotgrid    = shotgrid, 
                sg_fields   = SG_FIELD_MAPS_INVERT, 
                str_fields  = STR_FIELDS,
                nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
            )
            result.append(shot_result)
        
        return result
    
    elif shot_ids:
        result = []
        for _id in shot_ids:
            shot_data   = sg_entity_single_sequence_search(project, episode, sequence, shot, _id)
            shot_result = sg_entity_utils.search_response(
                data        = shot_data, 
                shotgrid    = shotgrid, 
                sg_fields   = SG_FIELD_MAPS_INVERT, 
                str_fields  = STR_FIELDS,
                nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
            )
            result.append(shot_result)

        return result
    
    else:
        result = sg_entity_single_sequence_search(project, episode, sequence, shot, shot_id, longname)
        return sg_entity_utils.search_response(
            data        = result, 
            shotgrid    = shotgrid, 
            sg_fields   = SG_FIELD_MAPS_INVERT, 
            str_fields  = STR_FIELDS,
            nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
        )

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data    = body.get('data')
    result  = []
    shot_longname_template = ''

    # ------------------------------------- #
    #   CACHE EPISODES BASED ON PROJECT     #
    # ------------------------------------- #
    projects = {}
    for each_data in data:
        project = each_data.get('project')
        redis_project_names = redis_ctl.keys(f'sg:project:{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])

            projects[each_data.get('project')] = {
                'id': int(project_result.get('id')),
                'code': project_result.get('code'),
                'path': project_result.get('sg_project_path'),
                'pattern': {
                    'shot':sg_project.sg_entity_search({'project':project})[0]['project_config']['pattern']['shot']
                }
            }
    
    if projects:
        # ----------------------------------------- #
        #       CACHE BEFORE EPISODE PROCESS        #
        # ----------------------------------------- #
        for project_name, project_data in projects.items():
            entity_cache(project_id=project_data.get('id'))

        sg_data = []
        for shot_dict in data:
            project     = shot_dict.get('project')
            episode     = shot_dict.get('episode')
            sequence    = shot_dict.get('sequence')
            shot        = shot_dict.get('shot')
            shot_id     = shot_dict.get('id')
            redis_episode_name =  'sg:episode:'
            redis_episode_name += f'*{project}:'    if project else '*:'
            redis_episode_name += f'*{episode}:*'   if episode else '*:*'
            redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

            redis_sequence_name =  'sg:sequence:'
            redis_sequence_name += f'*{project}:'       if project  else '*:'
            redis_sequence_name += f'*{episode}:'       if episode  else '*:'
            redis_sequence_name += f'*_{sequence}:*'    if sequence else '*:*'
            redis_sequence_names = redis_ctl.keys(redis_sequence_name.lower())

            if len(redis_episode_names) > 0 and len(redis_sequence_names) > 0:
                episode_result  = redis_ctl.hgetall(redis_episode_names[0])
                sequence_result = redis_ctl.hgetall(redis_sequence_names[0])

                episode_name    = episode_result.get('sg_short_name')   if episode_result.get('sg_short_name')  else episode
                sequence_name   = sequence_result.get('sg_short_name')  if sequence_result.get('sg_short_name') else sequence
                
                if episode_result and sequence_result:
                    redis_shot_name =  'sg:shot:'
                    redis_shot_name += f'*{project}:'   if project  else '*:'
                    redis_shot_name += f'*{episode}:'   if episode  else '*:'
                    redis_shot_name += f'*_{sequence}:' if sequence else '*:'
                    redis_shot_name += f'*_{shot}:'     if shot     else '*:'
                    redis_shot_name += f'{shot_id}'     if shot_id  else '*'
                    redis_shot_names = redis_ctl.keys(redis_shot_name.lower())

                    if len(redis_shot_names) == 0 and projects.get(project):
                        shot_data = {
                            'request_type': 'create',
                            'entity_type':  'Shot',
                            'data':{
                                'project':          {'type': 'Project', 'id': projects[project]['id']},
                                'sg_episode':       {'type': 'Episode', 'id': int(episode_result.get('id'))},
                                'sg_sequence':      {'type': 'Sequence', 'id': int(sequence_result.get('id'))},
                                'code':             projects[project]['pattern']['shot']['longname'].format(
                                    project=projects[project]['code'],
                                    episode=episode_name,
                                    sequence=sequence_name,
                                    shot=shot,
                                ),
                                'sg_short_name':    shot,
                                'sg_status_list':   'wtg',
                                'sg_cut_in':        int(shot_dict.get('cut_in')) if shot_dict.get('cut_in') else None,
                                'sg_cut_out':       int(shot_dict.get('cut_out')) if shot_dict.get('cut_out') else None,
                                'sg_cut_duration':  int(shot_dict.get('cut_duration')) if shot_dict.get('cut_duration') else None
                            }
                        }
                        sg_data.append(shot_data)

        if len(sg_data) > 0:
            sg = sg_con.connect()

            result = sg.batch(sg_data)

            thread_dir  = threading.Thread(target=create_directory, args=(projects, data,))
            thread_dir.start()

        # ---------------------------------------- #
        #       CACHE AFTER EPISODE PROCESS        #
        # ---------------------------------------- #
        for project_name, project_data in projects.items():
            thread_cache = threading.Thread(
                target=entity_cache, 
                kwargs={'project': project_name}
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

    multi_entities = {
        'asset_ids': {'type': 'Asset', 'field': 'assets'},
        'parent_shots': {'type': 'Shot', 'field': 'parent_shots'},
        'sub_shots': {'type': 'Shot', 'field': 'shots'}
    }

    for each in data:
        filters = each.get('filters')
        values  = each.get('values')
        multi_entity_update_modes  = each.get('multi_entity_update_modes')  # add, remove, set // default: set

        project     = filters.get('project')
        episode     = filters.get('episode')
        sequence    = filters.get('sequence')
        shot        = filters.get('shot')
        shot_id     = filters.get('id')

        if project:
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

            # ------------------------------ #
            #       GET EPISODE REDIS        #
            # ------------------------------ #
            if project_id:
                redis_episode_name =  'sg:episode:'
                redis_episode_name += f'*{project}:'    if project else '*:'
                redis_episode_name += f'*{episode}:*'   if episode else '*:*'
                redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

                if len(redis_episode_names) > 0:
                    # ------------------------- #
                    #       GET SEQUENCE        #
                    # ------------------------- #
                    redis_sequence_name = 'sg:sequence:'
                    redis_sequence_name += f'*{project}:'       if project  else '*:'
                    redis_sequence_name += f'*{episode}:'       if episode  else '*:'
                    redis_sequence_name += f'*_{sequence}:*'    if sequence else '*:*'
                    redis_sequence_names = redis_ctl.keys(redis_sequence_name.lower())

                    if len(redis_sequence_names) > 0:
                        # --------------------- #
                        #       GET SHOT        #
                        # --------------------- #
                        redis_shot_name =  'sg:shot:'
                        redis_shot_name += f'*{project}:'   if project  else '*:'
                        redis_shot_name += f'*{episode}:'   if episode  else '*:'
                        redis_shot_name += f'*_{sequence}:' if sequence else '*:'
                        redis_shot_name += f'*_{shot}:'     if shot     else '*:'
                        redis_shot_name += f'{shot_id}'     if shot_id  else '*'
                        redis_shot_names = redis_ctl.keys(redis_shot_name.lower())

                        if len(redis_shot_names) > 0:
                            entity_id = int(redis_shot_names[0].split(':')[-1])
                            
                            # /////// UPDATE VALUES ////// #
                            sg_data = {}
                            if values:
                                for key, val in values.items():
                                    if key in multi_entities.keys() and key.endswith('ids'):
                                        sg_data[multi_entities[key]['field']] = [{'type': multi_entities[key]['type'], 'id': int(each_id)} for each_id in val]
                                    
                                    else:
                                        sg_data[SG_FIELD_MAPS[key]] = val
                                
                                request_data = {
                                    'request_type': 'update',
                                    'entity_type':  'Shot',
                                    'entity_id':    entity_id,
                                    'data':         sg_data,
                                }

                                # ////// MULTI ENTITY UPDATE MODE ////// #
                                if multi_entity_update_modes:
                                    multi_entity_mode_ops = {}
                                    for key, val in multi_entity_update_modes.items():
                                        multi_entity_mode_ops[multi_entities[key]['field']] = val

                                    request_data['multi_entity_update_modes'] = multi_entity_mode_ops

                                sg_update_data.append(request_data)
    
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

    for shot_dict in data:
        if shot_dict.get('directory') == True:
            project     = shot_dict.get('project')
            episode     = shot_dict.get('episode')
            sequence    = shot_dict.get('sequence')
            shot        = shot_dict.get('shot')
            
            project_path = projects[project]['path']

            if cur_platform.lower() == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if os.path.exists(project_path):
                for _dir in dir_template.SHOT_DIRECTORIES:
                    # -------------------- #
                    #       RELEASE        #
                    # -------------------- #  
                    if _dir.startswith('release/'):
                        for reltype in dir_template.RELEASE_TYPE_DIRECTORIES['shot']:           # RELEASE TYPE
                            dir_path = f'{project_path}/{_dir.format(ep=episode, seq=sequence, shot=shot, reltype=reltype)}'
                            gen_utils.make_dirs(dir_path)

                    else:
                        for step, dccs in dir_template.STEP_DCC_DIRECTORIES['shot'].items():        # STEP
                            # ----------------- #
                            #       WORK        #
                            # ----------------- #  
                            if _dir.startswith('work/'):
                                for dcc in dccs:                                                    # DCC
                                    for elem in dir_template.DCC_ELEM_DIRECTORIES[dcc]:             # ELEMENTS
                                        dir_path = f'{project_path}/{_dir.format(ep=episode, seq=sequence, shot=shot, step=step, dcc=dcc, elem=elem)}'
                                        gen_utils.make_dirs(dir_path)

                            # ----------------------------- #
                            #       REVIEW / PUBLISH        #
                            # ----------------------------- # 
                            else:
                                dir_path = f'{project_path}/{_dir.format(ep=episode, seq=sequence, shot=shot, step=step)}'
                                gen_utils.make_dirs(dir_path)
                
    return True

