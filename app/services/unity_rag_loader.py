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
            '.asset': 'asset_binary',  # 标记为二进制文件
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
            '*.rar', '*.7z', '*.dll', '*.exe', '*.so', '*.dylib',
            '*.fbx', '*.obj', '*.blend', '*.max', '*.mb', '*.ma',  # 3D模型
            '*.png', '*.jpg', '*.jpeg', '*.tga', '*.psd', '*.bmp',  # 图片
            '*.wav', '*.mp3', '*.ogg', '*.aiff',  # 音频
            '*.ttf', '*.otf',  # 字体
        }
        
        # 二进制文件扩展名（不尝试用文本方式读取）
        self.binary_extensions = {
            '.asset', '.controller', '.anim'
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
        documents.extend(self._load_project_settings_safe())  # 使用安全版本
        documents.extend(self._load_packages_info())
        
        print(f"🎉 Unity项目加载完成: {len(documents)} 个文档")
        return documents
    
    # def _load_project_settings_safe(self) -> List[Dict]:
    #     """安全加载项目设置文件（处理二进制文件）"""
    #     print("  ⚙️ 安全加载项目设置...")
    #     settings_path = self.project_path / 'ProjectSettings'
    #     if not settings_path.exists():
    #         return []
        
    #     documents = []
    #     setting_files = list(settings_path.glob('*'))
        
    #     for setting_file in setting_files:
    #         if setting_file.is_file() and not self._should_exclude_file(setting_file):
    #             try:
    #                 # 检查文件扩展名
    #                 if setting_file.suffix in self.binary_extensions:
    #                     # 二进制文件，使用特殊处理
    #                     content = self._load_binary_file_summary(setting_file)
    #                     file_type = 'project_setting_binary'
    #                 else:
    #                     # 文本文件，正常读取
    #                     with open(setting_file, 'r', encoding='utf-8') as f:
    #                         content = f.read().strip()
    #                     file_type = 'project_setting'
                    
    #                 if content and len(content) > 10:
    #                     doc = self._create_document(
    #                         content=content,
    #                         file_path=setting_file,
    #                         file_type=file_type,
    #                         additional_metadata={
    #                             'setting_type': setting_file.name,
    #                             'is_binary': setting_file.suffix in self.binary_extensions
    #                         }
    #                     )
    #                     documents.append(doc)
    #                     print(f"    ✅ 加载: {setting_file.name}")
                    
    #             except Exception as e:
    #                 print(f"    ⚠️ 加载项目设置失败 {setting_file.name}: {e}")
        
    #     print(f"  ✅ 安全加载 {len(documents)} 个项目设置文件")
    #     return documents
    # 在 _load_project_settings_safe 方法中修改
    def _load_project_settings_safe(self) -> List[Dict]:
        """安全加载项目设置文件（跳过二进制文件）"""
        print("  ⚙️ 安全加载项目设置...")
        settings_path = self.project_path / 'ProjectSettings'
        if not settings_path.exists():
            return []
        
        documents = []
        setting_files = list(settings_path.glob('*'))
        
        # 只处理文本格式的设置文件
        text_settings = {
            'Packages/manifest.json',
            'ProjectSettings/ProjectVersion.txt',
            'ProjectSettings/BurstAotSettings_*.json',
            'ProjectSettings/ScriptableBuildPipeline.json'
        }
        
        for setting_file in setting_files:
            if setting_file.is_file() and not self._should_exclude_file(setting_file):
                # 跳过二进制文件
                if setting_file.suffix in self.binary_extensions:
                    print(f"    ⏭️  跳过二进制文件: {setting_file.name}")
                    continue
                    
                try:
                    with open(setting_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    if content and len(content) > 10:
                        doc = self._create_document(
                            content=content,
                            file_path=setting_file,
                            file_type='project_setting',
                            additional_metadata={
                                'setting_type': setting_file.name
                            }
                        )
                        documents.append(doc)
                        print(f"    ✅ 加载: {setting_file.name}")
                    
                except Exception as e:
                    print(f"    ⚠️ 加载项目设置失败 {setting_file.name}: {e}")
        
        print(f"  ✅ 安全加载 {len(documents)} 个项目设置文件")
        return documents
        
    def _load_binary_file_summary(self, file_path: Path) -> str:
        """为二进制文件生成摘要信息"""
        try:
            file_size = file_path.stat().st_size
            
            # 尝试读取文件头来识别文件类型
            with open(file_path, 'rb') as f:
                header = f.read(100)  # 读取前100字节
            
            # 分析文件头
            file_info = self._analyze_binary_header(header, file_path)
            
            summary = f"""
二进制文件摘要:
- 文件名: {file_path.name}
- 文件大小: {file_size} 字节
- 文件类型: {file_info.get('type', '未知')}
- 可能的格式: {file_info.get('format', '未知')}
- Unity GUID: {self.meta_cache.get(str(file_path), {}).get('guid', '未知')}

此文件是Unity二进制格式，包含项目设置信息。
无法直接以文本形式读取，但可以在Unity编辑器中查看和编辑。
"""
            return summary
            
        except Exception as e:
            return f"二进制文件处理失败: {str(e)}"
    
    def _analyze_binary_header(self, header: bytes, file_path: Path) -> Dict:
        """分析二进制文件头"""
        file_info = {'type': 'Unity二进制文件', 'format': 'YAML序列化'}
        
        # 尝试检测文件类型
        if header.startswith(b'%YAML'):
            file_info['format'] = 'YAML文本'
        elif b'Unity' in header:
            file_info['type'] = 'Unity序列化文件'
        
        # 根据文件名猜测内容
        filename = file_path.name.lower()
        if 'input' in filename:
            file_info['content'] = '输入设置'
        elif 'quality' in filename:
            file_info['content'] = '质量设置'
        elif 'graphics' in filename:
            file_info['content'] = '图形设置'
        elif 'audio' in filename:
            file_info['content'] = '音频设置'
        elif 'physics' in filename:
            file_info['content'] = '物理设置'
        elif 'time' in filename:
            file_info['content'] = '时间设置'
        elif 'tag' in filename:
            file_info['content'] = '标签和层设置'
        elif 'editor' in filename:
            file_info['content'] = '编辑器设置'
        
        return file_info
    
    def _load_file_content(self, file_path: Path) -> str:
        """安全加载文件内容"""
        try:
            # 检查是否为二进制文件
            if file_path.suffix in self.binary_extensions:
                return self._load_binary_file_summary(file_path)
            
            # 尝试UTF-8编码
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 过滤空文件或太小的文件
            if len(content) < 10:
                return None
                
            return content
            
        except UnicodeDecodeError:
            # UTF-8失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read().strip()
                return f"⚠️ 文件使用非UTF-8编码(latin-1):\n{content}"
            except:
                # 如果还是失败，返回二进制摘要
                return self._load_binary_file_summary(file_path)
        except Exception as e:
            return f"文件读取失败: {str(e)}"
    
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
        
        # 排除过大的文件（>10MB）
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                return True
        except:
            pass
        
        return False

    # 其他方法保持不变...
    def _preload_meta_files(self):
        """预加载.meta文件到缓存"""
        print("📋 预加载.meta文件...")
        meta_files = list(self.project_path.rglob('*.meta'))
        
        for meta_file in meta_files:
            try:
                asset_file = meta_file.with_suffix('')  # 移除.meta后缀
                if asset_file.exists():
                    with open(meta_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    self.meta_cache[str(asset_file)] = self._parse_meta_file(content)
            except Exception as e:
                print(f"⚠️ 加载meta文件失败 {meta_file}: {e}")
    
    def _parse_meta_file(self, meta_content: str) -> Dict:
        """解析Unity .meta文件"""
        try:
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
                content = self._load_file_content(code_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
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
      
    def _load_scene_files(self, base_path: Path) -> List[Dict]:
        """加载场景文件"""
        print("  🎭 加载场景文件...")
        scene_files = list(base_path.rglob('*.unity'))
        documents = []
        
        for scene_file in scene_files:
            if self._should_exclude_file(scene_file):
                continue
                
            try:
                content = self._load_file_content(scene_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
                    # 分析场景文件
                    analysis = self._analyze_scene_file(content, scene_file)
                    
                    doc = self._create_document(
                        content=content,
                        file_path=scene_file,
                        file_type='scene',
                        additional_metadata={
                            'scene_name': analysis.get('scene_name', 'Unknown'),
                            'game_objects_count': analysis.get('game_objects_count', 0),
                            'components_count': analysis.get('components_count', 0)
                        }
                    )
                    documents.append(doc)
                    
            except Exception as e:
                print(f"  ⚠️ 加载场景文件失败 {scene_file}: {e}")
        
        print(f"  ✅ 加载 {len(documents)} 个场景文件")
        return documents
    
    def _load_prefab_files(self, base_path: Path) -> List[Dict]:
        """加载预制体文件"""
        print("  🔧 加载预制体文件...")
        prefab_files = list(base_path.rglob('*.prefab'))
        documents = []
        
        for prefab_file in prefab_files:
            if self._should_exclude_file(prefab_file):
                continue
                
            try:
                content = self._load_file_content(prefab_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
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
                content = self._load_file_content(shader_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
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
                content = self._load_file_content(config_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
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
                content = self._load_file_content(doc_file)
                if content and "文件读取失败" not in content and "二进制文件" not in content:
                    doc = self._create_document(content, doc_file, 'document')
                    documents.append(doc)
            except Exception as e:
                print(f"  ⚠️ 加载文档失败 {doc_file}: {e}")
        
        return documents
    
    def _analyze_scene_file(self, content: str, file_path: Path) -> Dict:
        """分析Unity场景文件"""
        # Unity场景文件是YAML格式
        lines = content.split('\n')
        game_objects = 0
        components = 0
        scene_name = file_path.stem
        
        for line in lines:
            if line.strip().startswith('GameObject:'):
                game_objects += 1
            if line.strip().startswith('m_Component:'):
                components += 1
        
        return {
            'scene_name': scene_name,
            'game_objects_count': game_objects,
            'components_count': components
        }