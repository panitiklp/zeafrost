import unittest
import requests
import os
from pprint import pprint

HOST = 'localhost'
PORT = 5000

EPISODE_API = f'http://{HOST}:{PORT}/zeafrost/api/v1/episode'

PROJECT_NAME = 'zpip99'
EPISODE_NAME = '999'
EPISODE_ID = 8271
EPISODE_PUBLISH_PATH = f'T:/rnd/{PROJECT_NAME}/publish/shot/{EPISODE_NAME}'

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

class Episode(unittest.TestCase):
    def test_cache(self):
        payload = {
            'project': PROJECT_NAME
        }
        res = requests.post(f'{EPISODE_API}/cache', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertEqual(res_data['data'], True)

    # ----------------- #
    #       CREATE      #
    # ----------------- #
    def test_create(self):
        payload = {
            'data':[
                {
                    'project': PROJECT_NAME,
                    'episode': EPISODE_NAME,
                    'directory': True
                }
            ]
        }
        res = requests.post(f'{EPISODE_API}/create', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertEqual(res_data.get('data'), True)
    
    # ----------------------------------------- #
    #       CHECK PROJECT CREATED IS EXISTS     #
    # ----------------------------------------- #
    def test_created_directory_exists(self):
        is_exists = os.path.exists(EPISODE_PUBLISH_PATH)
        self.assertTrue(is_exists, 'directory exists.')

    # ------------------------- #
    #       SEARCH BY NAME      #
    # ------------------------- #
    def test_search_by_name(self):
        payload = {
            'project': PROJECT_NAME,
            'episode': EPISODE_NAME
        }

        res = requests.post(f'{EPISODE_API}/search', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertNotEqual(res_data['data'], [])

    # ----------------------- #
    #       SEARCH BY ID      #
    # ----------------------- #
    def test_search_by_id(self):
        payload = {
            'id': EPISODE_ID
        }

        res = requests.post(f'{EPISODE_API}/search', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertNotEqual(res_data['data'], [])
    
    # ----------------- #
    #       UPDATE      #
    # ----------------- #
    def test_update(self):
        payload = {
            'data': [
                {
                    'filters': {
                        'project': PROJECT_NAME,
                        'episode': EPISODE_NAME
                    },
                    'values': {
                        'description': 'HELLO, WORLD'
                    }
                }
            ]
        }

        res = requests.post(f'{EPISODE_API}/update', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertGreater(len(res_data['data']), 0)

if __name__ == '__main__':
    unittest.main()