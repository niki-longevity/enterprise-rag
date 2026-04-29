import redis
from minio import Minio
from src.shared.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password or None,
    db=settings.redis_db,
    decode_responses=True,
)

minio_client = Minio(
    settings.minio_host,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)