import os
import zipfile
from datetime import datetime
from app.services.code_generator import CodeGenerator
from app.services.asset_generator import AssetGenerator

class ProjectBuilder:
    def __init__(self):
        self.code_gen = CodeGenerator()
        self.asset_gen = AssetGenerator()
    
    async def create_unity_project(self, game_request: dict) -> str:
        """创建Unity项目并返回zip文件路径"""
        project_data = await self.code_gen.generate_unity_project(
            game_request["description"]
        )
        
        # 创建临时项目目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"UnityProject_{timestamp}"
        project_path = f"temp/{project_name}"
        
        os.makedirs(project_path, exist_ok=True)
        
        # 创建项目结构
        await self._build_project_structure(project_path, project_data, game_request)
        
        # 生成资源文件
        await self.asset_gen.generate_project_assets(project_path, game_request)
        
        # 创建zip包
        zip_path = f"temp/{project_name}.zip"
        self._create_zip_file(project_path, zip_path)
        
        return zip_path
    
    async def _build_project_structure(self, project_path: str, project_data: dict, game_request: dict):
        """构建项目文件结构"""
        # 创建基本Unity项目结构
        folders = [
            "Assets/Scripts",
            "Assets/Scenes", 
            "Assets/Sprites",
            "Assets/Audio",
            "Assets/Materials",
            "Packages",
            "ProjectSettings"
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # 写入代码文件
        for filepath, code in project_data["files"].items():
            full_path = os.path.join(project_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(code)
        
        # 创建基本的项目配置文件
        self._create_project_files(project_path, game_request)
    
    def _create_project_files(self, project_path: str, game_request: dict):
        """创建Unity项目必要的配置文件"""
        # manifest.json
        manifest = {
            "dependencies": {
                "com.unity.collab-proxy": "1.17.7",
                "com.unity.ide.rider": "3.0.16",
                "com.unity.ide.visualstudio": "2.0.16",
                "com.unity.test-framework": "1.1.33",
                "com.unity.textmeshpro": "3.0.6",
                "com.unity.timeline": "1.7.2",
                "com.unity.ugui": "1.0.0",
                "com.unity.modules.ai": "1.0.0",
                "com.unity.modules.androidjni": "1.0.0",
                "com.unity.modules.animation": "1.0.0",
                "com.unity.modules.assetbundle": "1.0.0",
                "com.unity.modules.audio": "1.0.0",
                "com.unity.modules.cloth": "1.0.0",
                "com.unity.modules.director": "1.0.0",
                "com.unity.modules.imageconversion": "1.0.0",
                "com.unity.modules.imgui": "1.0.0",
                "com.unity.modules.jsonserialize": "1.0.0",
                "com.unity.modules.particlesystem": "1.0.0",
                "com.unity.modules.physics": "1.0.0",
                "com.unity.modules.physics2d": "1.0.0",
                "com.unity.modules.screencapture": "1.0.0",
                "com.unity.modules.terrain": "1.0.0",
                "com.unity.modules.terrainphysics": "1.0.0",
                "com.unity.modules.tilemap": "1.0.0",
                "com.unity.modules.ui": "1.0.0",
                "com.unity.modules.uielements": "1.0.0",
                "com.unity.modules.umbra": "1.0.0",
                "com.unity.modules.unityanalytics": "1.0.0",
                "com.unity.modules.unitywebrequest": "1.0.0",
                "com.unity.modules.unitywebrequestassetbundle": "1.0.0",
                "com.unity.modules.unitywebrequestaudio": "1.0.0",
                "com.unity.modules.unitywebrequesttexture": "1.0.0",
                "com.unity.modules.unitywebrequestwww": "1.0.0",
                "com.unity.modules.vehicles": "1.0.0",
                "com.unity.modules.video": "1.0.0",
                "com.unity.modules.vr": "1.0.0",
                "com.unity.modules.wind": "1.0.0",
                "com.unity.modules.xr": "1.0.0"
            }
        }
        
        with open(os.path.join(project_path, "Packages/manifest.json"), 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
    
    def _create_zip_file(self, source_dir: str, output_path: str):
        """创建项目zip包"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)# 项目构建服务
