# api/main_api.py
from fastapi import FastAPI, HTTPException
from state import shared_state
from database.db import Database  # 导入数据库类
from typing import List, Dict, Any
from config import Settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="树莓派监控API")

# 依赖注入：获取数据库实例
# 这是一个更高级的做法，让API不直接依赖全局变量
# 但为了简单起见，我们暂时从DataManager获取
# 在真实项目中，你可能会有一个更复杂的依赖注入容器
# 这里我们简化处理，假设可以从某个地方获取db实例
# 为了演示，我们暂时用一个全局变量，但这不是最佳实践
# 最佳实践是使用FastAPI的Depends系统
# 我们先实现功能，稍后可以优化

# 暂时先这样，我们稍后优化
# from services.data_manager import DataManager
# db_manager = DataManager() # 这不是个好主意，会重复初始化

# 更好的做法是让main_api能访问到已经初始化的db实例
# 我们先写一个简单的端点，稍后重构
# 让我们假设在main.py中，我们可以把db实例传给run_server


# 修改 api/main_api.py 的 run_server 函数
async def run_server(config: Settings, db_instance: Database):
    import uvicorn

    # 将db实例存到app.state中，这是FastAPI推荐的方式
    app.state.db = db_instance

    server_config = uvicorn.Config(
        app, host=config.API_HOST, port=config.API_PORT, log_level="info"
    )
    server = uvicorn.Server(server_config)
    await server.serve()


# 然后在main.py中调用时传入db实例
# await run_server(settings, data_manager.db)
# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许 Vite 开发服务器的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


# --- API路由 ---
@app.get("/")
async def read_root():
    return {"message": "欢迎使用树莓派监控API"}


@app.get("/status")
async def get_status():
    """获取所有传感器的最新读数"""
    return shared_state


@app.get("/history", response_model=List[Dict[str, Any]])
async def get_history(limit: int = 100):
    """获取历史数据"""
    # 从app.state中获取db实例
    db: Database = app.state.db
    if not db:
        raise HTTPException(status_code=503, detail="数据库服务不可用")

    try:
        readings = await db.get_latest_readings(limit=limit)
        return readings
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"从数据库读取历史数据失败: {e}"
        ) from e
