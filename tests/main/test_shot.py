import unittest
import requests
import os
from pprint import pprint

HOST = 'localhost'
PORT = 5000

SHOT_API = f'http://{HOST}:{PORT}/zeafrost/api/v1/shot'

PROJECT_NAME = 'zpip99'
EPISODE_NAME = '999'
SEQUENCE_NAME = 's01'
SHOT_NAME = '0010'
SHOT_ID = 54025
SHOT_PUBLISH_PATH = f'T:/rnd/{PROJECT_NAME}/publish/shot/{EPISODE_NAME}/{SEQUENCE_NAME}/{SHOT_NAME}'

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

class Shot(unittest.TestCase):
    def test_cache(self):
        payload = {
            'project': PROJECT_NAME
        }
        res = requests.post(f'{SHOT_API}/cache', json=payload, headers=HEADERS)
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
                    'sequence': SEQUENCE_NAME,
                    'shot': SHOT_NAME,
                    'directory': True
                }
            ]
        }
        res = requests.post(f'{SHOT_API}/create', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertEqual(res_data.get('data'), True)
    
    # ----------------------------------------- #
    #       CHECK PROJECT CREATED IS EXISTS     #
    # ----------------------------------------- #
    def test_created_directory_exists(self):
        is_exists = os.path.exists(SHOT_PUBLISH_PATH)
        self.assertTrue(is_exists)

    # ------------------------- #
    #       SEARCH BY NAME      #
    # ------------------------- #
    def test_search_by_name(self):
        payload = {
            'project': PROJECT_NAME,
            'episode': EPISODE_NAME,
            'sequence': SEQUENCE_NAME,
            'shot': SHOT_NAME
        }

        res = requests.post(f'{SHOT_API}/search', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertNotEqual(res_data['data'], [])

    # ----------------------- #
    #       SEARCH BY ID      #
    # ----------------------- #
    def test_search_by_id(self):
        payload = {
            'id': SHOT_ID
        }

        res = requests.post(f'{SHOT_API}/search', json=payload, headers=HEADERS)
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
                        'episode': EPISODE_NAME,
                        'sequence': SEQUENCE_NAME,
                        'shot': SHOT_NAME
                    },
                    'values': {
                        'description': 'HELLO, WORLD',
                        'status': 'fin'
                    }
                }
            ]
        }

        res = requests.post(f'{SHOT_API}/update', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertGreater(len(res_data['data']), 0)

if __name__ == '__main__':
    unittest.main()