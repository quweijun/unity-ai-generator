# app/services/unity_text_processor.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class UnityTextProcessor:
    def __init__(self):
        # 初始化嵌入模型
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ 嵌入模型初始化成功")
        except Exception as e:
            logger.error(f"❌ 嵌入模型初始化失败: {e}")
            self.embedding_model = None
        
        # 针对Unity代码的智能分割器
        self.code_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=[
                '\nclass ', '\npublic class ', '\n[System.Serializable]',
                '\npublic ', '\nprivate ', '\nprotected ', '\nvoid ',
                '\nfunction ', '\n#region ', '\n#endregion ', '\n// ----',
                '\n\n', '\n', ' ', ''
            ]
        )
        
        # 针对配置文件的通用分割器
        self.config_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
    
    def split_unity_documents(self, documents: List[Dict]) -> List[Dict]:
        """分割Unity文档"""
        chunks = []
        
        print("✂️ 开始分割Unity文档...")
        
        for doc in documents:
            content = doc['content']
            metadata = doc['metadata']
            file_type = metadata['file_type']
            
            try:
                if file_type == 'code':
                    code_chunks = self._split_code_file(content, metadata)
                    chunks.extend(code_chunks)
                elif file_type in ['scene', 'prefab']:
                    yaml_chunks = self._split_yaml_file(content, metadata)
                    chunks.extend(yaml_chunks)
                else:
                    # 通用分割
                    text_chunks = self.config_splitter.split_text(content)
                    for i, chunk in enumerate(text_chunks):
                        chunks.append(self._create_chunk(chunk, metadata, i))
                        
            except Exception as e:
                print(f"⚠️ 分割文档失败 {metadata['file_path']}: {e}")
        
        print(f"✅ 文档分割完成: {len(chunks)} 个块")
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """生成文本块的嵌入向量"""
        print("step1")
        if self.embedding_model is None:
            raise RuntimeError("嵌入模型未初始化，请安装: pip install sentence-transformers")
        
        texts = [chunk['content'] for chunk in chunks]
        print(f"🧠 为 {len(texts)} 个文本块生成嵌入向量...")
        
        try:
            embeddings = self.embedding_model.encode(
                texts, 
                show_progress_bar=True,
                batch_size=32,
                convert_to_numpy=True
            )
            print(f"✅ 嵌入向量生成完成: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ 生成嵌入向量失败: {e}")
            # 返回随机嵌入向量作为备选
            print("⚠️ 使用随机嵌入向量作为备选")
            return np.random.randn(len(texts), 384).astype('float32')
    
    def _split_code_file(self, content: str, metadata: Dict) -> List[Dict]:
        """分割代码文件"""
        chunks = []
        
        # 使用专门的分割器
        text_chunks = self.code_splitter.split_text(content)
        
        for i, chunk in enumerate(text_chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_type': 'code_block',
                'chunk_index': i,
                'block_type': self._detect_block_type(chunk)
            })
            
            chunks.append({
                'content': chunk,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def _split_yaml_file(self, content: str, metadata: Dict) -> List[Dict]:
        """分割YAML文件（场景、预制体）"""
        chunks = []
        lines = content.split('\n')
        
        current_chunk = []
        current_section = "header"
        
        for line in lines:
            # 检测新的YAML文档开始
            if line.strip() == '---' and current_chunk:
                # 保存当前块
                if len(current_chunk) > 3:  # 过滤太小的块
                    chunk_content = '\n'.join(current_chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        'chunk_type': 'yaml_document',
                        'section': current_section
                    })
                    chunks.append({
                        'content': chunk_content,
                        'metadata': chunk_metadata
                    })
                
                # 开始新块
                current_chunk = [line]
                current_section = "new_document"
            else:
                current_chunk.append(line)
                
                # 更新当前章节类型
                if line.strip().startswith('GameObject:'):
                    current_section = "game_object"
                elif line.strip().startswith('MonoBehaviour:'):
                    current_section = "component"
        
        # 处理最后一个块
        if current_chunk and len(current_chunk) > 3:
            chunk_content = '\n'.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_type': 'yaml_document',
                'section': current_section
            })
            chunks.append({
                'content': chunk_content,
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def _detect_block_type(self, chunk: str) -> str:
        """检测代码块类型"""
        lines = chunk.split('\n')
        first_line = lines[0].strip() if lines else ""
        
        if first_line.startswith('class '):
            return 'class_definition'
        elif first_line.startswith('public ') or first_line.startswith('private '):
            if '(' in first_line and ')' in first_line:
                return 'method_definition'
            else:
                return 'field_definition'
        elif first_line.startswith('void ') or first_line.startswith('IEnumerator '):
            return 'method_definition'
        elif first_line.startswith('using '):
            return 'using_directive'
        elif first_line.startswith('//') or first_line.startswith('/*'):
            return 'comment'
        else:
            return 'code_block'
    
    def _create_chunk(self, content: str, metadata: Dict, chunk_index: int) -> Dict:
        """创建文本块"""
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            'chunk_type': 'text_block',
            'chunk_index': chunk_index
        })
        
        return {
            'content': content,
            'metadata': chunk_metadata
        }