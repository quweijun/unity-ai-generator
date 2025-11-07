# API路由
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.models.schemas import GameGenerationRequest
from app.services.project_builder import ProjectBuilder

router = APIRouter()
project_builder = ProjectBuilder()

@router.post("/generate-unity-project")
async def generate_unity_project(
    request: GameGenerationRequest,
    background_tasks: BackgroundTasks
):
    """生成Unity项目API端点"""
    try:
        zip_path = await project_builder.create_unity_project(request.dict())
        
        # 清理临时文件
        background_tasks.add_task(cleanup_temp_files, zip_path)
        
        return {
            "status": "success",
            "message": "项目生成完成",
            "download_url": f"/download-project/{os.path.basename(zip_path)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"项目生成失败: {str(e)}")

@router.get("/download-project/{filename}")
async def download_project(filename: str):
    """下载项目zip包"""
    file_path = f"temp/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        filename=f"UnityProject_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    )

async def cleanup_temp_files(file_path: str):
    """清理临时文件"""
    await asyncio.sleep(300)  # 5分钟后清理
    if os.path.exists(file_path):
        os.remove(file_path)