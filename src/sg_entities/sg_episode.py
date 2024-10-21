import os
import re
import sys
import threading
import shutil

from . import sg_entity_utils, sg_project
from .. import dir_template, gen_utils
from ..sg_controllers import sg_con
from ..redis_controllers import redis_ctl, redis_utils

CUR_PLATFORM = sys.platform.lower()
API_TIMEZONE = 'Asia/Bangkok'

SG_FIELD_MAPS = {
    'id': 'id',
    'project': 'project',
    'episode': 'code',
    'short_name': 'sg_short_name',
    'status': 'sg_status_list',
    'description': 'description',
    'frame_rate': 'sg_frame_rate',
    'resolution': 'sg_resolution'
}

SG_FIELD_MAPS_INVERT = {val: key for key, val in SG_FIELD_MAPS.items()}

# ========================= #
#       ENTITY CACHE        #
# ========================= #
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
            'Episode',
            filters=[['project', 'name_contains', project]],
            fields=list(SG_FIELD_MAPS.values()),
            order=[{'field_name': 'code', 'direction': 'asc'}]
        )

        redis_pattern = f'sg:episode:*{project}:*'.lower()
        redis_ctl.delete(redis_pattern)

    for elem in sg_result:
        sg_project = elem.get('project')

        if sg_project:
            redis_name = 'sg:episode:'
            redis_name += f'{sg_project.get("name")}:'
            redis_name += f'{elem.get("code")}:'
            redis_name += f'{elem.get("id")}'
            redis_ctl.hset(redis_name.lower(), redis_utils.redis_prepare_cache_data(elem))

    return True

# ================================== #
#       SHOTGRID ENTITY SEARCH       #
# ================================== #
def sg_entity_search(body):
    shotgrid = body.get('shotgrid') or False
    project = body.get('project')
    episode = body.get('episode')
    episode_id = body.get('id')

    valid_keys = {
        'shotgrid',
        'project',
        'episode',
        'id'
    }

    if not set(body.keys()).issubset(valid_keys):
        return []

    result = []

    redis_name = 'sg:episode:'
    redis_name += f'*{project}:' if project else '*:'
    redis_name += f'*{episode}:' if episode else '*:'
    redis_name += f'{episode_id}' if episode_id else '*'
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
        data=result,
        shotgrid=shotgrid,
        sg_fields=SG_FIELD_MAPS_INVERT,
        str_fields=['code', 'name', 'episode']
    )

# ================================== #
#       SHOTGRID ENTITY CREATE       #
# ================================== #
def sg_entity_create(body):
    data = body.get('data')
    result = False

    projects = {}
    for each in data:
        project = each.get('project')
        redis_project_names = redis_ctl.keys(f'sg:project:*{project}:*'.lower())

        if len(redis_project_names) > 0:
            project_result = redis_ctl.hgetall(redis_project_names[0])

            projects[each.get('project')] = {
                'id': int(project_result.get('id')),
                'code': project_result.get('code'),
                'path': project_result.get('sg_project_path')
            }

    if projects:
        # ----------------------------------------- #
        #       CACHE BEFORE EPISODE PROCESS        #
        # ----------------------------------------- #
        for project_name, project_data in projects.items():
            entity_cache(project_id=project_data.get('id'))

        # ------------------------- #
        #       CREATE EPISODE      #
        # ------------------------- #
        sg_data = []
        for episode_data in data:
            project = episode_data.get('project')
            episode = episode_data.get('episode')

            redis_episode_name = 'sg:episode:'
            redis_episode_name += f'*{project}:' if project else '*:'
            redis_episode_name += f'*{episode}:*' if episode else '*'
            redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

            if len(redis_episode_names) == 0 and projects.get(project):
                episode_data = {
                    'request_type': 'create',
                    'entity_type': 'Episode',
                    'data': {
                        'project': {'type': 'Project', 'id': projects[project]['id']},
                        'code': episode,
                        'sg_short_name': episode,
                        'sg_status_list': 'wtg',
                        'description': episode_data.get('description'),
                        'sg_frame_rate': episode_data.get('frame_rate'),
                        'sg_resolution': episode_data.get('resolution')
                    }
                }
                sg_data.append(episode_data)

        if len(sg_data) > 0:
            sg = sg_con.connect()
            result = sg.batch(sg_data)

            thread_dir = threading.Thread(target=create_directory, args=(projects, data,))
            thread_dir.start()

        # ---------------------------------------- #
        #       CACHE AFTER EPISODE PROCESS        #
        # ---------------------------------------- #
        for project_name, project_data in projects.items():
            thread_cache = threading.Thread(
                target=entity_cache,
                kwargs={'project': project_name}
            )
            thread_cache.start()

    return result

# ================================== #
#       SHOTGRID ENTITY UPDATE       #
# ================================== #
def sg_entity_update(body):
    data = body.get('data') or []
    project_id = 0

    sg_update_data = []
    result = []

    for each_data in data:
        filters = each_data.get('filters')
        values = each_data.get('values')

        project = filters.get('project')
        episode = filters.get('episode')
        episode_id = filters.get('id')

        if project:
            redis_project_data = sg_entity_utils.redis_get_project_data(project=project.lower())

            # ------------------------------------------------- #
            #       CHECK PROJECT, IF NOT EXISTS THEN CACHE     #
            # ------------------------------------------------- #
            if redis_project_data:
                project_id = redis_project_data.get('id')

            else:
                sg_project.entity_cache()
                redis_project_data = sg_entity_utils.redis_get_project_data(project=project.lower())
                project_id = redis_project_data.get('id')

            # --------------------------- #
            #       GET EPISODE ID        #
            # --------------------------- #
            if project_id:
                redis_name = 'sg:episode:'
                redis_name += f'*{project}:' if project else '*:'
                redis_name += f'*{episode}:' if episode else '*:'
                redis_name += f'{episode_id}' if episode_id else '*'
                redis_names = redis_ctl.keys(redis_name.lower())

                if len(redis_names) > 0:
                    entity_id = int(redis_names[0].split(':')[-1])

                    sg_data = {}
                    if values:
                        for key, val in values.items():
                            sg_data[SG_FIELD_MAPS[key]] = val

                    sg_update_data.append(
                        {
                            'request_type': 'update',
                            'entity_type': 'Episode',
                            'entity_id': entity_id,
                            'data': sg_data
                        }
                    )
    # ------------------------- #
    #       SHOTGRID UPDATE     #
    # ------------------------- #
    if len(sg_update_data) > 0:
        sg = sg_con.connect()
        result = sg.batch(sg_update_data)

        thread_redis_cache_update = threading.Thread(
            target=entity_cache,
            kwargs={'project_id': project_id}
        )
        thread_redis_cache_update.start()

    return result

# ================================== #
#       SHOTGRID ENTITY DELETE       #
# ================================== #
def sg_entity_delete(body):
    data = body.get('data')
    result = []

    if data:
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

        if projects:
            # ----------------------------------------- #
            #       CACHE BEFORE EPISODE PROCESS        #
            # ----------------------------------------- #
            for project_name, project_data in projects.items():
                entity_cache(project_id=project_data.get('id'))

            # ------------------------- #
            #       DELETE EPISODE      #
            # ------------------------- #
            sg_data = []
            for episode_data in data:
                project = episode_data.get('project')
                episode = episode_data.get('episode')
                episode_id = episode_data.get('id')

                redis_episode_name = 'sg:episode:'
                redis_episode_name += f'*{project}:' if project else '*:'
                redis_episode_name += f'*{episode}:' if episode else '*:'
                redis_episode_name += f'{episode_id}' if episode_id else '*'
                redis_episode_names = redis_ctl.keys(redis_episode_name.lower())

                if len(redis_episode_names) > 0 and projects.get(project):
                    episode_data = {
                        'request_type': 'delete',
                        'entity_type': 'Episode',
                        'entity_id': int(redis_episode_names[0].split(':')[-1])
                    }
                    sg_data.append(episode_data)

            if len(sg_data) > 0:
                sg = sg_con.connect()
                result = sg.batch(sg_data)

                thread_dir = threading.Thread(target=delete_directory, args=(projects, data,))
                thread_dir.start()

            # ---------------------------------------- #
            #       CACHE AFTER EPISODE PROCESS        #
            # ---------------------------------------- #
            for project_name, project_data in projects.items():
                thread_cache = threading.Thread(
                    target=entity_cache,
                    kwargs={'project_id': int(project_data.get('id'))}
                )
                thread_cache.start()

    return result

# ==================================== #
#       EPISODE CREATE DIRECTORY       #
# ==================================== #
def create_directory(projects, data):
    '''
    Parameters:
        projects (dict): project's data 
            projects = {
                "FOO": {
                    "id": 1,
                    "path": "path/to/project/FOO"
                }
            }

    Returns:
        True
    '''
    for episode_data in data:
        if episode_data.get('directory') == True:
            project_path = projects[episode_data.get('project')]['path']

            if CUR_PLATFORM == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if os.path.exists(project_path):
                for _dir in dir_template.EPISODE_DIRECTORIES:
                    dir_path = f'{project_path}/{_dir.format(ep=episode_data.get("episode"))}'
                    gen_utils.make_dirs(dir_path)

    return True

# ==================================== #
#       EPISODE DELETE DIRECTORY       #
# ==================================== #
def delete_directory(projects, data):
    for episode_data in data:
        if episode_data.get('directory') == True:
            project_path = projects[episode_data.get('project')]['path']

            if CUR_PLATFORM == 'linux':
                project_path = sg_entity_utils.convert_path_windows_to_linux(project_path)

            if os.path.exists(project_path):
                for _dir in dir_template.EPISODE_DIRECTORIES:
                    dir_path = f'{project_path}/{_dir.format(ep=episode_data.get("episode"))}'
                    try:
                        shutil.rmtree(dir_path)

                    except Exception as e:
                        print(f'{gen_utils.get_timestamp(API_TIMEZONE)} ERROR: {e.strerror}')

    return True
