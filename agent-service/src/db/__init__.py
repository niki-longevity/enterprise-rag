# 数据库模块初始化
from src.db.session import engine
from src.db.models import Base

Base.metadata.create_all(bind=engine)
