@router.post("/generate-unity-project")
async def generate_unity_project(
    request: GameGenerationRequest,
    background_tasks: BackgroundTasks
):
    """生成Unity项目API端点"""
    try:
        logger.info(f"开始处理游戏生成请求: {request.game_type}")
        
        zip_path = await project_builder.create_unity_project(request.dict())
        
        # 获取文件名
        filename = os.path.basename(zip_path)
        
        # 清理临时文件
        background_tasks.add_task(cleanup_temp_files, zip_path)
        
        return {
            "status": "success",
            "message": "项目生成完成",
            "download_url": f"/api/v1/download-project/{filename}",
            "filename": filename,
            "game_type": request.game_type
        }
    except Exception as e:
        logger.error(f"项目生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"项目生成失败: {str(e)}")

@router.get("/download-project/{filename}")
async def download_project(filename: str):
    """下载项目zip包"""
    file_path = f"temp/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        filename=f"UnityProject_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
        media_type='application/zip'
    )