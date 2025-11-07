# 文件操作工具
import os
import shutil
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FileUtils:
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """确保目录存在，如果不存在则创建"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败 {directory_path}: {str(e)}")
            return False
    
    @staticmethod
    def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """安全地写入文件，自动创建父目录"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            FileUtils.ensure_directory_exists(directory)
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.debug(f"文件写入成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"文件写入失败 {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def safe_read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """安全地读取文件内容"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"文件读取失败 {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_hours: int = 24):
        """清理指定目录中的旧文件"""
        try:
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        logger.info(f"清理旧文件: {filename}")
                        
        except Exception as e:
            logger.error(f"清理文件失败 {directory}: {str(e)}")
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"获取文件大小失败 {file_path}: {str(e)}")
            return 0
    
    @staticmethod
    def copy_directory(src: str, dst: str) -> bool:
        """复制整个目录"""
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            return True
        except Exception as e:
            logger.error(f"复制目录失败 {src} -> {dst}: {str(e)}")
            return False
    
    @staticmethod
    def find_files_by_extension(directory: str, extension: str) -> List[str]:
        """查找指定扩展名的所有文件"""
        matched_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(extension):
                        matched_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"查找文件失败 {directory}: {str(e)}")
        
        return matched_files
    
    @staticmethod
    def create_file_structure(base_path: str, structure: dict):
        """根据结构字典创建文件结构"""
        for name, content in structure.items():
            if isinstance(content, dict):
                # 如果是字典，创建子目录
                subdir_path = os.path.join(base_path, name)
                FileUtils.ensure_directory_exists(subdir_path)
                FileUtils.create_file_structure(subdir_path, content)
            else:
                # 如果是字符串，创建文件
                file_path = os.path.join(base_path, name)
                FileUtils.safe_write_file(file_path, content)