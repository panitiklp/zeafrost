from . import sg_entity_utils, sg_asset, sg_shot, sg_task
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'entity': 'entity',
    'shot': 'sg_shot_link',
    'asset': 'sg_asset_link',
    'step': 'sg_step',
    'description': 'description',
    'duration': 'duration',
    'note': 'sg_note',
    'user': 'user'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = []
TIME_LOGGED_TYPE = {
    'normal': 'Normal',
    'ot': 'OT',
    'extra': 'Extra'
}

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    task_id = body.get('task_id')

    filters = []
    result = []

    task_result = sg_task.sg_entity_search(body)

    if len(task_result) > 0:
        task_id = task_result[0].get('id')

    if task_id:
        filters += [['entity', 'is', {'type': 'Task', 'id': task_id}]]

    if filters:
        sg = sg_con.connect()
        result = sg.find(
            'TimeLog',
            filters=filters,
            fields=list(SG_FIELD_MAPS.values())
        )

    if shotgrid:
        return result
    else:
        return sg_entity_utils.entity_response_adapter(
            data=result,
            sg_fields=SG_FIELD_MAPS_INVERT,
            str_fields=STR_FIELDS
        )

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    sg_data = []
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
                'id': int(project_result.get('id')),
                'code': project_result.get('code'),
            }

    if projects:
        for project_name, project_data in projects.items():
            sg_shot.entity_cache(project=project_name)
            sg_asset.entity_cache(project=project_name)

        for each_data in data:
            project = each_data.get('project')
            step = each_data.get('step')
            task = each_data.get('task')
            username = each_data.get('user')
            description = each_data.get('description')
            time_logged = each_data.get('time_logged')
            time_unit = each_data.get('time_unit') or 'hour'
            time_note = each_data.get('time_note') or 'Normal'

            entity_id = None
            step_id = None
            task_id = each_data.get('task_id')
            user_id = None

            sg_create_data = {
                'request_type': 'create',
                'entity_type': 'TimeLog',
                'data': {}
            }

            if project:
                sg_create_data['data']['project'] = {'type': 'Project', 'id': projects[project]['id']}

            if task_id:
                sg_create_data['data']['entity'] = {'type': 'Task', 'id': task_id}

            else:
                redis_pattern_dict = sg_entity_utils.entity_redis_pattern(each_data)
                redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())

                if len(redis_pattern_dict.get('redis_names')) > 0:
                    entity_id = int(redis_pattern_dict['redis_names'][0].split(':')[-1])

                    if redis_pattern_dict.get('entity_type') == 'Shot':
                        sg_create_data['data']['sg_shot_link'] = {'type': 'Shot', 'id': entity_id}

                    elif redis_pattern_dict.get('entity_type') == 'Asset':
                        sg_create_data['data']['sg_asset_link'] = {'type': 'Asset', 'id': entity_id}

                if len(redis_step_names) > 0:
                    step_id = int(redis_step_names[0].split(':')[-1])
                    sg_create_data['data']['sg_step'] = {'type': 'Step', 'id': step_id}

                if task:
                    if each_data.get('time_logged'):
                        del each_data['time_logged']
                    if each_data.get('user'):
                        del each_data['user']
                    if each_data.get('time_unit'):
                        del each_data['time_unit']
                    if each_data.get('time_note'):
                        del each_data['time_note']
                    if each_data.get('description'):
                        del each_data['description']

                    task_result = sg_task.sg_entity_search(each_data)
                    if len(task_result) > 0:
                        task_id = task_result[0].get('id')
                        sg_create_data['data']['entity'] = {'type': 'Task', 'id': task_id}

            if username:
                user_id = sg_entity_utils.sg_user_id(username)
                if user_id:
                    sg_create_data['data']['user'] = {'type': 'HumanUser', 'id': user_id}

            if time_logged:
                sg_create_data['data']['duration'] = time_logged if time_unit == 'minute' else (time_logged * 60)

            if time_note:
                sg_create_data['data']['sg_note'] = TIME_LOGGED_TYPE.get(time_note.lower()) or 'Normal'

            if description:
                sg_create_data['data']['description'] = description

            if sg_create_data:
                sg_data.append(sg_create_data)

    if len(sg_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_data)

    return result