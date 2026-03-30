# =========================================================
# Redis Client Setup
# =========================================================
import redis
from app.config.settings import REDIS_URL

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5
)

try:
    redis_client.ping()
    print("Redis Connected Successfully")
except Exception as e:
    print("Redis Connection Failed:", e)
    
    