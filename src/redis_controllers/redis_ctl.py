from . import redis_con

def hset(key, val):
    r = redis_con.connect()
    result = r.hset(key, mapping=val)

    return result

def keys(pattern):
    r = redis_con.connect()
    result = r.keys(pattern)

    return result

def hget(name, key):
    r = redis_con.connect()
    result = r.hget(name, key)

    return result

def hgetall(name):
    r = redis_con.connect()
    result = r.hgetall(name)
    
    return result
    
def flushall():
    r = redis_con.connect()
    result = r.flushall()
    
    return result
    
def flushdb():
    r = redis_con.connect()
    result = r.flushdb()
    
    return result

def delete(pattern):
    r = redis_con.connect()

    count = 0
    for key in r.scan_iter(pattern):
        r.delete(key)
        count += 1
    
    return count