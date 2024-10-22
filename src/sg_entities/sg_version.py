import ast
import os
import re
import sys
import threading
from ast import literal_eval
from pprint import pprint

from . import sg_entity_utils, sg_asset, sg_shot, sg_timeLog, sg_task
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'name': 'code',
    'entity': 'entity',
    'description': 'description',
    'step_id': 'sg_version_step.Step.id',
    'step_code': 'sg_version_step.Step.code',
    'step_short_name': 'sg_version_step.Step.short_name',
    'task_id': 'sg_task.Task.id',
    'task_code': 'sg_task.Task.content',
    'task_priority': 'sg_task.Task.sg_step_id',
    'version_code': 'sg_version_code_number',
    'work_file': 'sg_worked_file_name',
    'user': 'user',
    'note': 'open_notes',
    'status': 'sg_status_list',
    'published_files': 'published_files',
    'created_at': 'created_at',
    'path_to_client': 'sg_path_to_client',
    'path_to_movie': 'sg_path_to_movie',
    'path_to_frames': 'sg_path_to_frames',
    'path_to_thumbnail': 'sg_path_to_thumbnail',
    'publish_status': 'sg_publish_status',
    'version_type': 'sg_version_type',
    'to_client': 'sg_sent_to_client'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']
NESTED_ENTITY_FOR_REDIS_FIELDS = {
    'step':{
        'sg_version_step.step.id': 'sg_version_step.Step.id',
        'sg_version_step.step.code': 'sg_version_step.Step.code',
        'sg_version_step.step.short_name': 'sg_version_step.Step.short_name'
    },
    'task':{
        'sg_task.task.id': 'sg_task.Task.id',
        'sg_task.task.code': 'sg_task.Task.content',
        'sg_task.task.sg_step_id': 'sg_task.Task.sg_step_id'
    }
}


def sg_entity_filter_search(entity, entities, body, filters, shotgrid):
    entity_type = {
        'episode': 'Shot',
        'sequence': 'Shot',
        'shot': 'Shot',
        'asset': 'Asset'
    }

    filters += [['entity', 'type_is', entity_type.get(entity)]]
    result  =  []

    dict_index = 0
    for i, elem in enumerate(filters):
        if isinstance(elem, dict):
            dict_index = i
            break
    
    if body.get('shot') or body.get('asset'):
        if entities:
            for entity_name in entities:
                body[entity] = entity_name
                redis_pattern_dict = sg_entity_utils.entity_redis_pattern(body)
                filters[dict_index]['filters'] += [['entity', 'name_is', redis_pattern_dict.get('entity_name')]]
        else:
            del filters[dict_index]
    else:
        if entities:
            for entity_name in entities:
                body[entity] = entity_name
                redis_pattern_dict = sg_entity_utils.entity_redis_pattern(body)
                filters[dict_index]['filters'] += [['entity', 'name_contains', redis_pattern_dict.get('entity_name')]]

    sg = sg_con.connect()
    result = sg.find(
        entity_type='Version', 
        filters=filters, 
        fields=list(SG_FIELD_MAPS.values())
    )

    if shotgrid:
        return result
    else:
        return sg_entity_utils.entity_response_adapter(
            data = result, 
            sg_fields = SG_FIELD_MAPS_INVERT, 
            str_fields = ['code']
        )

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    episode = body.get('episode')
    episodes = body.get('episodes')
    sequence = body.get('sequence')
    sequences = body.get('sequences')
    shot = body.get('shot')
    shots = body.get('shots')
    asset = body.get('asset')
    assets = body.get('assets')
    asset_type = body.get('asset_type')
    asset_types = body.get('asset_types')
    step = body.get('step')
    task = body.get('task')
    entity_id = body.get('id')
    entity_ids = body.get('ids')
    path_to_movie = body.get('path_to_movie')
    path_to_frames = body.get('path_to_frames')
    path_to_client = body.get('path_to_client')
    work_file = body.get('work_file')
    version_type = body.get('version_type')
    entity = body.get('entity') or ''

    if entity_ids:
        _filters = [
            {
                'filter_operator': 'any',
                'filters': []
            }
        ]
        for _id in entity_ids:
            _filters[0]['filters'].append(['id', 'is', int(_id)])
        
        sg = sg_con.connect()
        result = sg.find(
            'Version', 
            filters=_filters, 
            fields=list(SG_FIELD_MAPS.values())
        )
        if shotgrid:
            return result
        else:
            return sg_entity_utils.entity_response_adapter(
                data = result, 
                sg_fields = SG_FIELD_MAPS_INVERT, 
                str_fields = ['code'],
                nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
        )

    else:
        valid_keys = {
            'shotgrid',
            'project',
            'episode',
            'episodes',
            'sequence',
            'sequences',
            'shot',
            'shots',
            'asset',
            'assets',
            'asset_type',
            'asset_types',
            'step',
            'task',
            'id',
            'path_to_movie',
            'path_to_frames',
            'path_to_client',
            'work_file',
            'entity'
        }

        if not set(body.keys()).issubset(valid_keys):
            return []

        entities = []
        filters = []
        
        # ------------------ #
        #       FILTERS      #
        # ------------------ #
        filters_inner = {}
        filters_inner['filter_operator'] = 'any'
        filters_inner['filters'] = []

        if project: 
            filters += [['project', 'name_contains', project]]
        
        if entity_id: 
            filters += [['id', 'is', int(entity_id)]]
        
        if entity:
            filters += [['entity', 'type_is', entity.title()]]
        
        if step: 
            filters += [['sg_version_step.Step.short_name', 'is', step]]
    
        if task: 
            filters += [['sg_task.Task.content', 'is', task]]
    
        if path_to_movie: 
            filters += [['sg_path_to_movie', 'is', path_to_movie]]
    
        if path_to_frames: 
            filters += [['sg_path_to_frames', 'is', path_to_frames]]
    
        if path_to_client: 
            filters += [['sg_path_to_client', 'is', path_to_client]]
        
        if work_file:
            filters += [['sg_worked_file_name', 'is', work_file]]
        
        if version_type:
            filters += [['sg_version_type', 'is', version_type]]

        filters.append(filters_inner)

        # /////// SHOT //////// #
        if episode or episodes:   
            entity = 'episode' 
            entities = episodes or [episode]

        if sequences or sequence:
            entity = 'sequence'
            entities = sequences or [sequence]

        if shots or shot:
            entity = 'shot'
            entities = shots or [shot]
        
        # /////// ASSET //////// #
        if assets or asset:
            entity = 'asset'
            entities = assets or [asset]

        elif asset_types or asset_type:
            entity = 'asset' 
            types = asset_types or [asset_type]
            entities = []

            for type_ in types:
                redis_name = f'sg:asset:{project}:{type_}:*'.lower()
                redis_keys = redis_ctl.keys(redis_name)
                entities += [each.split(':')[4] for each in redis_keys]

        # //////// ENTITY ID //////// #
        if entity_id:
            sg = sg_con.connect()
            result = sg.find(
                'Version', 
                filters=[['id', 'is', entity_id]], 
                fields=list(SG_FIELD_MAPS.values())
            )
            if shotgrid:
                return result
            else:
                return sg_entity_utils.entity_response_adapter(
                data = result, 
                sg_fields = SG_FIELD_MAPS_INVERT, 
                str_fields = ['code'],
                nested_entity_fields = NESTED_ENTITY_FOR_REDIS_FIELDS
            )
        else:
            return sg_entity_filter_search(entity, entities, body, filters, shotgrid)

# ========================= #
#       VERSION TASK        #
# ========================= #
def sg_version_task(sg, entity_type, entity_name, step, task):
    task_id = None

    _filters = [
        ['step.Step.short_name', 'is', step],
        ['content', 'is', task]
    ]

    if entity_type == 'shot':
        _filters.append(['entity.Shot.code', 'is', entity_name])

    elif entity_type == 'asset':
        _filters.append(['entity.Asset.code', 'is', entity_name])
        
    sg_result = sg.find_one(
        entity_type='Task',
        filters=_filters
    )

    if sg_result:
        task_id = sg_result.get('id')
    
    return task_id

# ============================= #
#       VERSION PLAYLIST        #
# ============================= #
def sg_version_playlist(sg, project, project_id, step, step_id, playlist):    
    sg_result = sg.find_one(
        entity_type='Playlist',
        filters=[
            ['project', 'name_contains', project],
            ['sg_step.Step.short_name', 'is', step],
            ['code', 'is', playlist]
        ]
    )

    if sg_result:
        return sg_result.get('id')

    else:
        sg_create_result = sg.create(
            entity_type='Playlist',
            data={
                'project': {'type': 'Project', 'id': project_id},
                'sg_step': {'type': 'Step', 'id': step_id},
                'code': playlist,
            }
        )
        return sg_create_result.get('id')

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    sg_data = {}
    results  = []

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
                'id':   int(project_result.get('id')),
                'code': project_result.get('code'),
            }

    if projects:
        for project_name, project_data in projects.items():
            sg_shot.entity_cache(project=project_name)
            sg_asset.entity_cache(project=project_name)

        sg = sg_con.connect()

        for each_data in data:
            project = each_data.get('project')
            project_id = projects[project]['id']
            step = each_data.get('step')
            task = each_data.get('task')
            status = each_data.get('status') or 'rev'
            task_status = each_data.get('task_status')
            publish_status = each_data.get('publish_status')
            version_type = each_data.get('version_type')

            submitter = each_data.get('submitted_by')
            name = each_data.get('name')
            version_code = each_data.get('version_code')
            description = each_data.get('description')
            playlist = each_data.get('playlist')
            note = each_data.get('note')
            note_type = each_data.get('note_type')
            work_file = each_data.get('work_file')
            path_to_movie = each_data.get('path_to_movie')
            path_to_frames = each_data.get('path_to_frames')
            path_to_client = each_data.get('path_to_client')
            path_to_thumbnail = each_data.get('path_to_thumbnail')
            time_logged = each_data.get('time_logged')
            published_file_ids = each_data.get('published_file_ids')

            redis_pattern_dict = sg_entity_utils.entity_redis_pattern(each_data)
            redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())

            entity_data = {}
            sg_note_create_result = {}
            upload_file_path = ''

            if len(redis_pattern_dict.get('redis_names')) > 0:
                entity_data = redis_ctl.hgetall(redis_pattern_dict.get('redis_names')[0])
            
            entity_id = None
            entity_type = None
            step_id = None
            task_id = None
            playlist_id = None
            entity_name = None
            user_id = sg_entity_utils.sg_user_id(submitter)

            if len(redis_step_names) > 0:
                step_id = int(redis_step_names[0].split(':')[-1])
            
            if playlist and project and project_id and step and step_id:
                playlist_id = sg_version_playlist(sg, project, project_id, step, step_id, playlist)
            
            if len(redis_pattern_dict['redis_names']) > 0:
                entity_type = redis_pattern_dict.get('entity_type')
                entity_id = int(redis_pattern_dict['redis_names'][0].split(':')[-1])
                entity_name = redis_pattern_dict['redis_names'][0].split(':')[-2]
            
            if task and entity_type:
                task_id = sg_version_task(sg, entity_type.lower(), entity_name, step, task)
                

            # ------------------------------------- #
            #       BASE CREATE VERSION DATA        #
            # ------------------------------------- #
            sg_data = {
                'project': {'type': 'Project', 'id': project_id},
                'entity': {'type': entity_type, 'id': entity_id},
                'sg_status_list': status,
                'code': name,
                'description': description
            }

            # if version_code: 
            #     sg_data['sg_version_code_number'] = str(version_code)

            if playlist_id: 
                sg_data['playlists'] = [{'type': 'Playlist', 'id': playlist_id}]
            
            if step_id: 
                sg_data['sg_version_step'] = {'type': 'Step', 'id': step_id}
            
            if task_id: 
                sg_data['sg_task'] = {'type': 'Task', 'id': task_id}
            
            if task_id: 
                sg_data['sg_task'] = {'type': 'Task', 'id': task_id}
            
            if user_id: 
                sg_data['user'] = {'type': 'HumanUser', 'id': user_id}
            
            if publish_status: 
                sg_data['sg_publish_status'] = publish_status
            
            if path_to_movie: 
                sg_data['sg_path_to_movie'] = path_to_movie
            
            if path_to_frames: 
                sg_data['sg_path_to_frames'] = path_to_frames
            
            if path_to_client: 
                sg_data['sg_path_to_client'] = path_to_client
            
            if path_to_thumbnail: 
                sg_data['sg_path_to_thumbnail'] = path_to_thumbnail
            
            if work_file:
                sg_data['sg_worked_file_name'] = work_file
            
            # if version_type:
            #     sg_data['sg_version_type'] = version_type.title()
            
            if path_to_movie: 
                upload_file_path = path_to_movie

            elif path_to_frames: 
                upload_file_path = path_to_frames
            
            # ----------------- #
            #       NOTE        #
            # ----------------- #
            if note:
                note_types = [
                    'Internal',
                    'External',
                    'Client'
                ]
                subject =  'Note on '
                subject += f'{entity_name} '
                subject += f'{step} ' if step else ''
                subject += f'{task} ' if task else ''

                sg_note_data = {
                    'content':  note,
                    'subject':  subject,
                    'sg_status_list': 'opn'
                }

                if project_id:
                    sg_note_data['project'] = {'type':  'Project',  'id': project_id}
                
                if step_id:
                    sg_note_data['sg_steps'] = [{'type': 'Step',     'id': step_id}]
                
                if task_id:
                    sg_note_data['tasks'] = [{'type': 'Task',     'id': task_id}]

                if note_type and note_type.title() in note_types:
                    sg_note_data['sg_note_type'] = note_type.title()
                
                if entity_type and entity_id:
                    sg_note_data['note_links'] = [{'type': entity_type, 'id': entity_id}]
                
                if user_id and submitter:
                    subject =  f'{submitter.title()}'
                    subject += '\'s Note on '
                    subject += f'{entity_name} ' if entity_name  else ''
                    subject += f'{step} ' if step else ''
                    subject += f'{task} ' if task else ''

                    sg_note_data['user']    = {'type': 'HumanUser', 'id': user_id}
                    sg_note_data['subject'] = subject
                
                sg_note_create_result = sg.create(
                    entity_type='Note',
                    data=sg_note_data
                )

            # # ----------------------------------------- #
            # #       ADD ENTITY INFO INTO VERSION        #
            # # ----------------------------------------- #
            # # ----- SHOT ----- #
            # if entity_type == 'Shot' and entity_data:
            #     sg_data['sg_episode_version'] = {'type': 'Episode', 'id': int(ast.literal_eval(entity_data['sg_episode.episode.id']))}
            #     sg_data['sg_sequence'] = {'type': 'Sequence', 'id': int(ast.literal_eval(entity_data['sg_sequence.sequence.id']))}
            #     sg_data['sg_shot'] = {'type': 'Shot', 'id': int(entity_data.get('id'))}

            # # ----- ASSET ----- #
            # elif entity_type == 'Asset' and entity_data:
            #     sg_data['sg_asset'] = {'type': 'Asset', 'id': int(entity_data.get('id'))}

            # ----------------------------- #
            #       PUBLISHED FILE IDS      #
            # ----------------------------- #
            if published_file_ids:
                published_file_data = []

                for each_id in published_file_ids:
                    published_file_data.append({'type': 'PublishedFile', 'id': int(each_id)})

                sg_data['published_files'] = published_file_data
                
            # -------------------------------------------------------- #
            #       CREAT VERSION, AND UPDATE NOTE INTO VERSION        #
            # -------------------------------------------------------- #
            if entity_data:
                result = sg.create(
                    entity_type = 'Version',
                    data = sg_data
                )
                results.append(result)

                if result and task_status and task_id:
                    sg.update(
                        'Task',
                        entity_id=task_id,
                        data={'sg_status_list': task_status}
                    )

                # # ----------------------------- #
                # #       UPLOAD MOVIE FILE       #
                # # ----------------------------- #
                # if upload_file_path and result and not '%04d' in upload_file_path:
                #     thread_upload = threading.Thread(
                #         target=upload_file, 
                #         args=(
                #             sg, 
                #             result.get('id'), 
                #             upload_file_path,
                #         )
                #     )
                #     thread_upload.start()
                
                # --------------------- #
                #       TIME LOGGED     #
                # --------------------- #
                if time_logged:
                    timelog_payload = {
                        'data': [
                            {
                                'project': project,
                                'task_id': task_id,
                                'time_logged': time_logged,
                                'user': submitter,
                                'time_unit': 'minute'
                            }
                        ]
                    }
                    sg_timeLog.sg_entity_create(timelog_payload)

                # ------------------------------------ #
                #       UPDATE VERSION INTO NOTE       #
                # ------------------------------------ #
                if sg_note_create_result and result:
                    sg.update(
                        entity_type = 'Note',
                        entity_id = sg_note_create_result.get('id'),
                        data = {'note_links': [{'type': 'Version', 'id': result.get('id')}]},
                        multi_entity_update_modes = {'note_links': 'add'},
                    )

    return results

# ================================ #
#       SHOTGRID UPLOAD FILE       #
# ================================ #
def upload_file(sg, entity_id, file):
    platform = sys.platform
    upload_id = 0

    if platform == 'linux':
        file = sg_entity_utils.convert_path_windows_to_linux(file)

    if os.path.exists(file):
        upload_id = sg.upload(
            entity_type='Version',
            entity_id=entity_id,
            path=file,
            field_name='sg_uploaded_movie',
            display_name=os.path.split(file)[-1]
        )

    return upload_id

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data') or []
    sg_data = []
    result = []

    multi_entities = {
        'published_file_ids': {'type': 'PublishedFile', 'field': 'published_files'}
    }

    # ------------------------------------- #
    #   CACHE EPISODES BASED ON PROJECT     #
    # ------------------------------------- #
    for each in data:
        filters = each.get('filters')
        values = each.get('values')
        version_id = filters.get('id')
        sg_values = {}

        for key, value in values.items():
            if key in multi_entities.keys():
                sg_values[multi_entities[key]['field']] = [{'type': multi_entities[key]['type'], 'id': int(each_id)} for each_id in value]
            else:
                sg_values[SG_FIELD_MAPS[key]] = value

        if version_id:
            sg_data.append(
                {
                    'request_type': 'update',
                    'entity_type': 'Version',
                    'entity_id': version_id,
                    'data': sg_values
                }
            ) 

    if len(sg_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_data)

    return result

# ================================== #
#       SHOTGRID ENTITY DELETE       #
# ================================== #
def sg_entity_delete(body):
    data    = body.get('data')
    result = []
    sg_data = []

    for each_data in data:
        entity_id = each_data.get('id')
        if entity_id:
            each_sg_data = {
                'request_type': 'delete',
                'entity_type': 'Version',
                'entity_id': entity_id
            }

            sg_data.append(each_sg_data)
    
    if len(sg_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_data)

    return result

