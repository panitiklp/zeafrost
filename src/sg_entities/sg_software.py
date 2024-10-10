from . import sg_entity_utils
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'code': 'code',
    'description': 'description',
    'status': 'sg_status_list',
    'group': 'group_name',
    'group_default': 'group_default',
    'engine': 'engine',
    'is_utility': 'sg_utility',
    'windows_path': 'windows_path',
    'windows_args': 'windows_args',
    'linux_path': 'linux_path',
    'linux_args': 'linux_args',
    'mac_path': 'mac_path',
    'mac_args': 'mac_args',
    'products': 'products',
    'versions': 'version_names',
    'projects': 'project_sg_softwares_projects',
    'path_to_icon': 'sg_path_to_icon'
}
SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    result = sg_entity_utils.single_entity_cache(
        entity = 'Software', 
        fields = list(SG_FIELD_MAPS.values())
    )

    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    software = body.get('software')
    software_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'software',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    result = []

    redis_name = 'sg:software:'
    redis_name += f'{software}:' if software else '*:'
    redis_name += f'{software_id}' if software_id else '*'
    redis_names = redis_ctl.keys(redis_name.lower())

    result = sg_entity_utils.entity_cache_search(
        redis_name = redis_name,
        redis_names = redis_names,
        entity_cache = sg_entity_utils.single_entity_cache_callback(
            entity = 'Software', 
            fields = list(SG_FIELD_MAPS.values())
        )
    )

    if result:
        if shotgrid:
            return result
        else:
            return sg_entity_utils.entity_response_adapter(
                data = result, 
                sg_fields = SG_FIELD_MAPS_INVERT, 
                str_fields = STR_FIELDS
            )
    else:
        return []
