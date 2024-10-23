import re
from . import sg_entity_utils, sg_asset, sg_shot
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl
from pprint import pprint

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'entity': 'entity',
    'name': 'name',
    'code': 'code',
    'status': 'sg_status_list',
    'step_id': 'sg_step.Step.id',
    'step_code': 'sg_step.Step.code',
    'step_short_name': 'sg_step.Step.short_name',
    'task_id': 'task.Task.id',
    'task_code': 'task.Task.content',
    'task_priority': 'task.Task.sg_step_id',
    'version': 'version',
    'versions': 'sg_versions',
    'namespace': 'sg_namespace',
    'asset': 'sg_asset_link',
    'version_number': 'version_number',
    'version_code': 'sg_version_code',
    'work_file': 'sg_worked_file_name',
    'publish_type': 'published_file_type',
    'entity_type': 'sg_entity_type',
    'is_sound_sequence': 'sg_is_sound_sequence',
    'file_path': 'sg_file_path',
    'description': 'description',
    # 'asset_type': 'sg_asset_type',
    'user': 'sg_user',
    'created_at': 'created_at'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']
NESTED_ENTITY_FOR_REDIS_FIELDS = {
    'step':{
        'sg_step.step.id': 'sg_step.Step.id',
        'sg_step.step.code': 'sg_step.Step.code',
        'sg_step.step.short_name': 'sg_step.Step.short_name'
    },
    'task':{
        'task.task.id': 'task.Task.id',
        'task.task.code': 'task.Task.content',
        'task.task.sg_step_id': 'task.Task.sg_step_id'
    }
}

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    entity_id = body.get('id')
    entity_ids = body.get('ids')
    entity = body.get('entity')
    entity_linked_id = body.get('entity_id')
    project = body.get('project')
    step = body.get('step')
    steps = body.get('steps')
    task = body.get('task')
    publish_type = body.get('type') or body.get('publish_type')
    publish_types = body.get('types') or body.get('publish_types')
    publish_file = body.get('publish_file')
    publish_files = body.get('publish_files')
    asset_ids = body.get('asset_ids')
    namespace = body.get('namespace')
    version_code = body.get('version_code')
    version_number = body.get('version_number')
    path_to_movie = body.get('path_to_movie')
    path_to_frames = body.get('path_to_frames')
    latest = body.get('latest') or False
    code = body.get('code')
    asset_type = body.get('asset_type')
    status = body.get('status')

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
            'PublishedFile', 
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
    elif entity_linked_id:
        sg = sg_con.connect()
        result = sg.find(
            'PublishedFile', 
            filters=[
                ['entity', 'is', {'type': 'Asset', 'id':int(entity_linked_id)}]
            ], 
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
            'id',
            'entity',
            'project',
            'episode',
            'sequence',
            'shot',
            'asset_type',
            'asset',
            'variation',
            'step',
            'steps',
            'task',
            'type',
            'publish_type',
            'types',
            'publish_types',
            'publish_file',
            'publish_files',
            'asset_ids',
            'namespace',
            'version_code',
            'version_number',
            'path_to_movie',
            'path_to_frames',
            'latest',
            'status',
            'code'
        }

        if not set(body.keys()).issubset(valid_keys):
            return []
        
        entity_data = {}
        sg_filters = []
        result = []

        sg = sg_con.connect()
        
        if entity_id and entity:
            result = sg.find(
                entity_type = 'PublishedFile',
                filters = [['entity', 'is', {'type': entity, 'id': entity_id}]],
                fields = list(SG_FIELD_MAPS.values())
            )
        else:
            entity_data = sg_entity_utils.entity_redis_pattern(body)
        
        if body.get('shot') or body.get('asset'):
            if entity_data.get('entity_name'): 
                if entity_data.get('entity_type').lower() == 'asset' and len(entity_data.get('redis_names')) > 1:
                    sg_filters += [['entity', 'is', {'type': 'Asset', 'id': int(entity_data.get('redis_names')[0].split(':')[-1])}]]
                else:
                    sg_filters += [['entity', 'name_is', entity_data.get('entity_name')]]
        else:
            if entity_data.get('entity_name'): 
                if entity_data.get('entity_type').lower() == 'asset' and len(entity_data.get('redis_names')) > 1:
                    sg_filters += [['entity', 'is', {'type': 'Asset', 'id': int(entity_data.get('redis_names')[0].split(':')[-1])}]]
                else:
                    sg_filters += [['entity', 'name_contains', entity_data.get('entity_name')]]
        
        if entity:
            sg_filters += [['entity', 'type_is', entity.title()]]

        if asset_type:
            sg_filters += [['sg_asset_type', 'is', asset_type]]

        if publish_type: 
            sg_filters += [['published_file_type.PublishedFileType.code', 'is', publish_type]]

        if step: 
            sg_filters += [['sg_step.Step.short_name', 'is', step]]

        if publish_file: 
            sg_filters += [['sg_file_path', 'is', publish_file]]

        if project: 
            sg_filters += [['project', 'name_contains', project]] 

        if namespace: 
            sg_filters += [['sg_namespace', 'is', namespace]] 

        if task: 
            sg_filters += [['task.Task.content', 'is', task]]

        if version_code: 
            sg_filters += [['sg_version_code', 'is', version_code]]

        if version_number: 
            sg_filters += [['version_number', 'is', version_number]]

        if path_to_movie: 
            sg_filters += [['version.Version.sg_path_to_movie', 'is', path_to_movie]]

        if path_to_frames: 
            sg_filters += [['version.Version.sg_path_to_frames', 'is', path_to_frames]]

        if status: 
            sg_filters += [['sg_status_list', 'is', status]]

        if code: 
            sg_filters += [['code', 'contains', code]]
        
        if steps:
            step_filters = {
                'filter_operator': 'any',
                'filters': []
            }

            for _step in steps:
                step_filters['filters'] += [['sg_step.Step.short_name', 'is', _step]]
            
            sg_filters.append(step_filters)
        
        if asset_ids:
            asset_filters = {
                'filter_operator': 'any',
                'filters': []
            }

            for _id in asset_ids:
                asset_filters['filters'] += [['entity.Asset.id', 'is', _id]]
            
            sg_filters.append(asset_filters)
        
        if publish_types:
            publish_type_filters = {
                'filter_operator': 'any',
                'filters': []
            }

            for _type in publish_types:
                publish_type_filters['filters'] += [['published_file_type.PublishedFileType.code', 'is', _type]]
            
            sg_filters.append(publish_type_filters)

        if publish_files:
            publish_file_filters = {
                'filter_operator': 'any',
                'filters': []
            }

            for _file in publish_files:
                publish_file_filters['filters'] += [['sg_file_path', 'is', _file]]
            
            sg_filters.append(publish_file_filters)
        
        # ///////// RUN FIND ////////// #
        if sg_filters:
            if latest:
                result = sg.find(
                    entity_type = 'PublishedFile',
                    filters = sg_filters,
                    fields = list(SG_FIELD_MAPS.values()),
                    order = [{'field_name': 'created_at','direction': 'desc'}]
                )

                if result:
                    result = [result[0]]

            else:
                result = sg.find(
                    entity_type = 'PublishedFile',
                    filters = sg_filters,
                    fields = list(SG_FIELD_MAPS.values())
                )

        if shotgrid:
            return result

        else:
            return sg_entity_utils.entity_response_adapter(
                data = result, 
                sg_fields = SG_FIELD_MAPS_INVERT, 
                str_fields = STR_FIELDS,
                nested_entity_fields=NESTED_ENTITY_FOR_REDIS_FIELDS
            )

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    result = []

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
        sg = sg_con.connect()

        for project_name, project_data in projects.items():
            sg_shot.entity_cache(project=project_name)
            sg_asset.entity_cache(project=project_name)

        sg_data = []
        for each_data in data:
            asset_type = each_data.get('asset_type')
            asset = each_data.get('asset')
            variation = each_data.get('variation')
            episode = each_data.get('episode')
            sequence = each_data.get('sequence')
            shot = each_data.get('shot')
            step = each_data.get('step')
            task = each_data.get('task')
            status = each_data.get('status') or 'act'
            description = each_data.get('description')
            work_file = each_data.get('work_file')
            publish_file = each_data.get('publish_file')
            namespace = each_data.get('namespace')
            publish_file_type = each_data.get('type')
            version_id = each_data.get('version_id')
            version_ids = each_data.get('version_ids')
            version_number = each_data.get('version_number')
            version_code = each_data.get('version')
            publish_name = each_data.get('publish_name')
            is_sound_sequence = each_data.get('is_sound_sequence')
            user = each_data.get('user')

            project_id = None
            entity_id = None
            step_id = None
            task_id = None
            asset_id = None
            user_id = sg_entity_utils.sg_user_id(user)
            redis_name = ''
            redis_names = []
            entity_type = ''
            data_dict = {
                'request_type': 'create',
                'entity_type':  'PublishedFile',
                'data': {
                    'code': publish_name,
                    'name': publish_name
                }
            }

            if projects.get(project):
                project_id  = projects[project]['id']
                data_dict['data']['project'] = {'type': 'Project', 'id': project_id}

                # ------------------------------ #
                #       CHECK ENTITY DATA        #
                # ------------------------------ #
                if episode or sequence or shot:
                    redis_name = 'sg:shot:'
                    redis_name += f'*{project}:' if project else '*:'
                    redis_name += f'*{episode}:' if episode else '*:'
                    redis_name += f'*_{sequence}:' if sequence else '*:'
                    redis_name += f'*_{shot}:*' if shot else '*:*'
                    entity_type = 'Shot'

                    if asset:
                        asset_redis_name = ''
                        if variation:
                            asset_redis_name = 'sg:asset:'
                            asset_redis_name += f'*{project}:' if project else '*:'
                            asset_redis_name += f'{asset_type}:' if asset_type else '*:'
                            asset_redis_name += f'{asset}' if asset else '*'
                            asset_redis_name += f'_{variation}:*' if variation else '*:*'
                        else:
                            asset_redis_name = 'sg:asset:'
                            asset_redis_name += f'*{project}:' if project else '*:' 
                            asset_redis_name += f'{asset_type}:' if asset_type else '*:'
                            asset_redis_name += f'{asset}:*' if asset else '*:*'
                        
                        asset_redis_names = redis_ctl.keys(asset_redis_name.lower())
                        if len(asset_redis_names) > 0:
                            asset_id = int(asset_redis_names[0].split(':')[-1])

                
                elif asset_type or asset and not shot:
                    entity_type = 'Asset' 

                    if variation:
                        redis_name = 'sg:asset:'
                        redis_name += f'*{project}:' if project else '*:'
                        redis_name += f'{asset_type}:' if asset_type else '*:'
                        redis_name += f'{asset}' if asset else '*'
                        redis_name += f'_{variation}:*' if variation else '*:*'
                    else:
                        redis_name = 'sg:asset:'
                        redis_name += f'*{project}:' if project else '*:' 
                        redis_name += f'{asset_type}:' if asset_type else '*:'
                        redis_name += f'{asset}:*' if asset else '*:*'
                          
                redis_names = redis_ctl.keys(redis_name.lower())
                redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())

            # ------------------- #
            #       ENTITY        #
            # ------------------- #
            if len(redis_names) > 0 and entity_type:
                entity_id = int(redis_names[0].split(':')[-1])
                data_dict['data']['entity'] = {
                    'type': entity_type, 
                    'id': entity_id
                }
            else: 
                sg_shot.entity_cache(project=project)
                redis_names = redis_ctl.keys(redis_name.lower())

                if len(redis_names) > 0 and entity_type:
                    entity_id = int(redis_names[0].split(':')[-1])
                    data_dict['data']['entity'] = {
                        'type': entity_type, 
                        'id': entity_id
                    }
            if entity_id:
                # ----------------- #
                #       STEP        #
                # ----------------- #
                if len(redis_step_names) > 0:
                    step_id = int(redis_step_names[0].split(':')[-1])
                    data_dict['data']['sg_step'] = {
                        'type': 'Step', 
                        'id': step_id
                    }

                # ------------------------------ #
                #       PUBLISH FILE TYPE        #
                # ------------------------------ #
                if publish_file_type:
                    redis_publishedfiletype_names = redis_ctl.keys(f'sg:publishedfiletype:{publish_file_type}:*')                    
                    if len(redis_publishedfiletype_names) > 0:
                        data_dict['data']['published_file_type'] = {
                            'type': 'PublishedFileType', 
                            'id': int(redis_publishedfiletype_names[0].split(':')[-1])
                        }
                
                # ----------------- #
                #       TASK        #
                # ----------------- #
                if task:
                    sg_task_find_result = sg.find_one(
                        entity_type='Task',
                        filters=[
                            ['project', 'is', {'type': 'Project', 'id': project_id}],
                            ['entity', 'is', {'type': entity_type, 'id': entity_id}],
                            ['step', 'is', {'type': 'Step', 'id': step_id}],
                            ['content', 'is', task]
                        ]
                    )
                    
                    if sg_task_find_result:
                        task_id = sg_task_find_result.get('id')
                        data_dict['data']['task'] = {'type': 'Task', 'id': task_id}
                
                if version_id: 
                    data_dict['data']['version'] = {'type': 'Version', 'id': int(version_id)} # VERSION ID
                
                if version_ids:
                    data_dict['data']['sg_versions'] = [{'type': 'Version', 'id': int(_id)} for _id in version_ids] # VERSION IDS
                
                if user_id:
                    data_dict['data']['sg_user'] = {'type': 'HumanUser', 'id': user_id} # USER ID
                    data_dict['data']['created_by'] = {'type': 'HumanUser', 'id': user_id} # USER ID
                
                if entity_type: 
                    data_dict['data']['sg_entity_type'] = entity_type # ENTITY TYPE
                
                if work_file: 
                    data_dict['data']['sg_worked_file_name'] = work_file # WORK FILE
                
                if version_code: 
                    data_dict['data']['sg_version_code'] = version_code # VERSION CODE
                
                if publish_file: 
                    data_dict['data']['sg_file_path'] = publish_file  # PUBLISH FILE
                
                if status: 
                    data_dict['data']['sg_status_list'] = status # STATUS
                
                if description: 
                    data_dict['data']['description'] = description # DESCRIPTION
                
                if namespace: 
                    data_dict['data']['sg_namespace'] = namespace # NAMESPACE
                
                # if asset_type: 
                #     data_dict['data']['sg_asset_type'] = asset_type # ASSET TYPE

                # # /////// ADD ASSET /////// #
                # if entity_type.lower() == 'asset': 
                #     data_dict['data']['sg_asset_link'] = {'type': 'Asset', 'id': entity_id}

                # elif entity_type.lower() == 'shot' and asset_id: 
                #     data_dict['data']['sg_asset_link'] = {'type': 'Asset', 'id': asset_id}

                if version_number: 
                    data_dict['data']['version_number'] = int(version_number)
                    
                else:
                    version_number_regex_result = ''

                    if version_code: 
                        version_number_regex_result = re.findall(r'v([0-9]+)', version_code)

                    if version_number_regex_result: 
                        data_dict['data']['version_number'] = int(version_number_regex_result[0])                    
                
                sg_data.append(data_dict)
        if len(sg_data) > 0:
            result = sg.batch(sg_data)

    return result

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data') or []
    sg_data = []
    result = []

    multi_entities = {
        'version_ids': {'type': 'Version', 'field': 'sg_versions'}
    }

    # ------------------------------------- #
    #   CACHE EPISODES BASED ON PROJECT     #
    # ------------------------------------- #
    for each in data:
        filters = each.get('filters')
        values = each.get('values')
        published_id = filters.get('id')
        sg_values = {}

        for key, value in values.items():
            if key in multi_entities.keys():
                sg_values[multi_entities[key]['field']] = [{'type': multi_entities[key]['type'], 'id': int(_id)} for _id in value]
            else:
                sg_values[SG_FIELD_MAPS[key]] = value

        if published_id:
            sg_data.append(
                {
                    'request_type': 'update',
                    'entity_type': 'PublishedFile',
                    'entity_id': published_id,
                    'data': sg_values,
                    'multi_entity_update_modes': {'sg_versions': 'add'}
                }
            ) 
        
    if len(sg_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_data)

    return result