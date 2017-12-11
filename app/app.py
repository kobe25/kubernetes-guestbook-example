import os

from flask import Flask, jsonify, Response
import redis


app = Flask(__name__)
slave_replicas = int(os.getenv("REDIS_SLAVE_REPLICAS", 1))
write_timeout = int(os.getenv("REDIS_WRITE_TIMEOUT", 10)) * 1000


@app.route("/api/data/<key>")
def key(key):
    r = redis.StrictRedis(host="redis-slave", port=6379, db=0)

    value = r.get(key)
    return jsonify({"data": value.decode("ascii") if value else ""})


@app.route("/api/data/<key>/<value>", methods=["POST"])
def set_key(key, value):
    r = redis.StrictRedis(host="redis-master", port=6379, db=0)

    ret = r.set(key, value)
    if not ret:
        raise Exception("Value not setted")
    ret = r.wait(slave_replicas, write_timeout)
    if ret != slave_replicas:
        raise Exception("Replication to Redis slaves not completed")

    return jsonify({"message": "Updated"})


def is_ready(host):
    try:
        r = redis.StrictRedis(host=host, port=6379, db=0)
        return r.ping()
    except Exception as e:
        print(e)
        return False


@app.route("/healthz")
def healthz():
    if not is_ready("redis-master") or not is_ready("redis-slave"):
        return Response(status=500)

    return Response(status=200)
