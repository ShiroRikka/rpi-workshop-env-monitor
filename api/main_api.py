# api/main_api.py
from fastapi import FastAPI
from state import shared_state

# 创建FastAPI应用实例
app = FastAPI(title="树莓派监控API")


@app.get("/")
async def read_root():
    return {"message": "欢迎使用树莓派监控API"}


@app.get("/status")
async def get_status():
    """
    获取所有传感器的最新读数
    """
    return shared_state


async def run_server(config):
    """
    启动FastAPI/Uvicorn服务器的异步函数
    """
    import uvicorn

    # uvicorn.Server 可以在异步环境中运行
    server_config = uvicorn.Config(
        app, host=config.API_HOST, port=config.API_PORT, log_level="info"
    )
    server = uvicorn.Server(server_config)
    await server.serve()
