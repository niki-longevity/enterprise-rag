from elasticsearch import Elasticsearch
from typing import List

# ====================== 连接 ES ======================
# 本地ES默认地址，关闭安全验证
es = Elasticsearch(
    ["http://localhost:9200"],
    verify_certs=False
)

# 测试连接
print("ES 连接状态:", es.ping())  # True = 成功