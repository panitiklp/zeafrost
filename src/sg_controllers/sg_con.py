import os
import shotgun_api3
from dotenv import load_dotenv

basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

def connect():
    sg = shotgun_api3.Shotgun(
        os.environ.get('SHOTGRID_URL'),
        script_name=os.environ.get('SHOTGRID_SCRIPT_NAME'),
        api_key=os.environ.get('SHOTGRID_API_KEY')
    )

    return sg