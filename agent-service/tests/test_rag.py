from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from src.config.settings import settings

vector_store = Chroma(
            collection_name="policies",
            embedding_function=DashScopeEmbeddings(
                model=settings.dashscope_embedding_model
            ),
            persist_directory=settings.chroma_db_path
        )

query = "请假需要提前几天申请？"

result = vector_store.similarity_search(
    query,
    k=3
)

context = "\n".join([f"[{doc['title']}]{doc['content']}" for doc in result])
print(context)


