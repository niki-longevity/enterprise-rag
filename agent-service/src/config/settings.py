# 配置管理
# 统一管理Agent服务的配置项，从系统环境变量读取
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 服务监听配置
    host: str = "0.0.0.0"
    port: int = 8001

    # 阿里云千问API配置（从系统环境变量DASHSCOPE_API_KEY读取）
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")

    # DeepSeek API配置（从系统环境变量DEEPSEEK_API_KEY读取）
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 阿里云Embedding模型
    dashscope_embedding_model: str = "text-embedding-v2"

    # Java服务地址，用于Agent调用Java的内部API
    java_service_url: str = "http://localhost:8080"

    # ChromaDB向量库本地存储路径
    chroma_db_path: str = "./chroma_db"


settings = Settings()
