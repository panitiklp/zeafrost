from . import sg_entity_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'steps': 'sg_steps',
    'subject': 'subject',
    'tasks': 'tasks',
    'to': 'addressings_to',
    'cc': 'addressings_cc',
    'body': 'content',
    'author': 'user',
    'attachments': 'attachments',
    'client_approved': 'client_approved',
    'client_note': 'client_note',
    'type': 'sg_note_type',
    'status': 'sg_status_list',
    'read': 'read_by_current_user',
    'entity': 'note_links'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}
STR_FIELDS = ['code', 'name', 'sequence']

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid    = body.get('shotgrid') or False
    step        = body.get('step')
    task        = body.get('task')
    note_id     = body.get('id')
    step_id     = None

    valid_keys = {
        'shotgrid',
        'step',
        'task',
        'id',
        'project',
        'episode',
        'sequence',
        'shot',
        'type',
        'asset_type',
        'asset',
        'variation'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []
    
    sg_filters  = []
    result      = {}
    
    redis_pattern_dict = sg_entity_utils.entity_redis_pattern(body)

    if step:
        redis_step_names = redis_ctl.keys(f'sg:step:{step}:*'.lower())
        if len(redis_step_names) > 0:  step_id = int(redis_step_names[0].split(':')[-1])
    
    if step_id: sg_filters  += [['sg_steps', 'is', {'type': 'Step', 'id': step_id}]]
    if note_id: sg_filters  += [['id', 'is', int(note_id)]]
    if task:    sg_filters  += [['tasks', 'name_contains', task]]

    if redis_pattern_dict.get('entity_name'):
        sg_filters  += [['note_links', 'name_contains', redis_pattern_dict.get('entity_name')]]
    
    if sg_filters:
        sg = sg_con.connect()

        result = sg.find(
            'Note',
            filters = sg_filters,
            fields  = list(SG_FIELD_MAPS.values())
        )
    
    # ----------------------------- #
    #       RESPONSE ADAPTER        #
    # ----------------------------- #
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

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    pass
