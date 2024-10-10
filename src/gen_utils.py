import pytz
import os
from datetime import datetime

def get_timestamp(tzname):
    timezone = pytz.timezone(tzname) if tzname else pytz.utc
    now = datetime.now(timezone)

    timestamp_str = now.strftime('%Y-%m-%dT%H:%M:%S%z')

    return timestamp_str


def make_dirs(dir_path):
    dir_path = dir_path.replace('\\', '/')
    
    count = 0
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            count = 1

        except Exception as e:
            count = 0
    
    return count