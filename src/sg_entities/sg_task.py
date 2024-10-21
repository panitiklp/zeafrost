from collections import OrderedDict
from . import sg_asset, sg_shot, sg_entity_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils
from pprint import pprint

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'step_id': 'step.Step.id',
    'step_code': 'step.Step.code',
    'step_short_name': 'step.Step.short_name',
    'task':'content',
    'entity': 'entity',
    'episode': 'entity.Shot.sg_episode',
    # 'episode_id': 'entity.Shot.sg_episode.Episode.id',
    # 'episode_code': 'entity.Shot.sg_episode.Episode.code',
    # 'episode_shortname': 'entity.Shot.sg_episode.Episode.sg_short_name',
    'sequence': 'entity.Shot.sg_sequence',
    # 'sequence_id': 'entity.Shot.sg_sequence.Sequence.id',
    # 'sequence_code': 'entity.Shot.sg_sequence.Sequence.code',
    # 'sequence_shortname': 'entity.Shot.sg_sequence.Sequence.sg_short_name',
    'shot_id': 'entity.Shot.id',
    'shot_code': 'entity.Shot.code',
    'shot_shortname': 'entity.Shot.sg_short_name',
    'asset_id': 'entity.Asset.id',
    'asset_code': 'entity.Asset.code',
    'status': 'sg_status_list',
    'start_date': 'start_date',
    'due_date': 'due_date',
    'duration': 'duration',
    'note': 'open_notes',
    'task_priority': 'sg_step_id',
    'assignees': 'task_assignees',
    'reviewers': 'task_reviewers',
    'bid_hour': 'est_in_mins',
    'time_logged': 'time_logs_sum',
    'time_logged_over_under': 'time_vs_est',
    'time_logged_percentage_of_bid': 'time_percent_of_est'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'name', 'content', 'task']
SG_NESTED_FIELDS = ['task_assignees','task_reviewers']
NESTED_ENTITY_FOR_REDIS_FIELDS = {
    'step':{
        'step.step.id': 'step.Step.id',
        'step.step.code': 'step.Step.code',
        'step.step.short_name': 'step.Step.short_name'
    },
    'shot':{
        'entity.shot.id': 'entity.Shot.id',
        'entity.shot.code': 'entity.Shot.code',
        'entity.shot.sg_short_name': 'entity.Shot.sg_short_name'
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
            'Task', 
            filters = [['project', 'name_contains', project]],
            fields  = list(['content', 'step.Step.short_name', 'entity.Asset.code', 'entity.Shot.code']),
            order   = [{'field_name': 'code', 'direction':'asc'}]
        )
        redis_pattern = f'sg:task:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        redis_data = {}

        redis_name =  'sg:task:'
        redis_name += f'{project}:'
        
        if elem['entity.Asset.code']:
            redis_name += f'asset:{elem["entity.Asset.code"]}:'
        elif elem['entity.Shot.code']:
            redis_name += f'shot:{elem["entity.Shot.code"]}:'

        redis_name += f'{elem["step.Step.short_name"]}:'
        redis_name += f'{elem["content"]}:'
        redis_name += f'{elem.get("id")}'

        redis_data['project'] = project or ''
        redis_data['id'] = elem['id'] or ''
        redis_data['name'] = elem['content'] or ''
        redis_data['asset'] = elem['entity.Asset.code'] or ''
        redis_data['shot'] = elem['entity.Shot.code'] or ''
        redis_data['step'] = elem['step.Step.short_name'] or ''
        
        redis_ctl.hset(redis_name.lower(), redis_data)

    return True

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    episode = body.get('episode')
    sequence = body.get('sequence')
    shot = body.get('shot')
    asset_type = body.get('asset_type')
    asset = body.get('asset')
    variation = body.get('variation')
    step = body.get('step')
    task = body.get('task')
    entity_id = body.get('id')
    steps = body.get('steps')
    minimum_fields = body.get('minimum_fields')
    
    valid_keys = {
        'shotgrid',
        'project',
        'episode',
        'sequence',
        'shot',
        'asset_type',
        'asset',
        'variation',
        'step',
        'task',
        'entity_id',
        'steps',
        'minimum_fields',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    filters = []
    result  = []

    redis_pattern_dict = sg_entity_utils.entity_redis_pattern(body)
    if not redis_pattern_dict:
        return
    operator_filter = 'name_contains'

    if episode and sequence and shot:
        operator_filter = 'name_is'  
        if redis_pattern_dict.get('redis_names'):
            filters += [['entity', operator_filter, redis_pattern_dict.get('redis_names')[0].split(':')[-2]]]   
    
    elif episode and sequence:
        filters += [['entity', operator_filter, '{}_{}'.format(episode, sequence)]]   

    elif episode:
        filters += [['entity', operator_filter, str(episode)]]   

    if project: filters += [['project', 'name_contains', project]]
    if entity_id: filters += [['id', 'is', int(entity_id)]]
    if step: filters += [['step.Step.short_name', 'is', step]]
    if task: filters += [['content', 'is', str(task)]]
    if asset_type: filters += [['entity.Asset.sg_asset_type', 'is', asset_type]]
    if variation:
        if asset:
            filters += [['entity.Asset.code', 'is', f'{asset}_{variation}']]
    elif asset:
        filters += [['entity.Asset.code', 'is', asset]]
        
    if steps:
        step_filters = {
            'filter_operator': 'any',
            'filters': []
        }

        for _step in steps:
            step_filters['filters'] += [['step.Step.short_name', 'is', _step]]
        
        filters.append(step_filters)
    sg = sg_con.connect()

    if minimum_fields:
        result = sg.find(
            'Task', 
            filters = filters, 
            fields = [
                'id', 
                'content', 
                'step.Step.id',
                'step.Step.code',
                'step.Step.short_name',
                'entity.Shot.sg_episode',
                'entity.Shot.sg_sequence',
                'entity.Shot.sg_short_name',
                'entity.Shot.id',
                'entity.Shot.code',
                'entity.Asset.id',
                'entity.Asset.code',
                'task_reviewers',
                'task_assignees',
                'sg_status_list'
            ]
        )
    else:
        result = sg.find(
            'Task', 
            filters = filters, 
            fields = list(SG_FIELD_MAPS.values())
        )
    
    if shotgrid:
        return result

    else:
        if minimum_fields:
            parsed_result = []
            
            for result_data in result:
                data_dict = OrderedDict()
                data_dict['asset'] = OrderedDict()
                data_dict['shot'] = OrderedDict()
                data_dict['step'] = OrderedDict()

                for key, val in result_data.items():
                    # /////// EPISODE /////// #
                    if 'sg_episode' in key.lower():
                        data_dict['episode'] = val

                    # /////// SEQUENCE /////// #
                    elif 'sg_sequence' in key.lower():
                        data_dict['sequence'] = val

                    # /////// SHOT /////// #
                    elif 'shot.id' in key.lower():
                        data_dict['shot']['id'] = val

                    elif 'shot.code' in key.lower():
                        data_dict['shot']['name'] = val

                    elif 'shot.sg_short_name' in key.lower():
                        data_dict['shot']['short_name'] = val
                        data_dict['shot']['type'] = 'Shot'
                    
                    # /////// ASSET /////// #
                    elif 'asset.id' in key.lower():
                        data_dict['asset']['id'] = val
                    
                    elif 'asset.code' in key.lower():
                        data_dict['asset']['name'] = val
                        data_dict['asset']['type'] = 'Asset'
                    
                    # /////// STEP /////// #
                    elif 'step.id' in key.lower():
                        data_dict['step']['id'] = val
                    
                    elif 'step.code' in key.lower():
                        data_dict['step']['name'] = val
                    
                    elif 'step.short_name' in key.lower():
                        data_dict['step']['short_name'] = val
                        data_dict['step']['type'] = 'Step'

                    else:
                        if SG_FIELD_MAPS_INVERT.get(key):
                            data_dict[SG_FIELD_MAPS_INVERT[key]] = val
                parsed_result.append(data_dict)

            return parsed_result

        else:
            parsed_result = []
            for each_data in result:
                parsed_data = OrderedDict()
                parsed_data['episode'] = OrderedDict()
                parsed_data['sequence'] = OrderedDict()
                parsed_data['shot'] = OrderedDict()
                parsed_data['asset'] = OrderedDict()
                parsed_data['step'] = OrderedDict()

                for key, val in each_data.items():
                    if SG_FIELD_MAPS_INVERT.get(key):
                        # /////// SHOT /////// #
                        if 'entity.shot.id' == key.lower():
                            parsed_data['shot']['id'] = int(val) if val else None

                        elif 'entity.shot.code' == key.lower():
                            parsed_data['shot']['name'] = str(val) if val else None

                        elif 'entity.shot.sg_short_name' == key.lower():
                            parsed_data['shot']['short_name'] = str(val) if val else None
                            parsed_data['shot']['type'] = 'Shot'

                        # /////// ASSET /////// #
                        elif 'entity.asset.id' == key.lower():
                            parsed_data['asset']['id'] = int(val) if val else None

                        elif 'entity.asset.code' == key.lower():
                            parsed_data['asset']['name'] = str(val) if val else None
                            parsed_data['asset']['type'] = 'Asset'

                        # /////// STEP /////// #
                        elif 'step.step.id' == key.lower():
                            parsed_data['step']['id'] = int(val) if val else None

                        elif 'step.step.code' == key.lower():
                            parsed_data['step']['name'] = str(val) if val else None

                        elif 'step.step.short_name' == key.lower():
                            parsed_data['step']['short_name'] = str(val) if val else None
                            parsed_data['step']['type'] = 'Step'

                        else:
                            parsed_data[SG_FIELD_MAPS_INVERT[key]] = val
                
                parsed_result.append(parsed_data)
            return parsed_result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search_basic(body):
    project = body.get('project')
    task_id = body.get('id')
    entity = body.get('entity')
    
    result = []

    redis_name =  'sg:task:'
    redis_name += f'*{project}:' if project else '*:'
    redis_name += str(entity) if entity else '*'
    redis_name += str(task_id) if task_id else '*'

    redis_names = redis_ctl.keys(redis_name.lower())
    if redis_names:
        for redis_name in sorted(redis_names):
            res_data = {}
            resdis_name_split = redis_name.split(':')
            res_data['project'] = resdis_name_split[2].upper()
            res_data['entity_type'] = resdis_name_split[3]
            res_data['entity_name'] = resdis_name_split[4]
            res_data['step'] = resdis_name_split[5]
            res_data['task'] = resdis_name_split[6]
            res_data['task_id'] = int(resdis_name_split[7]) if resdis_name_split[7] else None
            result.append(res_data)
        
    
    return result

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data    = body.get('data')
    result  = []

    projects = sg_entity_utils.multi_project_union(data)

    for project_name, project_data in projects.items():
        sg_shot.entity_cache(project=project_name)
        sg_asset.entity_cache(project=project_name)
    
    sg = sg_con.connect()
    sg_data = []

    for each_data in data:
        project = each_data.get('project')
        step = each_data.get('step')
        task = each_data.get('task')
        project_id = projects[project]['id'] if projects.get(project) else None

        redis_pattern_dict = sg_entity_utils.entity_redis_pattern(each_data)
        redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())
        
        entity_type = redis_pattern_dict.get('entity_type')
        entity_id = int(redis_pattern_dict['redis_names'][0].split(':')[-1]) if len(redis_pattern_dict['redis_names']) > 0 else None
        step_id = int(redis_step_names[0].split(':')[-1]) if len(redis_step_names) > 0 else None
        
        if entity_id and step_id:
            data_dict = {
                'request_type': 'create',
                'entity_type': 'Task',
                'data': {
                    'project': {'type': 'Project', 'id': project_id},
                    'entity': {'type': entity_type, 'id': entity_id},
                    'step': {'type': 'Step', 'id': step_id},
                    'content': task,
                    'sg_status_list': 'wtg'
                }
            }

            sg_task_find_result = sg.find_one(
                'Task',
                filters = [
                    ['project', 'name_contains', project],
                    ['entity',  'name_contains', redis_pattern_dict['entity_name']],
                    ['step.Step.short_name', 'is', step],
                    ['content', 'is', task]
                ]
            )

            if not sg_task_find_result:
                sg_data.append(data_dict)

    if len(sg_data) > 0:
        result = sg.batch(sg_data)
            
    return result

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data') or []
    result = []

    # ------------------------------------- #
    #   CACHE EPISODES BASED ON PROJECT     #
    # ------------------------------------- #
    projects = {}
    for each in data:
        filters = each.get('filters')

        project = filters.get('project') 
        redis_project_names = redis_ctl.keys(f'sg:project:{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])
            
            projects[filters.get('project')] = {
                'id': int(project_result.get('id')),
                'code': project_result.get('code'),
            }
        
    if projects:
        sg = sg_con.connect()
        sg_data = []

        for each_data in data:
            filters = each_data.get('filters')
            values = each_data.get('values')

            project = filters.get('project')
            step = filters.get('step')
            task = filters.get('task')
            project_id = projects[project]['id'] if projects.get(project) else None

            redis_pattern_dict = sg_entity_utils.entity_redis_pattern(filters)
            redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())

            sg_filters = []
            sg_task_find_result = {}

            if project_id:
                sg_filters += [['project', 'is', {'type': 'Project', 'id': project_id}]]

            if len(redis_pattern_dict['redis_names']) > 0:
                sg_filters += [['entity', 'is', {'type': redis_pattern_dict['entity_type'], 'id': int(redis_pattern_dict['redis_names'][0].split(':')[-1])}]]
            
            if len(redis_step_names) > 0:
                sg_filters += [['step', 'is', {'type': 'Step', 'id': int(redis_step_names[0].split(':')[-1])}]]
            
            if task:
                sg_filters += [['content', 'is', task]]

            if sg_filters:
                sg_task_find_result = sg.find_one('Task', filters=sg_filters)

            # --------------------- #
            #       TASK VALUES     #
            # --------------------- #
            if sg_task_find_result and values:
                sg_values = {}
                multi_entity_update_mode = {}

                for key, value in values.items():
                    if key != 'update_mode':
                        # ------------------------- #
                        #       SINGLE FIELD        #
                        # ------------------------- #
                        if not SG_FIELD_MAPS[key] in SG_NESTED_FIELDS:
                            sg_values[SG_FIELD_MAPS[key]] = value

                        # ------------------------- #
                        #       TASK ASSIGNEES      #
                        # ------------------------- #
                        else:
                            if SG_FIELD_MAPS[key] == 'task_assignees':
                                sg_values['task_assignees'] = []
                                multi_entity_update_mode['task_assignees'] = value.get('update_mode') or 'set'

                                for user in value.get('users'):
                                    redis_user_names = redis_ctl.keys(f'sg:user:{user}:*')

                                    if len(redis_user_names) > 0:
                                        user_id = int(redis_user_names[0].split(':')[-1])
                                        sg_values['task_assignees'].append({'type': 'HumanUser', 'id': user_id})
                            
                            # ------------------------- #
                            #       TASK REVIEWERS      #
                            # ------------------------- #
                            elif SG_FIELD_MAPS[key] == 'task_reviewers':
                                sg_values['task_reviewers'] = []
                                multi_entity_update_mode['task_reviewers'] = value.get('update_mode') or 'set'
                                
                                for user in value.get('users'):
                                    redis_user_names = redis_ctl.keys(f'sg:user:{user}:*')

                                    if len(redis_user_names) > 0:
                                        user_id = int(redis_user_names[0].split(':')[-1])
                                        sg_values['task_reviewers'].append({'type': 'HumanUser', 'id': user_id})
                sg_data_tmp = {
                    'request_type': 'update',
                    'entity_type': 'Task',
                    'entity_id': sg_task_find_result.get('id'),
                    'data': sg_values
                }

                if multi_entity_update_mode:
                    sg_data_tmp['multi_entity_update_modes'] = multi_entity_update_mode

                sg_data.append(sg_data_tmp)
            
        # --------------------- #
        #       TASK UPDATE     #
        # --------------------- #
        if len(sg_data) > 0:
            result = sg.batch(sg_data)
    
    return result

# ======================================== #
#       SHOTGRID TASK SEARCH BY USER       #
# ======================================== #
def sg_search_by_user(body):
    user    = body.get("user")
    project = body.get("project")
    status  = body.get("status")
    shotgrid = body.get('shotgrid') or False
    result  = []
    
    redis_user_names = redis_ctl.keys(f'sg:user:{user}:*'.lower())

    if len(redis_user_names) > 0:
        sg_filters = [['task_assignees', 'is', {'type': 'HumanUser', 'id': int(redis_user_names[0].split(':')[-1])}]]

        if project:
            redis_project_pattern   = f'sg:project:*{project}:*'.lower()
            redis_project_names     = redis_ctl.keys(redis_project_pattern)

            if len(redis_project_names) > 0:
                sg_filters += [['project', 'is', {'type': 'Project', 'id': int(redis_project_names[0].split(':')[-1])}]]

        if status:
            sg_filters += [['sg_status_list', 'is', status]]

        sg = sg_con.connect()
        sg_result = sg.find(
            'Task',
            filters = sg_filters,
            fields  = list(SG_FIELD_MAPS.values())
        )

        result = [data for data in sg_result if redis_ctl.keys(f'sg:project:*:{data["project"].get("id")}'.lower())]

    if result:
        if shotgrid:
            return result
        else:
            return sg_entity_utils.entity_response_adapter(
                data        = result,
                sg_fields   = SG_FIELD_MAPS_INVERT,
                str_fields  = STR_FIELDS
            )
    else:
        return []
