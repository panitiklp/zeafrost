from . import sg_entity_utils
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'code': 'code',
    'short_name': 'short_name',
    'description': 'description',
    'softwares': 'sg_softwares',
    'steps': 'sg_steps',
    'status': 'sg_status_list'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'short_name']

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    result = sg_entity_utils.single_entity_cache(
        entity='PublishedFileType', 
        fields=list(SG_FIELD_MAPS.values())
    )
    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    published_type = body.get('type')
    published_type_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'type',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    result = []

    redis_name = 'sg:publishedfiletype:'
    redis_name += f'{published_type}:' if published_type else '*:'
    redis_name += f'{published_type_id}' if published_type_id else '*'
    redis_names = redis_ctl.keys(redis_name.lower())

    result = sg_entity_utils.entity_cache_search(
        redis_name=redis_name,
        redis_names=redis_names,
        entity_cache=sg_entity_utils.single_entity_cache_callback(
            entity='PublishedFileType', 
            fields=list(SG_FIELD_MAPS.values())
        )
    )
    
    if shotgrid:
        return result
    else:
        return sg_entity_utils.entity_response_adapter(
            data=result, 
            sg_fields=SG_FIELD_MAPS_INVERT,
            str_fields=STR_FIELDS
        )
