# 配置文件
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 阿里云百炼配置
    ALI_API_KEY: str = os.getenv("ALI_API_KEY", "sk-ee07d39d9e224440ad4daebed836aec6")
    ALI_MODEL_CODER: str = "qwen-coder"  # 通义千问-Coder模型ID
    ALI_MODEL_ART: str = "wanx"         # 通义万相模型ID
    ALI_API_BASE: str = "https://dashscope.aliyuncs.com/api/v1/services/"
    
    # 应用配置
    PROJECT_TEMP_DIR: str = "temp_projects"
    MAX_PROJECT_SIZE: int = 50 * 1024 * 1024  # 50MB

settings = Settings()