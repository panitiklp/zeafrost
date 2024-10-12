import os
import redis
import time
from datetime import datetime
from dotenv import load_dotenv

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

def connect():
    redis_pool = redis.ConnectionPool(
        host=os.environ.get('REDIS_HOST_IP'),
        port=os.environ.get('REDIS_PORT'),
        password=os.environ.get('REDIS_PASSWORD'),
        decode_responses=True,
        db=0,
    )

    r = ''
    while True:
        try:
            r = redis.Redis(connection_pool=redis_pool, charset='utf-8')
            break

        except redis.exceptions.ConnectionError as e:
            sleep_time = 5

            print(f'{datetime.now()} - ERROR: Error connecting to Redis server: {e}')
            print(f'{datetime.now()} - INFO: Retrying in {sleep_time} seconds...')

            time.sleep(sleep_time)

    return r

