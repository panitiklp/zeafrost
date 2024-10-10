from . import sg_entity_utils
from ..sg_controllers import sg_con

SG_FIELD_MAPS = {
    'id': 'id',
    'code': 'code',
    'shot': 'shot',
    'asset_type': 'sg_asset_type',
    'asset': 'asset',
    'namespaces': 'sg_namepaces',
    'publish_subsciption': 'sg_publish_subsciption',
    'published_file_path': 'sg_publish_subsciption.PublishedFile.sg_file_path',
    'published_file_type': 'sg_publish_subsciption.PublishedFile.published_file_type',
    'upstream_published_files': 'sg_publish_subsciption.PublishedFile.upstream_published_files',
    'downstream_published_files': 'sg_publish_subsciption.PublishedFile.downstream_published_files'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code']

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    episode = body.get('episode')
    sequence = body.get('sequence')
    shot = body.get('shot')
    entity = body.get('entity')
    entity_id = body.get('id')

    sg_filters = []
    result = []

    # ---------------------- #
    #       ENTITY ID        #
    # ---------------------- #
    if entity_id:
        sg = sg_con.connect()
        
        if entity.lower() == 'shot':
            sg_filters += [['shot', 'is', {'type': 'Shot', 'id': entity_id}]]

        elif entity.lower() == 'asset':
            sg_filters += [['asset', 'is', {'type': 'Asset', 'id': entity_id}]]
        
        if sg_filters:
            result = sg.find(
                'AssetShotConnection',
                filters = sg_filters,
                fields = list(SG_FIELD_MAPS.values())
            )

        # ///// RESPONSE ADAPTER ///// #
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

    # ----------------------------- #
    #       IF NOT ENTITY ID        #
    # ----------------------------- #
    redis_pattern_dict = sg_entity_utils.entity_redis_pattern(body)
    sg = sg_con.connect()
    
    operator_filter = 'name_contains'
    if episode and sequence and shot:
        operator_filter = 'name_is'
    
    if redis_pattern_dict.get('redis_names'):
        if redis_pattern_dict.get('entity_type').lower() == 'shot':
            sg_filters += [['shot', operator_filter,   redis_pattern_dict.get('redis_names')[0].split(':')[-2]]]
        
        elif redis_pattern_dict.get('entity_type').lower() == 'asset':
            sg_filters += [['asset', operator_filter,  redis_pattern_dict.get('redis_names')[0].split(':')[-2]]]
        
        result = sg.find(
            'AssetShotConnection',
            filters = sg_filters,
            fields = list(SG_FIELD_MAPS.values())
        )
    
    # ///// RESPONSE ADAPTER ///// #
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


def sg_entity_update(body):
    data = body.get('data') or []
    result = {}

    for each in data:
        filters = each.get('filters')
        values = each.get('values')

        shot_id = filters.get('shot_id')
        asset_id = filters.get('asset_id')
        namespaces = values.get('namespaces') or ''
        
        asc_result = {}
        
        if shot_id and asset_id:
            sg = sg_con.connect()
            asc_result = sg.find_one(
                'AssetShotConnection',
                filters=[
                    ['asset', 'is', {'type': 'Asset', 'id': asset_id}],
                    ['shot', 'is', {'type': 'Shot', 'id': shot_id}]
                ]
            )

            if asc_result:
                result = sg.update(
                    'AssetShotConnection',
                    entity_id = asc_result['id'],
                    data = {
                        'sg_namepaces': str(namespaces)
                    }
                )
                

    return result