# app/services/unity_rag_system.py
from .unity_rag_loader import UnityRAGLoader
from .unity_text_processor import UnityTextProcessor
from .vector_store import ChromaVectorStore
import asyncio

class UnityRAGSystem:
    def __init__(self, unity_project_path: str):
        self.unity_project_path = unity_project_path
        self.loader = UnityRAGLoader(unity_project_path)
        self.processor = UnityTextProcessor()
        self.vector_store = ChromaVectorStore(persist_directory="./chroma_unity_db")
        self.is_initialized = False
    
    async def initialize(self):
        """初始化Unity RAG系统"""
        if self.is_initialized:
            return
        
        print("🚀 初始化Unity RAG系统...")
        
        # 1. 加载Unity项目
        documents = self.loader.load_unity_project()
        
        # 2. 分割文档
        chunks = self.processor.split_unity_documents(documents)
        
        # 3. 生成嵌入向量
        embeddings = self.processor.generate_embeddings(chunks)
        
        # 4. 保存到向量数据库
        self.vector_store.create_collection("unity_project")
        self.vector_store.add_documents(chunks, embeddings)
        
        self.is_initialized = True
        
        # 打印统计信息
        self._print_statistics(documents, chunks)
    
    def _print_statistics(self, documents: List[Dict], chunks: List[Dict]):
        """打印统计信息"""
        file_types = {}
        for doc in documents:
            file_type = doc['metadata']['file_type']
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        print("\n📊 Unity项目统计:")
        print(f"📁 总文件数: {len(documents)}")
        print(f"📄 总文本块数: {len(chunks)}")
        print("📋 文件类型分布:")
        for file_type, count in file_types.items():
            print(f"  - {file_type}: {count}")
    
    async def ask_about_unity_project(self, question: str, file_types: List[str] = None) -> Dict:
        """关于Unity项目的问答"""
        if not self.is_initialized:
            await self.initialize()
        
        # 构建过滤条件
        where_filter = None
        if file_types:
            where_filter = {"file_type": {"$in": file_types}}
        
        # 检索相关文档
        relevant_docs = self.vector_store.search(
            question, 
            n_results=10,
            where=where_filter
        )
        
        # 构建提示词
        prompt = self._build_unity_prompt(question, relevant_docs)
        
        # 调用大模型
        answer = await self._call_llm(prompt)
        
        return {
            'question': question,
            'answer': answer,
            'relevant_sources': [
                {
                    'file': doc['metadata']['file_path'],
                    'type': doc['metadata']['file_type'],
                    'score': doc['score'],
                    'context': doc['metadata'].get('block_type', '')
                }
                for doc in relevant_docs
            ]
        }
    
    def _build_unity_prompt(self, question: str, relevant_docs: List[Dict]) -> str:
        """构建Unity专用提示词"""
        
        context_parts = []
        for i, doc in enumerate(relevant_docs):
            metadata = doc['metadata']
            context_parts.append(f"""
            ## 来源 {i+1} [{metadata['file_type']}] (相关性: {doc['score']:.2f})
            **文件**: {metadata['file_path']}
            **类型**: {metadata['file_type']} / {metadata.get('block_type', 'N/A')}
            {class_info}

            ```{self._get_code_language(metadata['file_type'])}
            {doc['content'][:600]}
            """)

        context_str = '\n'.join(context_parts)
        
        prompt = f"""
        Unity项目智能分析
        项目上下文
        {context_str}

        用户问题
        {question}

        回答要求
        你是一个资深的Unity开发专家，基于以上Unity项目代码和资源文件回答用户问题。

        请重点关注：

        Unity最佳实践 - 性能优化、内存管理

        架构设计 - MonoBehaviour使用、组件通信

        资源管理 - 预制体、场景、材质的使用

        平台特性 - 移动端、PC端优化差异

        请提供具体、可操作的Unity开发建议。
        """
    return prompt

    def _get_code_language(self, file_type: str) -> str:
        """获取代码语言"""
        if file_type == 'code':
            return 'csharp'
        elif file_type in ['scene', 'prefab']:
            return 'yaml'
        elif file_type == 'shader':
            return 'hlsl'
        else:
            return 'text'

  
    ### 4. 使用示例

    ```python
    # 使用示例
    async def main():
        # 初始化Unity RAG系统
        unity_rag = UnityRAGSystem("/path/to/your/unity/project")
        await unity_rag.initialize()
        
        # 问答示例
        results = await unity_rag.ask_about_unity_project(
            "我的PlayerController脚本中Update方法性能有问题，如何优化？",
            file_types=['code']  # 只搜索代码文件
        )
        
        print("回答:", results['answer'])
        print("相关来源:")
        for source in results['relevant_sources']:
            print(f"- {source['file']} (分数: {source['score']:.2f})")

    # 运行
    if __name__ == "__main__":
        asyncio.run(main())
