from collections import OrderedDict
from . import sg_entity_utils
from . import step_downstream
from . import sg_task
from .. import rocketchat
from .. import intercon
from ..redis_controllers import redis_ctl
from ..sg_controllers import sg_con

from pprint import pprint
import copy
import requests

SG_FIELD_MAPS = {
    'id': 'id',
    'name': 'name',
    'firstname': 'firstname',
    'first_name': 'sg_first_name',
    'last_name': 'sg_last_name',
    'lastname': 'lastname',
    'groups': 'groups',
    'division': 'sg_division',
    'department_id': 'department.Department.id',
    'department': 'department.Department.code',
    'department_name': 'department.Department.name',
    'position': 'sg_position',
    'status': 'sg_status_list',
    # 'employee_id': 'sg_employee_id',
    'employee_status': 'sg_emp_status',
    'login': 'login',
    # 'domain_name': 'sg_domain_login',
    'email': 'email',
    'phone': 'sg_telephone',
    'projects': 'projects',
    'availibility': 'sg_availibility',
    'permission_rule': 'permission_rule_set',
    'projects': 'projects',
    'users': 'users',
    'task': 'task'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}

DIVISION_MAP = { 1 : 'vfx', 2 : 'anm', 4 : 'game'}
DEPARTMENT_MAP = {
    1: '---',
    2: 'anm',
    3: 'art',
    4: 'pip',
    5: 'prod',
    6: 'lay',
    7: 'lgt',
    8: 'cmp',
    9: 'td',
    10: 'rig',
    11: 'cfx',
    12: 'ast',
    13: '3dgn',
    14: 'dyn',
    15: 'game',
    16: 'vfx',
    17: '',
    18: '',
    19: '',
    20: 'dir',
    21: 'fx',
    22: 'roto',
    23: 'onl',
    24: 'tex',
    25: '',
    26: '',
    27: '',
    28: 'mod',
    29: 'vfx1',
    30: 'vfx2',
    31: 'vfx3',
    32: 'dev',
    33: '',
    34: 'ta',
    35: 'gdev',
    36: 'gdes',
    37: 'mkt',
    38: 'ui',
    39: 'cs',
    40: 'qa' 
}

# ========================= #
#       ENTITY CACHE        #
# ========================= #
def entity_cache(*args, **kwargs):
    result = sg_entity_utils.single_entity_cache(
        entity  = 'User', 
        fields  = list(SG_FIELD_MAPS.values())
    )
    # rocketchat.rocketchat_user_room_cache()
    
    return result

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid    = body.get('shotgrid') or False
    username    = body.get('username')
    user_id     = body.get('id')
    downstream = body.get('downstream') or False

    result = []

    if downstream:
        result = get_user_downstream(payload=body)

    else:
        valid_keys = {
            'shotgrid',
            'username',
            'id'
        }

        if not set(body.keys()).issubset(valid_keys):
            return []

        redis_name  =  'sg:user:'
        redis_name  += f'{username}:'   if username     else '*:'
        redis_name  += f'{user_id}'     if user_id      else '*'
        redis_names = redis_ctl.keys(redis_name.lower())

        result = sg_entity_utils.entity_cache_search(
            redis_name   = redis_name.lower(),
            redis_names  = redis_names,
            entity_cache = sg_entity_utils.single_entity_cache_callback(
                entity   = 'User', 
                fields   = list(SG_FIELD_MAPS.values())
            )
        )

    if result:
        if shotgrid:
            return result
        else:
            return response_adapter(result) 
    else:
        return []

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data    = body.get('data')
    shotgrid = body.get('shotgrid') or False
    result  = []

    sg = sg_con.connect()
    sg_data = []

    for each_data in data:

        data_sg_key = {}

        for key in each_data.keys():

            if key in SG_FIELD_MAPS.keys():

                if key == 'groups':

                    if each_data['groups'] == 'ygg':
                        data_sg_key['groups'] = [{'id': 146, 'name': 'YGG', 'type': 'Group'}]

                    elif each_data['groups'] == 'freelance':
                         data_sg_key['groups'] = [{'id': 147, 'name': 'freelance', 'type': 'Group'}]

                elif key == 'department':

                    sg_department_find_result = sg.find_one(
                        'Department',
                        filters = [
                            ['code', 'is', each_data['department']]],
                        fields=['name'])

                    if sg_department_find_result:
                        data_sg_key['department'] = {
                            'id':sg_department_find_result['id'], 
                            'name':sg_department_find_result['name'],
                            'type': 'Department'}

                elif key == 'division':

                    if each_data['division'] == 1 or each_data['division'] == 'vfx':
                        data_sg_key['sg_division'] = 'VFX'

                    elif each_data['division'] == 2 or each_data['division'] == 'anm' or each_data['division'] == 'animation':
                        data_sg_key['sg_division'] = 'Animation'

                    elif each_data['division'] == 4 or 'game' in each_data['division']:
                        data_sg_key['sg_division'] = 'Game'

                else:
                    data_sg_key[SG_FIELD_MAPS[key]] = each_data[key]

        if data_sg_key:

            if not 'sg_status_list' in data_sg_key.keys():
                data_sg_key['sg_status_list'] = 'dis'

            data_dict = {
                'request_type': 'create',
                'entity_type': 'HumanUser',
                'data': data_sg_key
            }

            sg_user_find_result = sg.find_one(
                'HumanUser',
                filters = [
                    ['sg_domain_login', 'is', data_sg_key['sg_domain_login']]],
                fields = list(SG_FIELD_MAPS_INVERT.keys()))

            if not sg_user_find_result:
                sg_data.append(data_dict)


        # Create User Deadline
        #---------------------
        if each_data.get('deadline'):

            deadline_payload = {'username':'', 'groups': ''}
            result_deadline = create_user_deadline(deadline_payload)


    if sg_data:
        result = sg.batch(sg_data)

    if shotgrid:
        return result
    else:
        return response_adapter(result)

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):

    data = body.get('data') or []
    result = []

    sg = sg_con.connect()
    sg_data = []

    ignore_update = ['first_name', 'firstname', 'last_name', 'lastname', 'email']

    for each in data:
        filters = each.get('filters')
        values = each.get('values')

        check_ignore = set(ignore_update).intersection(values)

        if check_ignore:
            for key in check_ignore:
                del values[key]

        if filters and values:
            user = each['filters'].get('domain_name') or each['filters'].get('username')

            redis_user_names = redis_ctl.keys(f'sg:user:{user}:*'.lower())

            if len(redis_user_names) > 0:
                user_result = redis_ctl.hgetall(redis_user_names[0])
                entity_id = user_result.get('id')
                data_sg_key = {}

                for key in values.keys():

                    if key in SG_FIELD_MAPS.keys():

                        if key == 'groups':

                            if values['groups'] == 'ygg':
                                data_sg_key['groups'] = [{'id': 146, 'name': 'YGG', 'type': 'Group'}]

                            elif values['freelance'] == 'ygg':
                                data_sg_key['groups'] = [{'id': 147, 'name': 'freelance', 'type': 'Group'}]

                        elif key == 'department':

                            sg_department_find_result = sg.find_one(
                                'Department',
                                filters = [
                                    ['code', 'is', values['department']]],
                                fields=['name'])

                            if sg_department_find_result:
                                data_sg_key['department'] = {
                                    'id':sg_department_find_result['id'], 
                                    'name':sg_department_find_result['name'],
                                    'type': 'Department'}

                        elif key == 'division':

                            if values['division'] == 1 or values['division'] == 'vfx':
                                data_sg_key['sg_division'] = 'VFX'

                            elif values['division'] == 2 or values['division'] == 'anm' or values['division'] == 'animation':
                                data_sg_key['sg_division'] = 'Animation'

                            elif values['division'] == 4 or 'game' in values['division']:
                                data_sg_key['sg_division'] = 'Game'

                        else:
                            data_sg_key[SG_FIELD_MAPS[key]] = values[key]

                if data_sg_key:

                    data_dict = {
                        'request_type': 'update',
                        'entity_type': 'HumanUser',
                        'entity_id': int(entity_id),
                        'data': data_sg_key }

                    sg_data.append(data_dict)
        else:
            if check_ignore:
                result = {
                    'code': 400,
                    'message': 'USER_ERROR: [USER], Have key can not update // {}'.format(check_ignore),
                    'data': [] }

                return result

    if sg_data:
        # pprint(sg_data)
        result = sg.batch(sg_data)

    if result:
        return response_adapter(result)
    else:
        return result


# ================================== #
#         SHOTGRID USER SYNC         #
# ================================== #
def user_sync(body):

    result = {'code':200, 'message': '', 'result':[]}
    
    itc = intercon.Intercon()
    itcUsers = itc.user()

    sg_users = sg_entity_search(body)

    payloads_create = []
    payloads_update = []
    
    for itcUser in itcUsers:

        if itcUser.get('domain_login') and not itcUser.get('domain_login') == 'sysadmin':

            if itcUser.get('div_id') in [1, 2, 4]:   # ['VFX', 'ANIM', 'GAME']
                sg_id = ''
                user_data = {}

                for sg_user in sg_users:
                    if itcUser.get('domain_login') == sg_user.get('domain_name'):
                        sg_id = sg_user.get('id')
                        user_data = sg_user

                if itcUser.get('status') == 1 or itcUser.get('status') == 8:

                    if sg_id:
                        
                        value = {}
                        payload_update = {
                            'filters': {'domain_name': itcUser.get('domain_login')},
                            'values': {}
                        }

                        if  itcUser.get('domain_login') == 'thaksaporn':
                            
                            # parse map number division
                            #--------------------------
                            div_id = 0

                            if user_data.get('division') == 'Animation':
                                div_id = 2
                            elif 'VFX' in user_data.get('division'):
                                div_id = 1
                            elif 'Game' in user_data.get('division'):
                                div_id = 4

                            if div_id:
                                if not itcUser.get('div_id') == div_id:
                                    value['division'] = itcUser.get('div_id')

                            # Employee ID
                            #------------
                            if itcUser.get('empid'):
                                if not int(itcUser.get('empid')) == user_data.get('employee_id'):
                                    value['employee_id'] = itcUser.get('empid')

                            # Nickname
                            #---------
                            if not itcUser.get('nickname_en') == user_data.get('name'):
                                value['name'] = itcUser.get('nickname_en') 

                            if value:
                                payload_update['values'] = value
                                payloads_update.append(payload_update)

                    else:
                        
                        division_txt = DIVISION_MAP[itcUser.get('div_id')] or ''
                        login = '{}.{}'.format(division_txt , itcUser.get('domain_login'))

                        payload_user = {
                            'division': itcUser.get('div_id'),                          # 1 , 2 , 4
                            'groups':'ygg',                                             # ygg , freelance
                            'employee_id': itcUser.get('empid'),                        # 20055
                            'name': itcUser.get('nickname_en'),                         # Phone
                            'first_name': itcUser.get('fname_en'),                      # Thaksaporn
                            'firstname': itcUser.get('fname_en'),                       # Thaksaporn
                            'last_name': itcUser.get('sname_en'),                       # Petchrich
                            'lastname': itcUser.get('sname_en'),                        # Petchrich
                            'login': login,                                             # anm.thaksaporn
                            'domain_name': itcUser.get('domain_login'),                 # thaksaporn
                            'department': DEPARTMENT_MAP[itcUser.get('dept_id')],       # pip            
                            'status': 'dis'                                             # Always False
                        }

                        payloads_create.append(payload_user)

    if payloads_create:
        # pprint(payloads_create)
        res = sg_entity_create({'data': payloads_create})
        if type(res) == type([1,2,3]):
            result['data'] = res

    if payloads_update: 
        # pprint(payloads_update)
        result = sg_entity_update({'data': payloads_update})

    entity_cache({})
    return result


# ============================ #
#       RESPONSE ADAPTER       #
# ============================ #
def response_adapter(data):
    result = []

    for each_data in data:
        each_result = user_data_map(each_data)
        result.append(each_result)
    
    return result

# ========================= #
#       USER DATA MAP       #
# ========================= #
def user_data_map(data):
    result = {}
    
    for key, value in data.items():
        if key.startswith('department'):
            try:
                result['department'] = OrderedDict()
                result['department']['type'] = 'Department'
                result['department']['id'] = data.get('department.department.id') or data['department'].get('id')
                result['department']['name'] = data.get('department.department.name') or data['department'].get('name')

                if data['department'].get('code'):
                    result['department']['code'] = data.get('department.department.code')
            except: pass

        if SG_FIELD_MAPS_INVERT.get(key):
            if key == 'sg_domain_login':
                result[SG_FIELD_MAPS_INVERT.get(key)] = value.lower()
                rocketchat_data = redis_ctl.hgetall(f'rocketchat:user:{value}'.lower())
                result['rocketchat_id'] = rocketchat_data.get('id')
            
            else:
                result[SG_FIELD_MAPS_INVERT.get(key)] = value

    return result


# ========================= #
#         UTILLITY          #
# ========================= #
def get_user_downstream(payload):
    
    step = payload.get('step') or ''
    downstream_datas = []

    if step:

        # get step downstream
        #--------------------
        downstream_data = step_downstream.step_downstream
        payload_task = copy.deepcopy(payload)

        # search task in step
        #--------------------
        downstreams = downstream_data['step'][step]['downstream']
        key_payload = list(payload_task.keys())

        if 'id' in key_payload:
            del payload_task['id']

        if 'downstream' in key_payload:
            del payload_task['downstream']

        if 'username' in key_payload:
            del payload_task['username']

        if 'step' in key_payload:
            del payload_task['step']

        payload_task['steps'] = downstreams
        data_tasks = sg_task.sg_entity_search(payload_task)

        for data_task in data_tasks:

            data_task = dict(data_task)
            assignees = []

            data = {
                'task': {
                    'id': data_task['id'],
                    'name':data_task['task'],
                    'status': data_task['status'],
                    'step': dict(data_task['step'])},
                'users': []}

            # process data user [username]
            #------------------
            for assignee in data_task['assignees']:

                payload_user = {'id': assignee['id']}
                result_user = sg_entity_search(payload_user)

                if result_user:
                    result_user = dict(result_user[0])

                    data_user = {
                        'id': result_user['id'],
                        'username': result_user['domain_name'],
                        'rocketchat_id': result_user['rocketchat_id'],
                        'department': result_user['department'],
                        'name': result_user['name']}

                    assignees.append(data_user)

            data['users'] = assignees
            downstream_datas.append(data)

    return downstream_datas

def create_user_deadline(payload):
    deadline = False

    # Check exist User Deadline
    #--------------------------
    urlSearch = 'http://192.168.120.50/harvest/api/v1/user/search'
    urlInsert = 'http://192.168.120.50/harvest/api/v1/user/insert'
    urlUpdate = 'http://192.168.120.50/harvest/api/v1/user/update'

    headers = {'Content-Type': "application/json", 'Accept': "application/json", "Origin":"isopod"}

    dlCheckPayload = {"username" : payload['username']}
    resultdlCheck = requests.post(urlSearch, json = dlCheckPayload, headers=headers) 
    resultData = resultdlCheck.json()

    # Create New User
    #----------------
    if not resultData.get('data').get('StatusUser'):
        dlPayload = dlCheckPayload
        if payload.get('machine'):
            dlPayload['machine'] = payload.get('machine')

        resultCreate = requests.post(urlInsert, json = dlPayload, headers=headers)

        # Update Group User
        #------------------
        if resultCreate.json().get('data').get('StatusUser'):
            dlUpdatePayload = {'username': payload['username']}
            group = payload.get('payload') or ''

            if group:
                dlUpdatePayload['group'] = group
                resultUpdate = requests.post(urlUpdate, json = dlUpdatePayload, headers=headers)
                if resultUpdate.json().get('data').get('StatusUser'):
                    deadline = True

    return deadline