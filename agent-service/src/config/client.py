import redis
from minio import Minio

from src.config.settings import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password or None,
    db=settings.redis_db,
    decode_responses=True,
)

minio_client = Minio(
    settings.minio_host,  # WSL2 中的 MinIO 服务地址
    access_key=settings.minio_access_key,   # 替换为你的 MINIO_ROOT_USER
    secret_key=settings.minio_secret_key,   # 替换为你的 MINIO_ROOT_PASSWORD
    secure=False,       # 关键点：本地 HTTPS 证书不可用，设为 False
)