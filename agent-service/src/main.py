# FastAPI启动入口
# 启动员工助手服务，监听8001端口，前端直接调用此服务
from fastapi import FastAPI
from src.config.settings import settings
from src.api import chat, webhook

app = FastAPI(title="Employee Assistant Agent", version="1.0.0")

# 注册路由，前端直接调 /api/chat 等接口
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(webhook.router, prefix="/api", tags=["webhook"])


@app.get("/health")
def health_check():
    # 健康检查接口，用于服务监控
    return {"status": "ok", "service": "agent-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
