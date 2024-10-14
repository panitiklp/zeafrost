from . import sg_entity_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

SG_FIELD_MAPS = {
    'id': 'id',
    'code': 'code',
    'project': 'project',
    'description': 'description',
    'status': 'sg_status',
    'steps': 'sg_steps',
    'departments': 'sg_departments',
    'rederers': 'sg_rederers',
    'software': 'sg_software',
    'environment': 'sg_environment',
    'windows_path': 'windows_path',
    'default_shot': 'sg_default_shot',
    'default_asset': 'sg_default_asset'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
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
            'PipelineConfiguration', 
            filters = [['project', 'name_contains', project]],
            fields = list(SG_FIELD_MAPS.values())
        )
        redis_pattern = f'sg:pipelineconfiguration:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        sg_project = elem.get('project')
        if sg_project:
            redis_name = 'sg:pipelineconfiguration:'
            redis_name += f'{sg_project.get("name")}:'
            redis_name += f'{elem.get("code")}:'
            redis_name += f'{elem.get("id")}'
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))
    
    if len(redis_ctl.keys(redis_pattern)) > 0:
        return True
    else:
        return False

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    software = body.get('software')
    software_version = body.get('version')
    description = body.get('description')
    config_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'project',
        'software',
        'version',
        'description',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    result = []

    redis_name = 'sg:pipelineconfiguration:'
    redis_name += f'*{project}:' if project else '*:'
    redis_name += f'*{software}' if software  else '*'
    redis_name += f'*{software_version}' if software_version else '*'
    redis_name += f'*{description}' if description else '*'
    redis_name += f'{config_id}' if config_id else '*'
    redis_names = redis_ctl.keys(redis_name.lower())

    if len(redis_names) > 0:
        for redis_name in sorted(redis_names):
            episode_data = redis_ctl.hgetall(redis_name)
            result.append(episode_data)
    else:
        entity_cache({'project': project})
        redis_names = redis_ctl.keys(redis_name.lower())

        if len(redis_names) > 0:
            for redis_name in sorted(redis_names):
                episode_data = redis_ctl.hgetall(redis_name)
                result.append(episode_data)

    return sg_entity_utils.search_response(
        data  = result, 
        shotgrid = shotgrid, 
        sg_fields = SG_FIELD_MAPS_INVERT, 
        str_fields = STR_FIELDS
    )
