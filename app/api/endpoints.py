from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import asyncio
from datetime import datetime

# ！！！重要：必须先定义 router，然后才能使用装饰器！！！
router = APIRouter()

# 现在可以安全地使用 @router 装饰器了
@router.post("/generate-unity-project")
async def generate_unity_project(request: dict, background_tasks: BackgroundTasks):
    """生成Unity项目API端点 - 简化版本"""
    try:
        print(f"收到生成请求: {request}")
        
        # 返回测试响应
        return {
            "status": "success",
            "message": "项目生成功能已连接",
            "download_url": "/api/v1/download-project/test.zip",
            "filename": f"UnityProject_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "received_data": request
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

@router.get("/download-project/{filename}")
async def download_project(filename: str):
    """下载项目zip包 - 简化版本"""
    return {
        "status": "success", 
        "message": f"下载端点已连接 - 文件名: {filename}",
        "note": "实际文件下载功能待实现"
    }

@router.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "status": "success", 
        "message": "API端点工作正常",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "Unity AI Generator"}

# 清理函数
async def cleanup_temp_files(file_path: str):
    """清理临时文件"""
    await asyncio.sleep(300)
    if os.path.exists(file_path):
        os.remove(file_path)