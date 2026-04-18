# FastAPI启动入口
# 启动Agent服务，监听8001端口，提供HTTP API供Java服务调用
from fastapi import FastAPI
from src.config.settings import settings
from src.api import chat

app = FastAPI(title="Employee Assistant Agent", version="1.0.0")

# 注册路由
app.include_router(chat.router, prefix="/api/agent", tags=["agent"])


@app.get("/health")
def health_check():
    # 健康检查接口，用于服务监控
    return {"status": "ok", "service": "agent-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
