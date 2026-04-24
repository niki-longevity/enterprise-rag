from src.rag.retriever import search

query = "请假需要提前几天申请？"

res = search( query, 3)
list = [doc["content"] for doc in res]
# print(list)
print("\n".join(list))

