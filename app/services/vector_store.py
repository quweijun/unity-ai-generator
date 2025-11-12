# app/services/vector_store.py
import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化Chroma向量数据库"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = None
            logger.info(f"✅ Chroma客户端初始化成功: {persist_directory}")
        except Exception as e:
            logger.error(f"❌ Chroma初始化失败: {e}")
            raise
    
    def create_collection(self, collection_name: str = "unity_project"):
        """创建或获取集合"""
        try:
            # 尝试获取现有集合
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"✅ 加载现有集合: {collection_name}")
        except Exception:
            # 创建新集合
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Unity project code and documentation"}
            )
            logger.info(f"✅ 创建新集合: {collection_name}")
    
    # def add_documents(self, chunks: List[Dict], embeddings: np.ndarray):
    #     """添加文档到向量数据库"""
    #     if not self.collection:
    #         self.create_collection()
        
    #     logger.info("💾 保存文档到向量数据库...")
        
    #     documents = []
    #     metadatas = []
    #     ids = []
        
    #     for i, chunk in enumerate(chunks):
    #         # 限制文档长度，避免过长
    #         content = chunk['content']
    #         if len(content) > 10000:  # 限制最大长度
    #             content = content[:10000] + "\n... [内容截断]"
            
    #         documents.append(content)
    #         metadatas.append(chunk['metadata'])
            
    #         # 生成唯一ID
    #         file_path = chunk['metadata'].get('file_path', 'unknown')
    #         chunk_id = f"chunk_{i}_{hash(file_path) % 10000:04d}"
    #         ids.append(chunk_id)
        
    #     try:
    #         # 转换为列表格式
    #         embeddings_list = embeddings.tolist()
            
    #         self.collection.add(
    #             embeddings=embeddings_list,
    #             documents=documents,
    #             metadatas=metadatas,
    #             ids=ids
    #         )
            
    #         logger.info(f"🎉 向量数据库更新完成: {len(documents)} 个文档")
            
    #     except Exception as e:
    #         logger.error(f"❌ 添加文档到向量数据库失败: {e}")
    #         raise
    
    # def add_documents(self, chunks: List[Dict], embeddings: np.ndarray):
    #     """添加文档到向量数据库"""
    #     if not self.collection:
    #         self.create_collection()
        
    #     logger.info("💾 保存文档到向量数据库...")
        
    #     documents = []
    #     metadatas = []
    #     ids = []
        
    #     for i, chunk in enumerate(chunks):
    #         # 限制文档长度，避免过长
    #         content = chunk['content']
    #         if len(content) > 10000:  # 限制最大长度
    #             content = content[:10000] + "\n... [内容截断]"
            
    #         documents.append(content)
            
    #         # 清理metadata，确保只包含基本数据类型
    #         metadata = self._clean_metadata(chunk['metadata'])
    #         metadatas.append(metadata)
            
    #         # 生成唯一ID
    #         file_path = chunk['metadata'].get('file_path', 'unknown')
    #         chunk_id = f"chunk_{i}_{hash(file_path) % 10000:04d}"
    #         ids.append(chunk_id)
        
    #     try:
    #         # 转换为列表格式
    #         embeddings_list = embeddings.tolist()
            
    #         self.collection.add(
    #             embeddings=embeddings_list,
    #             documents=documents,
    #             metadatas=metadatas,
    #             ids=ids
    #         )
            
    #         logger.info(f"🎉 向量数据库更新完成: {len(documents)} 个文档")
            
    #     except Exception as e:
    #         logger.error(f"❌ 添加文档到向量数据库失败: {e}")
    #         raise
    def add_documents(self, chunks, embeddings):
        """添加文档块到向量数据库"""
        try:
            # 准备文档数据
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # 方法1：如果 chunk 是字典
                if isinstance(chunk, dict):
                    text = chunk.get('text', '') or chunk.get('content', '')
                    metadata = chunk.get('metadata', {})
                # 方法2：如果 chunk 有 text 属性
                elif hasattr(chunk, 'text'):
                    text = chunk.text
                    metadata = getattr(chunk, 'metadata', {})
                else:
                    logger.warning(f"⚠️ 无法处理的 chunk 类型: {type(chunk)}")
                    continue

                if not text:
                    logger.warning(f"⚠️ 跳过空文本的 chunk {i}")
                    continue

                #documents.append(chunk.text)
                documents.append(text)
                
                # 清理元数据，确保没有 None 值
                cleaned_metadata = {}
                #if (not isinstance(chunk, dict)) and hasattr(chunk, 'metadata'):
                if metadata:#chunk.metadata:
                    for key, value in metadata.items():#chunk.metadata.items():
                        if value is not None:
                            # 根据值的类型进行适当转换
                            if isinstance(value, (str, int, float, bool)):
                                cleaned_metadata[key] = value
                            else:
                                # 将其他类型转换为字符串
                                cleaned_metadata[key] = str(value)
                        else:
                            # 对于 None 值，提供默认值或跳过
                            cleaned_metadata[key] = ""  # 或者跳过这个字段
                    
                metadatas.append(cleaned_metadata)
                ids.append(f"chunk_{i}")
            
            # 转换为嵌入向量列表
            embeddings_list = embeddings.tolist()

            self.collection.add(
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ 成功添加 {len(documents)} 个文档到向量数据库")
            
        except Exception as e:
            logger.error(f"❌ 添加文档到向量数据库失败: {e}")
            raise

    def _clean_metadata(self, metadata: Dict) -> Dict:
        """清理metadata，确保只包含ChromaDB支持的数据类型"""
        cleaned = {}
        
        for key, value in metadata.items():
            if value is None:
                cleaned[key] = None
            elif isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, list):
                # 将列表转换为字符串
                cleaned[key] = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                # 将字典转换为JSON字符串
                import json
                try:
                    cleaned[key] = json.dumps(value)
                except:
                    cleaned[key] = str(value)
            else:
                # 其他类型转换为字符串
                cleaned[key] = str(value)
        
        return cleaned

        def search(self, query: str, n_results: int = 5, 
                  where_filter: Optional[Dict] = None) -> List[Dict]:
            """搜索相关文档"""
            if not self.collection:
                return []
            
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter
                )
                
                formatted_results = []
                if results['documents'] and len(results['documents'][0]) > 0:
                    for i in range(len(results['documents'][0])):
                        formatted_results.append({
                            'content': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'distance': results['distances'][0][i] if results['distances'] else 0,
                            'score': 1 - (results['distances'][0][i] if results['distances'] else 0)
                        })
                
                logger.info(f"🔍 搜索完成: 查询='{query}', 结果数={len(formatted_results)}")
                return formatted_results
                
            except Exception as e:
                logger.error(f"❌ 搜索失败: {e}")
                return []
        
    def search_by_embedding(self, embedding: np.ndarray, n_results: int = 5) -> List[Dict]:
        """通过嵌入向量搜索"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=n_results
            )
            
            formatted_results = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'score': 1 - results['distances'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ 向量搜索失败: {e}")
            return []
    
    def get_collection_info(self) -> Dict:
        """获取集合信息"""
        if not self.collection:
            return {}
        
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'name': self.collection.name,
                'persist_directory': self.persist_directory
            }
        except Exception as e:
            logger.error(f"❌ 获取集合信息失败: {e}")
            return {}
    
    def delete_collection(self, collection_name: str):
        """删除集合"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"🗑️ 删除集合: {collection_name}")
        except Exception as e:
            logger.error(f"❌ 删除集合失败: {e}")
    
    def list_collections(self) -> List[str]:
        """列出所有集合"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"❌ 列出集合失败: {e}")
            return []


# 简单的内存向量存储（备用方案）
class SimpleVectorStore:
    """简单的内存向量存储，用于测试或备选"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadatas = []
    
    def add_documents(self, chunks: List[Dict], embeddings: np.ndarray):
        """添加文档到内存存储"""
        self.documents = [chunk['content'] for chunk in chunks]
        self.metadatas = [chunk['metadata'] for chunk in chunks]
        self.embeddings = embeddings.tolist()
    
    def search(self, query: str, n_results: int = 5, where_filter: Optional[Dict] = None) -> List[Dict]:
        """简单搜索（基于关键词匹配）"""
        # 这里实现简单的关键词匹配
        # 实际使用时应该用真正的向量搜索
        query_lower = query.lower()
        results = []
        
        for i, doc in enumerate(self.documents):
            score = 0
            # 简单的关键词匹配评分
            for word in query_lower.split():
                if word in doc.lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'content': doc,
                    'metadata': self.metadatas[i],
                    'score': min(score / len(query.split()), 1.0)
                })
        
        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:n_results]