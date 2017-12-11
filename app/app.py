import os

from flask import Flask, jsonify, Response
import redis


HTTP_STATUS_OK = 200
HTTP_STATUS_SERVER_ERROR = 500
app = Flask(__name__)
slave_replicas = int(os.getenv("REDIS_SLAVE_REPLICAS", 1))
write_timeout = int(os.getenv("REDIS_WRITE_TIMEOUT", 10)) * 1000

redis_master = redis.Redis(host="redis-master", port=6379, db=0)
redis_slave = redis.Redis(host="redis-slave", port=6379, db=0)


@app.route("/api/data/<key>")
def key(key):
    value = redis_slave.get(key)
    return jsonify({"data": value.decode("ascii") if value else ""})


@app.route("/api/data/<key>/<value>", methods=["POST"])
def set_key(key, value):
    ret = redis_master.set(key, value)
    if not ret:
        raise Exception("Value not setted")
    ret = redis_master.wait(slave_replicas, write_timeout)
    if ret != slave_replicas:
        raise Exception("Replication to Redis slaves not completed")

    return jsonify({"message": "Updated"})


def is_ready(host):
    try:
        r = redis.Redis(host=host, port=6379, db=0)
        return r.ping()
    except Exception as e:
        print(e)
        return False


@app.route("/healthz")
def healthz():
    health = is_ready("redis-master") and is_ready("redis-slave")
    return Response(status=HTTP_STATUS_OK if health else HTTP_STATUS_SERVER_ERROR)
