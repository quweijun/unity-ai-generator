# FastAPI应用入口
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 使用绝对导入（避免相对导入问题）
try:
    from app.api.endpoints import router as api_router
    logger.info("✅ 绝对导入成功")
except ImportError as e:
    logger.error(f"❌ 导入失败: {e}")
    # 创建空的路由器作为备选
    from fastapi import APIRouter
    api_router = APIRouter()
    
    @api_router.get("/test")
    async def test():
        return {"message": "基础API工作正常"}

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
    
    # 挂载静态文件和模板
    application.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    
    # 包含API路由
    application.include_router(api_router, prefix="/api/v1")
    
    # 创建必要的目录
    required_dirs = ["temp_projects", "logs", "static/css", "static/js", "templates"]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
        logger.info(f"📁 创建目录: {dir_name}")
    
    # 添加前端页面路由
    @application.get("/")
    async def read_root(request: Request):
        """渲染主页面"""
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            logger.error(f"渲染模板失败: {e}")
            return JSONResponse(
                content={
                    "status": "running",
                    "service": "Unity AI Generator", 
                    "message": "Web界面正在开发中，API端点已就绪"
                }
            )
    
    return application

app = create_application()

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Unity AI Generator",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    logger.info("🚀 启动 Unity AI Generator 服务...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )