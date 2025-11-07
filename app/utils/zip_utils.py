# 压缩包工具
import zipfile
import os
import logging
from typing import List, Optional
from app.utils.file_utils import FileUtils

logger = logging.getLogger(__name__)

class ZipUtils:
    @staticmethod
    def create_zip_from_directory(
        source_dir: str, 
        output_zip: str, 
        exclude_dirs: List[str] = None
    ) -> bool:
        """
        从目录创建zip压缩包
        
        Args:
            source_dir: 源目录路径
            output_zip: 输出的zip文件路径
            exclude_dirs: 要排除的目录列表
            
        Returns:
            bool: 是否成功创建
        """
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', '.DS_Store']
        
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    # 排除指定的目录
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for file in files:
                        if file in exclude_dirs:
                            continue
                            
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"成功创建压缩包: {output_zip}")
            return True
            
        except Exception as e:
            logger.error(f"创建压缩包失败 {source_dir} -> {output_zip}: {str(e)}")
            return False
    
    @staticmethod
    def extract_zip(zip_path: str, extract_to: str) -> bool:
        """解压zip文件到指定目录"""
        try:
            FileUtils.ensure_directory_exists(extract_to)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_to)
            
            logger.info(f"成功解压文件: {zip_path} -> {extract_to}")
            return True
            
        except Exception as e:
            logger.error(f"解压文件失败 {zip_path}: {str(e)}")
            return False
    
    @staticmethod
    def get_zip_file_list(zip_path: str) -> Optional[List[str]]:
        """获取zip文件中的文件列表"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                return zipf.namelist()
        except Exception as e:
            logger.error(f"读取zip文件列表失败 {zip_path}: {str(e)}")
            return None
    
    @staticmethod
    def add_files_to_zip(zip_path: str, files_to_add: List[tuple]) -> bool:
        """
        添加文件到现有的zip包中
        
        Args:
            zip_path: zip文件路径
            files_to_add: 要添加的文件列表，格式为[(文件路径, 在zip中的路径), ...]
        """
        try:
            with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, arcname in files_to_add:
                    if os.path.exists(file_path):
                        zipf.write(file_path, arcname)
                        logger.debug(f"添加文件到压缩包: {file_path} -> {arcname}")
            
            return True
            
        except Exception as e:
            logger.error(f"添加文件到压缩包失败 {zip_path}: {str(e)}")
            return False
    
    @staticmethod
    def get_zip_info(zip_path: str) -> Optional[dict]:
        """获取zip文件的详细信息"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                total_size = sum(zipf.getinfo(f).file_size for f in file_list)
                compressed_size = sum(zipf.getinfo(f).compress_size for f in file_list)
                
                return {
                    "file_count": len(file_list),
                    "total_size": total_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compressed_size / total_size if total_size > 0 else 0,
                    "files": file_list
                }
                
        except Exception as e:
            logger.error(f"获取zip信息失败 {zip_path}: {str(e)}")
            return None
    
    @staticmethod
    def create_zip_from_file_list(file_list: List[tuple], output_zip: str) -> bool:
        """
        从文件列表直接创建zip包
        
        Args:
            file_list: 文件列表，格式为[(文件路径, 在zip中的路径), ...]
            output_zip: 输出的zip文件路径
        """
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, arcname in file_list:
                    if os.path.exists(file_path):
                        zipf.write(file_path, arcname)
                    else:
                        logger.warning(f"文件不存在，跳过: {file_path}")
            
            logger.info(f"从文件列表成功创建压缩包: {output_zip}")
            return True
            
        except Exception as e:
            logger.error(f"从文件列表创建压缩包失败: {str(e)}")
            return False