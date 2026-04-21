from src.rag.retriever import search

query = "请假需要提前几天申请？"

res = search( query, 3)
print(res)


