import logging
import os

from flask import Flask, jsonify, request
from redis import Redis
from redis.exceptions import RedisError


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("cloud-course-backend")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

logger.info("Redis target configured: host=%s port=%s", REDIS_HOST, REDIS_PORT)

app = Flask(__name__)
redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)


@app.get("/api/ping")
def ping():
    logger.info(
        "Received /api/ping request from %s",
        request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    return jsonify(status="ok")


@app.get("/api/redis/set")
def redis_set():
    key = request.args.get("key", "testkey")
    value = request.args.get("value", "hello")
    try:
        redis_client.set(key, value)
        logger.info("Redis SET completed for key=%s", key)
        return jsonify(status="ok", key=key, value=value)
    except RedisError as exc:
        logger.exception("Redis SET failed for key=%s", key)
        return jsonify(status="error", message=str(exc)), 503


@app.get("/api/redis/get")
def redis_get():
    key = request.args.get("key", "testkey")
    try:
        value = redis_client.get(key)
        logger.info("Redis GET completed for key=%s found=%s", key, value is not None)
        return jsonify(status="ok", key=key, value=value, found=value is not None)
    except RedisError as exc:
        logger.exception("Redis GET failed for key=%s", key)
        return jsonify(status="error", message=str(exc)), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

