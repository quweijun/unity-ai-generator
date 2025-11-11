# app/services/unity_rag_loader.py
import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Set
import hashlib

class UnityRAGLoader:
    def __init__(self, unity_project_path: str):
        self.project_path = Path(unity_project_path)
        self.meta_cache = {}
        
        # Unity特定文件扩展名
        self.unity_extensions = {
            '.cs': 'code',
            '.unity': 'scene',
            '.prefab': 'prefab', 
            '.mat': 'material',
            '.asset': 'asset',
            '.controller': 'animator',
            '.anim': 'animation',
            '.shader': 'shader',
            '.cginc': 'shader_include',
            '.hlsl': 'shader_code',
            '.json': 'config',
            '.xml': 'config',
            '.txt': 'document',
            '.md': 'document',
            '.yml': 'config',
            '.yaml': 'config'
        }
        
        # 需要排除的目录
        self.exclude_dirs = {
            'Library', 'Temp', 'Build', 'Logs', 'Obj', 'Builds',
            '__pycache__', '.git', 'node_modules', '.vs', '.idea'
        }
        
        # 需要排除的文件模式
        self.exclude_files = {
            '*.meta', '*.tmp', '*.bak', '*.unitypackage', '*.zip',
            '*.rar', '*.7z', '*.dll', '*.exe', '*.so', '*.dylib'
        }
    
    def load_unity_project(self) -> List[Dict[str, Any]]:
        """加载整个Unity项目"""
        documents = []
        
        print("🎮 开始加载Unity项目...")
        print(f"📁 项目路径: {self.project_path}")
        
        # 预加载.meta文件缓存
        self._preload_meta_files()
        
        # 加载各个重要目录
        documents.extend(self._load_assets_directory())
        documents.extend(self._load_project_settings())
        documents.extend(self._load_packages_info())
        
        print(f"🎉 Unity项目加载完成: {len(documents)} 个文档")
        return documents
    
    def _preload_meta_files(self):
        """预加载.meta文件到缓存"""
        print("📋 预加载.meta文件...")
        meta_files = list(self.project_path.rglob('*.meta'))
        
        for meta_file in meta_files:
            try:
                asset_file = meta_file.with_suffix('')  # 移除.meta后缀
                if asset_file.exists():
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.meta_cache[str(asset_file)] = self._parse_meta_file(content)
            except Exception as e:
                print(f"⚠️ 加载meta文件失败 {meta_file}: {e}")
    
    def _parse_meta_file(self, meta_content: str) -> Dict:
        """解析Unity .meta文件"""
        try:
            # 简单的YAML解析（Unity meta文件是YAML格式）
            lines = meta_content.split('\n')
            guid = None
            file_format = None
            
            for line in lines:
                if line.strip().startswith('guid:'):
                    guid = line.split(':', 1)[1].strip()
                elif line.strip().startswith('fileFormatVersion:'):
                    file_format = line.split(':', 1)[1].strip()
            
            return {
                'guid': guid,
                'file_format_version': file_format
            }
        except:
            return {}
    
    def _load_assets_directory(self) -> List[Dict]:
        """加载Assets目录"""
        assets_path = self.project_path / 'Assets'
        if not assets_path.exists():
            print("⚠️ Assets目录不存在")
            return []
        
        print("📁 加载Assets目录...")
        documents = []
        
        # 按文件类型分别处理
        documents.extend(self._load_code_files(assets_path))
        documents.extend(self._load_scene_files(assets_path))
        documents.extend(self._load_prefab_files(assets_path))
        documents.extend(self._load_shader_files(assets_path))
        documents.extend(self._load_config_files(assets_path))
        documents.extend(self._load_other_assets(assets_path))
        
        return documents
    
    def _load_code_files(self, base_path: Path) -> List[Dict]:
        """加载C#脚本文件"""
        print("  📝 加载C#脚本...")
        code_files = list(base_path.rglob('*.cs'))
        documents = []
        
        for code_file in code_files:
            if self._should_exclude_file(code_file):
                continue
                
            try:
                with open(code_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析C#文件结构
                analysis = self._analyze_csharp_file(content, code_file)
                
                doc = self._create_document(
                    content=content,
                    file_path=code_file,
                    file_type='code',
                    additional_metadata={
                        'class_name': analysis.get('main_class'),
                        'methods_count': len(analysis.get('methods', [])),
                        'dependencies': analysis.get('dependencies', []),
                        'complexity': analysis.get('complexity', 'unknown')
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载C#文件失败 {code_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个C#脚本")
        return documents
    
    def _analyze_csharp_file(self, content: str, file_path: Path) -> Dict:
        """分析C#文件结构"""
        lines = content.split('\n')
        classes = []
        methods = []
        dependencies = []
        usings = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检测using语句
            if line_stripped.startswith('using ') and line_stripped.endswith(';'):
                usings.append(line_stripped)
                # 提取依赖
                if 'UnityEngine' in line_stripped:
                    dependencies.append('UnityEngine')
                if 'System.' in line_stripped:
                    dependencies.append('System')
            
            # 检测类定义
            if line_stripped.startswith('public class ') or line_stripped.startswith('class '):
                class_name = line_stripped.split(' ')[-1].split(':')[0].split('<')[0]
                classes.append(class_name)
            
            # 检测方法定义
            if (line_stripped.startswith('public ') or 
                line_stripped.startswith('private ') or 
                line_stripped.startswith('protected ') or
                line_stripped.startswith('void ')) and '(' in line and ')' in line:
                method_name = line_stripped.split('(')[0].split(' ')[-1]
                methods.append(method_name)
        
        return {
            'main_class': classes[0] if classes else None,
            'classes': classes,
            'methods': methods,
            'dependencies': dependencies,
            'usings': usings,
            'complexity': self._assess_complexity(len(methods), len(classes))
        }
    
    def _assess_complexity(self, method_count: int, class_count: int) -> str:
        """评估代码复杂度"""
        if method_count > 20 or class_count > 3:
            return 'high'
        elif method_count > 10:
            return 'medium'
        else:
            return 'low'
    
    def _load_scene_files(self, base_path: Path) -> List[Dict]:
        """加载场景文件"""
        print("  🎭 加载场景文件...")
        scene_files = list(base_path.rglob('*.unity'))
        documents = []
        
        for scene_file in scene_files:
            if self._should_exclude_file(scene_file):
                continue
                
            try:
                with open(scene_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析场景文件
                analysis = self._analyze_scene_file(content, scene_file)
                
                doc = self._create_document(
                    content=content,
                    file_path=scene_file,
                    file_type='scene',
                    additional_metadata={
                        'game_objects_count': analysis.get('game_objects_count', 0),
                        'components_count': analysis.get('components_count', 0),
                        'scene_name': analysis.get('scene_name', 'Unknown')
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载场景文件失败 {scene_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个场景文件")
        return documents
    
    def _analyze_scene_file(self, content: str, file_path: Path) -> Dict:
        """分析Unity场景文件"""
        # Unity场景文件是YAML格式
        lines = content.split('\n')
        game_objects = 0
        components = 0
        scene_name = file_path.stem
        
        for line in lines:
            if line.strip().startswith('gameObject:'):
                game_objects += 1
            if line.strip().startswith('m_Component:'):
                components += 1
        
        return {
            'scene_name': scene_name,
            'game_objects_count': game_objects,
            'components_count': components
        }
    
    def _load_prefab_files(self, base_path: Path) -> List[Dict]:
        """加载预制体文件"""
        print("  🔧 加载预制体文件...")
        prefab_files = list(base_path.rglob('*.prefab'))
        documents = []
        
        for prefab_file in prefab_files:
            if self._should_exclude_file(prefab_file):
                continue
                
            try:
                with open(prefab_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = self._create_document(
                    content=content,
                    file_path=prefab_file,
                    file_type='prefab',
                    additional_metadata={
                        'prefab_name': prefab_file.stem
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载预制体失败 {prefab_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个预制体")
        return documents
    
    def _load_shader_files(self, base_path: Path) -> List[Dict]:
        """加载Shader文件"""
        print("  🌈 加载Shader文件...")
        shader_extensions = ['.shader', '.cginc', '.hlsl']
        shader_files = []
        
        for ext in shader_extensions:
            shader_files.extend(list(base_path.rglob(f'*{ext}')))
        
        documents = []
        
        for shader_file in shader_files:
            if self._should_exclude_file(shader_file):
                continue
                
            try:
                with open(shader_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = self._create_document(
                    content=content,
                    file_path=shader_file,
                    file_type='shader',
                    additional_metadata={
                        'shader_name': shader_file.stem,
                        'shader_type': shader_file.suffix[1:]
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载Shader失败 {shader_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个Shader文件")
        return documents
    
    def _load_config_files(self, base_path: Path) -> List[Dict]:
        """加载配置文件"""
        print("  ⚙️ 加载配置文件...")
        config_extensions = ['.json', '.xml', '.yml', '.yaml', '.txt']
        config_files = []
        
        for ext in config_extensions:
            config_files.extend(list(base_path.rglob(f'*{ext}')))
        
        documents = []
        
        for config_file in config_files:
            if self._should_exclude_file(config_file):
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                doc = self._create_document(
                    content=content,
                    file_path=config_file,
                    file_type='config'
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载配置文件失败 {config_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个配置文件")
        return documents
    
    def _load_other_assets(self, base_path: Path) -> List[Dict]:
        """加载其他资源文件"""
        print("  📦 加载其他资源文件...")
        documents = []
        
        # 加载文档文件
        doc_files = list(base_path.rglob('*.md'))
        for doc_file in doc_files:
            if self._should_exclude_file(doc_file):
                continue
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                doc = self._create_document(content, doc_file, 'document')
                documents.append(doc)
            except Exception as e:
                print(f"  ⚠️ 加载文档失败 {doc_file}: {e}")
        
        return documents
    
    def _load_project_settings(self) -> List[Dict]:
        """加载项目设置文件"""
        print("  ⚙️ 加载项目设置...")
        settings_path = self.project_path / 'ProjectSettings'
        if not settings_path.exists():
            return []
        
        documents = []
        setting_files = list(settings_path.glob('*'))
        
        for setting_file in setting_files:
            if setting_file.is_file() and not self._should_exclude_file(setting_file):
                try:
                    with open(setting_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = self._create_document(
                        content=content,
                        file_path=setting_file,
                        file_type='project_setting',
                        additional_metadata={
                            'setting_type': setting_file.name
                        }
                    )
                    documents.append(doc)
                    
                except Exception as e:
                    print(f"  ⚠️ 加载项目设置失败 {setting_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个项目设置文件")
        return documents
    
    def _load_packages_info(self) -> List[Dict]:
        """加载包信息"""
        print("  📦 加载包信息...")
        packages_file = self.project_path / 'Packages' / 'manifest.json'
        documents = []
        
        if packages_file.exists():
            try:
                with open(packages_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析包信息
                packages_data = json.loads(content)
                dependencies = packages_data.get('dependencies', {})
                
                doc = self._create_document(
                    content=content,
                    file_path=packages_file,
                    file_type='packages',
                    additional_metadata={
                        'package_count': len(dependencies),
                        'packages': list(dependencies.keys())[:10]  # 前10个包
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ 加载包信息失败 {packages_file}: {e}")
        
        print(f"  ✅ 加载包信息完成")
        return documents
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """判断是否应该排除文件"""
        # 检查目录
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return True
        
        # 检查文件模式
        for pattern in self.exclude_files:
            if file_path.match(pattern):
                return True
        
        return False
    
    def _create_document(self, content: str, file_path: Path, file_type: str, 
                        additional_metadata: Dict = None) -> Dict:
        """创建文档对象"""
        relative_path = file_path.relative_to(self.project_path)
        
        # 基础元数据
        metadata = {
            'file_path': str(relative_path),
            'file_name': file_path.name,
            'file_extension': file_path.suffix,
            'file_type': file_type,
            'file_size': len(content),
            'lines_count': content.count('\n') + 1,
            'unity_guid': self.meta_cache.get(str(file_path), {}).get('guid')
        }
        
        # 添加额外元数据
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return {
            'id': hashlib.md5(f"{relative_path}".encode()).hexdigest(),
            'content': content,
            'metadata': metadata
        }