import os

from flask import Flask, jsonify, Response, g
from werkzeug.local import LocalProxy
from collections import namedtuple
import redis


app = Flask(__name__)
slave_replicas = int(os.getenv("REDIS_SLAVE_REPLICAS", 1))
write_timeout = int(os.getenv("REDIS_WRITE_TIMEOUT", 10)) * 1000

HTTP_STATUS_OK = 200
HTTP_STATUS_SERVER_ERROR = 500

RedisConnections = namedtuple('_redis_connections', ['master', 'slave'])


def get_redis_cnx():
    redis_cnx = getattr(g, '_redix_cnx', None)
    if not redis_cnx:
        master_cnx = redis.StrictRedis(host="redis-master", port=6379, db=0)
        slave_cnx = redis.StrictRedis(host="redis-slave", port=6379, db=0)
        g._redis_cnx = redis_cnx = RedisConnections(master_cnx, slave_cnx)
    return redis_cnx


redis_cnx = LocalProxy(get_redis_cnx)


@app.route("/api/data/<key>")
def key(key):
    r = redis_cnx.slave
    value = r.get(key)
    return jsonify({"data": value.decode("ascii") if value else ""})


@app.route("/api/data/<key>/<value>", methods=["POST"])
def set_key(key, value):
    r = redis_cnx.master

    ret = r.set(key, value)
    if not ret:
        raise Exception("Value not setted")
    ret = r.wait(slave_replicas, write_timeout)
    if ret != slave_replicas:
        raise Exception("Replication to Redis slaves not completed")

    return jsonify({"message": "Updated"})


def is_ready(host):
    try:
        r = getattr(redis_cnx, host)
        return r.ping()
    except Exception as e:
        print(e)
        return False


@app.route("/healthz")
def healthz():
    health = is_ready("master") and is_ready("slave")
    return Response(status=HTTP_STATUS_OK if health else HTTP_STATUS_SERVER_ERROR)
