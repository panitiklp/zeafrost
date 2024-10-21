from . import sg_entity_utils
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'department': 'code',
    'name': 'name',
    'order': 'sg_department_order',
    'steps': 'steps',
    'users': 'users'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    result = sg_entity_utils.single_entity_cache(
        entity='Department', 
        fields=list(SG_FIELD_MAPS.values())
    )
    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    department = body.get('department')
    department_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'department',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    result = []

    redis_name = 'sg:department:'
    redis_name += f'{department}:' if department else '*:'
    redis_name += f'{department_id}' if department_id else '*'
    redis_names = redis_ctl.keys(redis_name.lower())

    result = sg_entity_utils.entity_cache_search(
        redis_name=redis_name,
        redis_names=redis_names,
        entity_cache=sg_entity_utils.single_entity_cache_callback(
            entity='Department', 
            fields=list(SG_FIELD_MAPS.values())
        )
    )
    
    if result:
        if shotgrid:
            return result
        else:
            return sg_entity_utils.entity_response_adapter(
                data=result,
                sg_fields=SG_FIELD_MAPS_INVERT,
                str_fields=STR_FIELDS
            ) 
    else:
        return []
