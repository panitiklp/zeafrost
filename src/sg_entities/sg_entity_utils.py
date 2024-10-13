from ast import literal_eval
from collections import OrderedDict
from pprint import pprint
import re

from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

DRIVE_MAP = {
    't': 'hq-data',
    'p': 'hq-data/Guest_Drive/P',
    'y': 'hq-data/Guest_Drive/y',
    'z': 'hq-data/Guest_Drive/z'
}

def get_drive_letter(path):
    """
    Extracts the drive letter from a given path.

    Args:
        path (str): The path from which to extract the drive letter.

    Returns:
        str: The extracted drive letter in lowercase, or None if no drive letter is found.
    """
    result = re.findall(r'(^[A-Za-z]):/', path.replace('\\', '/'))
    if result:
        return result[0].lower()

import re

def convert_path_windows_to_linux(path):
    """
    Converts a Windows path to a Linux path.

    Args:
        path (str): The Windows path to be converted.

    Returns:
        str: The converted Linux path.

    Example:
        >>> convert_path_windows_to_linux('C:\\workspace\\zeafrost\\src\\sg_entities')
        '/mnt/c/workspace/zeafrost/src/sg_entities'
    """
    drive_letter = get_drive_letter(path)
    
    if drive_letter and DRIVE_MAP.get(drive_letter):
        path = re.sub(f'{drive_letter}:/', f'/mnt/{DRIVE_MAP[drive_letter]}/', path.replace('\\', '/'), flags=re.IGNORECASE)
        return path
    
# ============================================== #
#       CHECK DATA TYPE (STRUCT) FROM DATA       #
# ============================================== #
def eval_type_check(data={}):
    """
    Check the type of the given data using the eval function.

    Args:
        data (dict, list, tuple, int): The data to be evaluated.

    Returns:
        bool: True if the data is of type dict, list, tuple, or int. False otherwise.
    """
    result = False

    if isinstance(eval(data), dict):
        result = True

    elif isinstance(eval(data), list):
        result = True 

    elif isinstance(eval(data), tuple):
        result = True 

    elif isinstance(eval(data), int):
        result = True

    else:
        result = False
    
    return result
    
# ============================================ #
#       SHOTGRID ENTITY CACHE AND SEARCH       #
# ============================================ #
def entity_cache_search(redis_name='', redis_names=[], entity_cache=None, **kwargs):
    project_id = kwargs.get('project_id')
    step_id = kwargs.get('step_id')
    result = []

    # -------------------------------------------------------------- #
    #       IF NAME IS NOT EXISTS IN REDIS, THEN CACHE - PLURAL      #
    # -------------------------------------------------------------- #
    if not redis_names:
        redis_names = entity_cache(
            project_id = project_id,
            step_id = step_id
        )

    # ---------------------------------------------------------------- #
    #       IF NAME IS NOT EXISTS IN REDIS, THEN CACHE - SINGULAR      #
    # ---------------------------------------------------------------- #
    if redis_ctl.keys(redis_name):
        redis_names = redis_ctl.keys(redis_name)

    else:
        entity_cache(
            project_id = project_id,
            step_id = step_id
        )

        redis_names = redis_ctl.keys(redis_name)

    # ----------------------------- #
    #       GET DATA FROM REDIS     #
    # ----------------------------- #
    for name in redis_names:
        redis_result = redis_ctl.hgetall(name)

        for key, val in redis_result.items():
            try:
                redis_result[key] = literal_eval(val) if eval_type_check(val) else val
            except Exception as e:
                pass

        result.append(redis_result)

    return result

# ============================================================= #
#       SHOTGRID SINGULAR ENTITIY CACHE CALLBACK FUNCTION       #
# ============================================================= #
def single_entity_cache_callback(entity='', fields=[], *args, **kwargs):
    """
    Returns a callback function that retrieves data from a single entity cache.

    Args:
        entity (str): The entity name.
        fields (list): The list of fields to retrieve from the cache.

    Returns:
        function: A callback function that retrieves data from the cache.

    """
    def callback(*args, **kwargs):
        redis_names = single_entity_cache(
            entity = entity, 
            fields = fields
        )
        
        return redis_names
    
    return callback

# =========================================== #
#       SHOTGRID SINGULAR ENTITIY CACHE       #
# =========================================== #
def single_entity_cache(entity='', fields=[]):
    """
    Caches the entities retrieved from Shotgun API into Redis.

    Args:
        entity (str): The entity type to cache. Possible values are 'step', 'user', 'status', 'software', 'department', 'publishedfiletype'.
        fields (list): The list of fields to retrieve from Shotgun API.

    Returns:
        bool: True if the caching is successful.

    """
    code_maps = {
        'step': 'short_name',
        'user': 'login',
        'status': 'code',
        'software': 'code',
        'department': 'code',
        'publishedfiletype': 'code'
    }
    
    # -------------------------------- #
    #      SHOTGRID CONNECTION         #
    # -------------------------------- #
    sg = sg_con.connect()
    sg_result = sg.find(
        'HumanUser' if entity.lower() == 'user' else entity, 
        filters = [], 
        fields  = fields
    )
    # ----------------------------- #
    #       DELETE REDIS DATA       #
    # ----------------------------- #
    redis_pattern = f'sg:{entity}:*'.lower()
    redis_ctl.delete(redis_pattern)

    # ----------------------------- #
    #       CACHE REDIS DATA        #
    # ----------------------------- #
    for elem in sg_result:
        code = code_maps.get(entity.lower())

        if elem.get(code):
            redis_name = f'sg:{entity}:'
            redis_name += f'{elem.get(code)}:'
            redis_name += f'{elem.get("id")}'
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))
    
    return True
    
# ================================== #
#       REDIS GET PROJECT DATA       #
# ================================== #
def redis_get_project_data(project='*', project_id='*'):
    """
    Retrieve project data from Redis based on the provided project and project_id.

    Args:
        project (str, optional): The project name. Defaults to '*'.
        project_id (str, optional): The project ID. Defaults to '*'.

    Returns:
        dict: A dictionary containing the project data retrieved from Redis.
    """
    redis_proj_data = {}
    redis_proj_name = 'sg:project:'
    redis_proj_name += f'*{project}:' if project else '*:'
    redis_proj_name += f'{project_id}' if project_id else '*'
    redis_proj_names = redis_ctl.keys(redis_proj_name.lower())
    
    if redis_proj_names and len(redis_proj_names) > 0:
        redis_proj_data = redis_ctl.hgetall(redis_proj_names[0])
    
    return redis_proj_data

def multi_project_union(data):
    """
    Retrieves project information from Redis based on the given data.

    Args:
        data (list): A list of dictionaries containing project information.

    Returns:
        dict: A dictionary containing project details, where the project name is the key and the project details are the value.
            Each project detail is represented as a dictionary with the following keys:
                - 'id': The project ID (integer).
                - 'code': The project code (string).
                - 'path': The project path (string).
    """
    projects = {}

    for each_data in data:
        project = each_data.get('project')
        redis_project_names = redis_ctl.keys(f'sg:project:{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])
            
            projects[each_data.get('project')] = {
                'id': int(project_result.get('id')),
                'code': project_result.get('code'),
                'path': project_result.get('sg_project_path')
            }
    
    return projects

def entity_redis_pattern(data):
    """
    Constructs a Redis pattern based on the provided data dictionary.

    Args:
        data (dict): A dictionary containing the data for constructing the Redis pattern.
            The dictionary should contain the following keys:
            - project (str): The project name.
            - episode (str): The episode name.
            - sequence (str): The sequence name.
            - shot (str): The shot name.
            - type (str): The asset type.
            - asset_type (str): The asset type (alternative to 'type').
            - asset (str): The asset name.
            - variation (str): The asset variation.

    Returns:
        dict: A dictionary containing the following keys:
            - entity_name (str): The constructed entity name.
            - entity_type (str): The type of the entity ('Shot' or 'Asset').
            - redis_name (str): The constructed Redis pattern.
            - redis_names (list): A list of Redis keys matching the Redis pattern.
    """
    project = data.get('project')
    episode = data.get('episode')
    sequence = data.get('sequence')
    shot = data.get('shot')
    asset_type = data.get('type') or data.get('asset_type')
    asset = data.get('asset')
    variation = data.get('variation')

    entity_name = ''
    entity_type = ''
    redis_name = ''

    if episode or sequence or shot:
        entity_type = 'Shot'
        redis_name = 'sg:shot:'
        redis_name += f'*{project}:' if project else '*:'
        redis_name += f'*{episode}:' if episode else '*:'
        redis_name += f'*_{sequence}:' if sequence else '*:'
        redis_name += f'*_{shot}:*' if shot else '*:*'

        entity_name = f'{project}' if project else ''
        entity_name += f'_{episode}' if episode else ''
        entity_name += f'_{sequence}' if sequence else ''
        entity_name += f'_{shot}' if shot else ''

    elif asset_type or asset:
        entity_type = 'Asset'
        redis_name = 'sg:asset:'
        redis_name += f'*{project}:' if project else '*:'
        redis_name += f'{asset_type}:' if asset_type else '*:'

        if variation:
            redis_name += f'{asset}:' if asset else '*'
            redis_name += f'_{variation}:*' if variation else '*:*'
            entity_name = f'{asset}' if asset else ''
            entity_name += f'_{variation}' if variation else ''

        else:
            redis_name += f'{asset}:*' if asset else '*:*'
            entity_name = asset

    
    redis_names = redis_ctl.keys(redis_name.lower())

    if entity_name:
        return {
            'entity_name': re.findall('\d+_(\w+)', entity_name)[0] if re.match('^\d+_', entity_name) else entity_name,
            'entity_type': entity_type,
            'redis_name': redis_name,
            'redis_names': redis_names
        }
    else:
        return {
            'entity_name': '',
            'entity_type': entity_type,
            'redis_name': redis_name,
            'redis_names': redis_names
        }

def search_response(data, shotgrid, sg_fields, str_fields, nested_entity_fields=None):
    """
    Process the search response data based on the provided parameters.

    Args:
        data (dict): The search response data.
        shotgrid (bool): A flag indicating whether the data is from ShotGrid or not.
        sg_fields (list): A list of ShotGrid fields to include in the response.
        str_fields (list): A list of string fields to include in the response.
        nested_entity_fields (list, optional): A list of nested entity fields to include in the response.

    Returns:
        dict: The processed response data.

    Raises:
        None

    """
    if shotgrid:
        return redis_utils.redis_correct_data_from_cache(data)
    else:
        return entity_response_adapter(data, sg_fields, str_fields, nested_entity_fields)

def entity_response_adapter(data, sg_fields, str_fields, nested_entity_fields=None):
    """
    Converts the given data into a structured response format based on the provided field mappings.

    Args:
        data (list): The data to be converted.
        sg_fields (dict): A dictionary mapping the field names in the data to their corresponding names in the response format.
        str_fields (list): A list of field names that should be converted to strings.
        nested_entity_fields (dict, optional): A dictionary mapping the nested entity field names to their corresponding field mappings. Defaults to None.

    Returns:
        list: The converted data in the structured response format.
    """
    result = []
    convert_fileds = []
    string_to_list_values = [
        'geometry_cacheable_nodes'
    ]
    string_to_dict_values = [
        'namespaces', 
    ]

    step_regex_pattern = re.compile('[a-z_]+\.(step)\.', re.IGNORECASE)

    for each_data in data:
        entity_data = OrderedDict()

        if nested_entity_fields:
            for key in nested_entity_fields.keys():
                entity_data[key] = OrderedDict()
        
        entity_data['step'] = OrderedDict()
        entity_data['task'] = OrderedDict()

        for key, val in each_data.items():
            if sg_fields.get(key):  
                if step_regex_pattern.search(key.lower()):
                    key_field = key.split('.')[-1].lower()

                    if key_field == 'id':
                        entity_data['step']['type'] = 'Step'
                        entity_data['step']['id'] = int(val) if val else None

                    if key_field == 'code':
                        entity_data['step']['name'] = str(val)

                    if key_field == 'short_name':
                        entity_data['step']['short_name'] = str(val)
                
                elif key.lower().startswith('task') or key.lower().startswith('sg_task'):
                    key_field = key.split('.')[-1].lower()
                    if key_field == 'id':
                        entity_data['task']['type'] = 'Task'
                        entity_data['task']['id'] = int(val) if val else None
                    
                    if key_field == 'content':
                        entity_data['task']['name'] = str(val)
                        
                    if key_field == 'sg_step_id':
                        entity_data['task']['priority'] = int(val) if val else None
                                    
                else:
                    entity_data[sg_fields[key]] = val

            else:
                if 'episode' in key.lower():
                    key_field = sg_fields[nested_entity_fields['episode'][key]].split('episode_')[-1]  
                    entity_data['episode']['type'] = 'Episode'

                    if key_field == 'id':
                        entity_data['episode']['id'] = int(val) if val else None

                    if key_field == 'code':
                        entity_data['episode']['name'] = str(val)

                    else:
                        entity_data['episode'][key_field] = str(val)

                if 'sequence' in key.lower():
                    key_field = sg_fields[nested_entity_fields['sequence'][key]].split('sequence_')[-1]  
                    entity_data['sequence']['type'] = 'Sequence'

                    if key_field == 'id':
                        entity_data['sequence']['id'] = int(val) if val else None
                    
                    elif key_field == 'code':
                        entity_data['sequence']['name'] = str(val)

                    else:
                        entity_data['sequence'][key_field] = str(val)
                
        convert_fileds.append(entity_data)

    for each_data in convert_fileds:
        each_parsed_data = {}

        for key, val in each_data.items():
            try:
                each_parsed_data[key] = literal_eval(val)
            except:
                each_parsed_data[key] = val

            if key in str_fields:
                each_parsed_data[key] = str(val)

            if key in string_to_list_values:
                each_parsed_data[key] = val.split(',') if val else []

            if key in string_to_dict_values:
                try:
                    each_parsed_data[key] = literal_eval(val)
                except ValueError:
                    each_parsed_data[key] = []
            
        result.append(each_parsed_data)
    return result

def sg_user_id(username):
    """
    Retrieve the user ID associated with the given username.

    Args:
        username (str): The username to retrieve the user ID for.

    Returns:
        int or None: The user ID if found, otherwise None.
    """
    user_id = None
    redis_user_names = redis_ctl.keys(f'sg:user:{username}:*'.lower())

    if len(redis_user_names) > 0:
        user_id = int(redis_user_names[0].split(':')[-1])
        
    return user_id

def entity_valid_body_key(args_dict, body):
    """
    Check if the keys in the body dictionary are valid based on the provided arguments dictionary.

    Args:
        args_dict (dict): A dictionary containing the valid keys.
        body (dict): A dictionary containing the keys to be validated.

    Returns:
        bool: True if all keys in the body dictionary are valid, False otherwise.
    """
    valid_key = True

    for key in body.keys():
        if key == 'id':
            valid_key = True
        elif key not in args_dict.keys():
            valid_key = False
            break
    
    return valid_key