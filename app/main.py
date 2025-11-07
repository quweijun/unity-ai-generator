# FastAPI应用入口
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.core.config import settings
from app.api.endpoints import router as api_router

def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    application = FastAPI(
        title="Unity AI Generator",
        description="基于阿里通义大模型的Unity项目智能生成系统",
        version="1.0.0"
    )
    
    # 配置CORS中间件
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 包含API路由
    application.include_router(api_router, prefix="/api/v1")
    
    # 创建必要的目录
    os.makedirs("temp_projects", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    return application

app = create_application()

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "status": "running",
        "service": "Unity AI Generator",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )