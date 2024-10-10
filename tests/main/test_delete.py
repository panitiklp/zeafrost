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

