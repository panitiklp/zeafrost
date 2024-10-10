import unittest
import requests
import os

HOST = 'localhost'
PORT = 5000
PROJECT_API = f'http://{HOST}:{PORT}/zeafrost/api/v1/project'

PROJECT_NAME = 'zpip99'
PROJECT_TYPE = 'rnd'
FRAME_RATE = '24'
RESOLUTION = '1920x1080'
PROJECT_PATH = f'T:/rnd/{PROJECT_NAME}'

PROJECT_ID = 2484

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

class Project(unittest.TestCase):
    # ---------------- #
    #       CACHE      #
    # ---------------- #
    def test_cache(self):
        res = requests.post(f'{PROJECT_API}/cache', json={}, headers=HEADERS)
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
                    'type': PROJECT_TYPE,
                    'frame_rate': FRAME_RATE,
                    'resolution': RESOLUTION,
                    'project_path': PROJECT_PATH,
                    'directory': True
                }
            ]
        }
        res = requests.post(f'{PROJECT_API}/create', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertEqual(res_data.get('data'), True)
    
    # ----------------------------------------- #
    #       CHECK PROJECT CREATED IS EXISTS     #
    # ----------------------------------------- #
    def test_created_directory_exists(self):
        is_exists = os.path.exists(PROJECT_PATH)
        self.assertEqual(is_exists, True)

    # ------------------------- #
    #       SEARCH BY NAME      #
    # ------------------------- #
    def test_search_by_name(self):
        payload = {
            'project': PROJECT_NAME
        }

        res = requests.post(f'{PROJECT_API}/search', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertNotEqual(res_data['data'], [])

    # ----------------------- #
    #       SEARCH BY ID      #
    # ----------------------- #
    def test_search_by_id(self):
        payload = {
            'id': PROJECT_ID
        }

        res = requests.post(f'{PROJECT_API}/search', json=payload, headers=HEADERS)
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
                        'project': PROJECT_NAME
                    },
                    'values': {
                        'description': 'HELLO, WORLD'
                    }
                }
            ]
        }

        res = requests.post(f'{PROJECT_API}/update', json=payload, headers=HEADERS)
        res_data = res.json()
        self.assertGreater(len(res_data['data']), 0)

if __name__ == '__main__':
    unittest.main()