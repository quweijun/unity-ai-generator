from app.services.unity_rag_system import UnityRAGSystem
import asyncio

async def init_rag_system():
    rag = UnityRAGSystem('/content/unity-ai-generator/unity_projects/ShootBubble/')
    await rag.initialize()
    #rag.reinitialize()
    print('✅ Unity RAG系统就绪')
    rag_system = asyncio.get_event_loop().run_until_complete(init_rag_system())


try:
    # 方法1：使用现有事件循环
    import nest_asyncio
    nest_asyncio.apply()
    rag_system = asyncio.run(init_rag_system())
except RuntimeError:
    print(f"start app fail")
#     # 方法2：在已有事件循环中运行
#     rag_system = asyncio.get_event_loop().run_until_complete(init_rag_system())