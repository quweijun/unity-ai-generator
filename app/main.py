# FastAPI应用入口
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import os
import logging
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import router as api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的操作
    logger.info("🚀 Unity AI Generator 服务启动中...")
    logger.info(f"📁 工作目录: {os.getcwd()}")
    logger.info(f"🔑 API密钥状态: {'已设置' if settings.ALI_API_KEY else '未设置'}")
    
    yield  # 应用运行期间
    
    # 关闭时的操作
    logger.info("🛑 Unity AI Generator 服务关闭")

def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    application = FastAPI(
        title="Unity AI Generator",
        description="基于阿里通义大模型的Unity项目智能生成系统",
        version="1.0.0",
        debug=True,  # 开启调试模式
        lifespan=lifespan
    )
    
    # 配置CORS中间件
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 自定义中间件：请求日志记录
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"📥 收到请求: {request.method} {request.url}")
        logger.info(f"📋 客户端: {request.client.host}:{request.client.port}")
        
        # 对于POST请求，记录请求体（但避免记录敏感信息）
        if request.method == "POST" and "generate-unity-project" in str(request.url):
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    # 只记录前500个字符，避免日志过大
                    logger.info(f"📦 请求体 (前500字符): {body_str[:500]}...")
                # 重新设置请求体，因为body()方法会消耗它
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
            except Exception as e:
                logger.warning(f"❌ 记录请求体失败: {e}")
        
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(f"📤 返回响应: {response.status_code} - 处理时间: {process_time:.2f}s")
        
        return response
    
    # 包含API路由
    application.include_router(api_router, prefix="/api/v1")
    
    # 创建必要的目录
    required_dirs = ["temp_projects", "logs", "temp"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"📁 创建目录: {dir_name}")
    
    return application

app = create_application()

# 全局异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误（422错误）"""
    logger.error(f"❌ 请求验证失败: {exc.errors()}")
    logger.error(f"📦 请求体: {await request.body()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "请求数据验证失败",
            "detail": exc.errors(),
            "body_preview": str(await request.body())[:500]  # 记录请求体前500字符
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.error(f"❌ HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理其他未捕获的异常"""
    logger.error(f"💥 未处理异常: {str(exc)}")
    import traceback
    logger.error(f"🔍 堆栈跟踪: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "服务器内部错误",
            "detail": str(exc)
        }
    )

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "status": "running",
        "service": "Unity AI Generator",
        "version": "1.0.0",
        "endpoints": {
            "health_check": "/health",
            "api_docs": "/docs",
            "generate_project": "/api/v1/generate-unity-project"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    import psutil
    import platform
    
    # 检查必要的目录
    required_dirs = ["temp_projects", "logs", "temp"]
    dir_status = {}
    for dir_name in required_dirs:
        dir_status[dir_name] = os.path.exists(dir_name)
    
    # 系统信息
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "memory_usage": f"{psutil.virtual_memory().percent}%",
        "disk_usage": f"{psutil.disk_usage('.').percent}%"
    }
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "directories": dir_status,
        "system": system_info,
        "api_key_configured": bool(settings.ALI_API_KEY)
    }

@app.get("/info")
async def service_info():
    """服务信息端点"""
    return {
        "service": "Unity AI Generator",
        "version": "1.0.0",
        "description": "基于阿里通义大模型的Unity项目智能生成系统",
        "features": [
            "Unity项目代码生成",
            "游戏资源自动生成",
            "项目打包下载",
            "支持多种游戏类型"
        ],
        "supported_game_types": [
            "2d_platformer", "shooter", "rpg", "puzzle", "adventure"
        ]
    }

if __name__ == "__main__":
    logger.info("🎯 正在启动 Unity AI Generator 服务...")
    
    # 检查环境变量
    if not settings.ALI_API_KEY:
        logger.warning("⚠️  未检测到 ALI_API_KEY 环境变量，请确保已正确设置")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",  # 设置为debug级别以获取更多信息
        access_log=True
    )