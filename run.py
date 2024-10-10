import gc
from ast import literal_eval
from flask import Flask, request, jsonify, make_response, send_from_directory
from collections import OrderedDict

from src import gen_utils, main_ctl, rocketchat
from src.redis_controllers import redis_ctl
from src.sg_entities import sg_user

app = Flask(__name__)

BASE_ROUTE = 'zeafrost/api/v1'
ALLOWED_METHODS = [
    'GET',
    'POST',
    'OPTIONS'
]
__version__ = 'v1.0'

API_TIMEZONE = 'Asia/Bangkok'

# ========================================== GENERIC =============================================== #
# ---------------------------- #
#       RESPONSE TEMPLATE      #
# ---------------------------- #
def api_response(**kwargs):
    res = OrderedDict()
    res['entity'] = kwargs.get('entity')
    
    if isinstance(kwargs.get('data'), dict):
        if kwargs['data'].get('error'):
            res['code'] = 400
            res['message'] = str(kwargs.get('data').get('error'))
            res['data'] = {}

        else:
            res['code'] = kwargs.get('code')
            res['message'] = kwargs.get('message') 
            res['data'] = kwargs.get('data') or {}
    else:
        res['code'] = kwargs.get('code')
        res['message'] = kwargs.get('message')
        res['data'] = kwargs.get('data')

    res['payload'] = kwargs.get('payload')
    res['timestamp'] = kwargs.get('timestamp')

    response = make_response(jsonify(res))
    response.headers['Content-Type'] = 'application/json; charset=utf-8;'
    response.headers['Accept'] = 'application/json; charset=utf-8;'
    response.headers['User-Agent'] = f'Zeafrost/{__version__}'

    return response

# ------------------ #
#       FAVICON      #
# ------------------ #
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(f'{app.root_path}/static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# =========================================== CRUD ================================================ #
# ----------------- #
#       SEARCH      #
# ----------------- #
@app.route(f'/{BASE_ROUTE}/<entity>/search', methods=ALLOWED_METHODS)
def search(entity):
    result = []
    body = {}

    if request.method == 'GET':
        body_raw = request.args
        for key, val in body_raw.items():
            val = str(val)
            try:
                body[key] = eval(val)
            except:
                body[key] = val
        
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.search(
            entity=entity.lower(),
            body=body
        )

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity=entity.lower(), 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# -------------------------------- #
#       SEARCH - TASK BY USER      #
# -------------------------------- #
@app.route(f'/{BASE_ROUTE}/task/search-by-user', methods=ALLOWED_METHODS)
def task_search_by_user():
    result = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.task_search_by_user(body=body)

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity='task', 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# ----------------- #
#       CREATE      #
# ----------------- #
@app.route(f'/{BASE_ROUTE}/<entity>/create', methods=ALLOWED_METHODS)
def create(entity):
    result = []
    body = {}
    
    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.create(
            entity=entity.lower(),
            body=body
        )

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity=entity.lower(), 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# ----------------- #
#       UPDATE      #
# ----------------- #
@app.route(f'/{BASE_ROUTE}/<entity>/update', methods=ALLOWED_METHODS)
def update(entity):
    result = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.update(
            entity=entity.lower(),
            body=body
        )

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity=entity.lower(), 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# ----------------- #
#       DELETE      #
# ----------------- #
@app.route(f'/{BASE_ROUTE}/<entity>/delete', methods=ALLOWED_METHODS)
def delete(entity):
    result = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.delete(
            entity=entity.lower(),
            body=body
        )

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity=entity.lower(), 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# ---------------- #
#       CACHE      #
# ---------------- #
@app.route(f'/{BASE_ROUTE}/<entity>/cache', methods=ALLOWED_METHODS)
def cache(entity):
    result = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if request.method in ['GET', 'POST']:
        result = main_ctl.cache(
            entity=entity.lower(),
            body=body
        )

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity=entity.lower(), 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res


@app.route(f'/{BASE_ROUTE}/user/sync', methods=ALLOWED_METHODS)
def user_sync():
    result = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':

        body = request.json
        result = sg_user.user_sync(body)
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message=result.get('message'), 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res

    res = api_response(
        code=result.get('code'), 
        message=result.get('message'), 
        entity='user', 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    return res


# =========================================== ROCKETCHAT ================================================ #
# --------------------------- #
#      ROCKETCHAT SEARCH      #
# --------------------------- #
@app.route(f'/{BASE_ROUTE}/rocketchat/<collection>/search', methods=ALLOWED_METHODS)
def rocketchat_search(collection):
    result = OrderedDict()
    result['data'] = []

    rocketchat_name = ''
    redis_names = []
    body = {}

    if request.method == 'GET':
        body = request.args
    
    elif request.method == 'POST':
        body = request.json
    
    elif request.method == 'OPTIONS':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res

    if collection == 'user':
        rocketchat_name = body.get('username')
    
    elif collection == 'room':
        if body.get('id'):
            rocketchat_name = f'*:{body.get("id")}'
        else:
            rocketchat_name = f'{body.get("room")}:*'
    
    if rocketchat_name:
        redis_names = redis_ctl.keys(f'rocketchat:{collection}:{rocketchat_name}'.lower())

        # ----------------------------------------------- #
        #       CACHE AGAIN IF REDIS NAME NOT EXISTS      #
        # ----------------------------------------------- #
        if len(redis_names) == 0:
            rocketchat.rocketchat_user_room_cache()
            redis_names = redis_ctl.keys(f'rocketchat:{collection}:{rocketchat_name}'.lower())

        for name in redis_names:
            data = OrderedDict()
            redis_data = redis_ctl.hgetall(name)
            
            if isinstance(redis_data, dict):
                for key, val in redis_data.items():
                    if key != 'rooms':
                        data[key] = val

                    else:
                        data['rooms'] = literal_eval(val)

                result['data'].append(data)
        
    res = api_response(
        code=200, 
        message='OK' if len(result['data']) > 0 else 'Data Not Found.', 
        entity=f'rocketchat/{collection}', 
        payload=body, 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# =========================================== REDIS ================================================ #
# ------------------------- #
#       REDIS FLUSHALL      #
# ------------------------- #
@app.route(f'/{BASE_ROUTE}/redis/flushall', methods=ALLOWED_METHODS)
def redis_flushall():
    if request.method == 'OPTION':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res

    result = redis_ctl.flushall()

    res = api_response(
        code=200 if result else 400, 
        message='OK' if result else 'UNSUCCESS', 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# ------------------------ #
#       REDIS FLUSHDB      #
# ------------------------ #
@app.route(f'/{BASE_ROUTE}/redis/flushdb', methods=ALLOWED_METHODS)
def redis_flushdb():
    if request.method == 'OPTION':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res

    result = redis_ctl.flushdb()

    res = api_response(
        code=200 if result else 400, 
        message='OK' if result else 'UNSUCCESS', 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()        # clean unreference memory

    return res

# --------------------- #
#       REDIS HSET      #
# --------------------- #
@app.route(f'/{BASE_ROUTE}/redis/hset', methods=ALLOWED_METHODS)
def redis_hset():
    body = {}

    if request.method == 'GET':
        body = request.args

    elif request.method == 'POST':
        body = request.json

    elif request.method == 'OPTION':
        res = api_response(
            code=200, 
            message='', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
        return res
    
    if body.keys():
        result = redis_ctl.hset(str(list(body.keys())[0]).lower(), list(body.values())[0])

        res = api_response(
            code=200, 
            message=result, 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )

    else:
        res = api_response(
            code=400, 
            message='no data input.', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
    
    gc.collect()        # clean unreference memory

    return res

# ----------------------- #
#       REDIS DELETE      #
# ----------------------- #
@app.route(f'/{BASE_ROUTE}/redis/delete', methods=ALLOWED_METHODS)
def redis_delete():
    body = {}

    if request.method == 'GET':
        body = request.args

    elif request.method == 'POST':
        body = request.json
    
    if body.get('pattern'):
        result = redis_ctl.delete(body.get('pattern'))

        res = api_response(
            code=200, 
            message=f'delete {result} keys', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )

    else:
        res = api_response(
            code=400, 
            message='no data input.', 
            timestamp=gen_utils.get_timestamp(API_TIMEZONE)
        )
    
    gc.collect()        # clean unreference memory

    return res

# --------------- #
#       TEST      #
# --------------- #
@app.route(f'/{BASE_ROUTE}/test', methods=ALLOWED_METHODS)
def sg_test():
    result = main_ctl._test()
    
    res = api_response(
        code=200, 
        message='OK', 
        data=result.get('data'), 
        timestamp=gen_utils.get_timestamp(API_TIMEZONE)
    )

    gc.collect()  # clean unreference memory

    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)