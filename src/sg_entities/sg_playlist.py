from . import sg_entity_utils
from ..sg_controllers import sg_con

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'step': 'sg_step',
    'playlist': 'code',
    'versions': 'versions'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'name']

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    step = body.get('step')
    playlist = body.get('playlist')

    valid_keys = {
        'shotgrid',
        'project',
        'step',
        'playlist'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []

    sg_filters = []
    result = {}

    if project: sg_filters += [['project', 'name_contains', project]]
    if step: sg_filters += [['sg_step.Step.short_name', 'is', step]]
    if playlist: sg_filters += [['code', 'is', playlist]]

    sg = sg_con.connect()

    result = sg.find(
        entity_type='Playlist',
        filters=sg_filters,
        fields=list(SG_FIELD_MAPS.values())
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
        return result
