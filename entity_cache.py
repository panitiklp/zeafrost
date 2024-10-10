import requests
import logging

LOGGING_FORMAT = '%(asctime)s-%(levelname)s: %(entity)s // %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = 'http://localhost:5000'
API_URL = f'{HOST}/zeafrost/api/v1'

def cache_step():
    res = requests.get(f'{API_URL}/step/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'STEP'})

def cache_department():
    res = requests.get(f'{API_URL}/department/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'DEPARTMENT'})

def cache_pipelineconfiguration():
    res = requests.get(f'{API_URL}/pipelineconfiguration/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'PIPELINECONFIGURATION'})

def cache_software():
    res = requests.get(f'{API_URL}/software/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'SOFTWARE'})

def cache_publishfiletype():
    res = requests.get(f'{API_URL}/publishfiletype/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'PUBLISHFILETYPE'})

def cache_user():
    res = requests.get(f'{API_URL}/user/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'USER'})

def cache_project():
    res = requests.get(f'{API_URL}/project/cache')
    logger.info('cache done.' if res.status_code == 200 else 'cache failed.', extra={'entity': 'PROJECT'})

def cache_production_entity():
    project_data = requests.get(f'{API_URL}/project/search')
    for each in project_data.json()['data']:
        proj = each['project']

        ep_res = requests.get(f'{API_URL}/episode/cache?project={proj}')
        logger.info(f'{proj}\t\tcache done.' if ep_res.status_code == 200 else f'{proj}\t\tcache failed.', extra={'entity': 'EPISODE'})

        seq_res = requests.get(f'{API_URL}/sequence/cache?project={proj}')
        logger.info(f'{proj}\t\tcache done.' if seq_res.status_code == 200 else f'{proj}\t\tcache failed.', extra={'entity': 'SEQUENCE'})

        shot_res = requests.get(f'{API_URL}/shot/cache?project={proj}')
        logger.info(f'{proj}\t\tcache done.' if shot_res.status_code == 200 else f'{proj}\t\tcache failed.', extra={'entity': 'SHOT'})

        asset_res = requests.get(f'{API_URL}/asset/cache?project={proj}')
        logger.info(f'{proj}\t\tcache done.' if asset_res.status_code == 200 else f'{proj}\t\tcache failed.', extra={'entity': 'ASSET'})

if __name__ == '__main__':
    cache_step()
    cache_department()
    cache_pipelineconfiguration()
    cache_software()
    cache_publishfiletype()
    cache_user()
    cache_project()
    cache_production_entity()
