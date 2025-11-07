# FastAPI应用入口
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import logging
import time
from contextlib import asynccontextmanager

from .core.config import settings
from .api.endpoints import router as api_router

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

# 确保模板和静态文件目录存在
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)

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
        debug=True,
        lifespan=lifespan
    )
    
    # 挂载静态文件和模板
    application.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    
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
        
        # 记录请求信息（排除静态文件请求）
        if not request.url.path.startswith('/static'):
            logger.info(f"📥 收到请求: {request.method} {request.url}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        if not request.url.path.startswith('/static'):
            logger.info(f"📤 返回响应: {response.status_code} - 处理时间: {process_time:.2f}s")
        
        return response
    
    # 包含API路由
    application.include_router(api_router, prefix="/api/v1")
    
    # 创建必要的目录
    required_dirs = ["temp_projects", "logs", "temp"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"📁 创建目录: {dir_name}")
    
    # 添加前端页面路由
    @application.get("/")
    async def read_root(request: Request):
        """渲染主页面"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @application.get("/demo")
    async def read_demo(request: Request):
        """演示页面"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    return application

app = create_application()

# ... 保留原有的异常处理、健康检查等端点 ...

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
        log_level="info"
    )