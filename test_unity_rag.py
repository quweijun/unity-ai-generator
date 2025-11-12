"""
test_unity_rag.py
----------------------------------------
用于测试 UnityRAGSystem 初始化与问答功能
路径假设为：
/content/unity-ai-generator/app/services/unity_rag_system.py

运行方式：
  python test_unity_rag.py
或在 Colab 中：
  %run test_unity_rag.py
"""

import asyncio
import nest_asyncio
import traceback
from app.services.unity_rag_system import UnityRAGSystem

# 允许在 Jupyter / Colab 环境中重复使用事件循环
nest_asyncio.apply()

PROJECT_PATH = "/content/unity-ai-generator/unity_projects/ShootBubble/"

async def test_rag_system():
    print("🟢 开始初始化 UnityRAGSystem ...")
    rag = UnityRAGSystem(PROJECT_PATH)
    await rag.initialize()
    print("✅ Unity RAG系统就绪")

    # 测试问答
    test_questions = [
        "这个游戏的主要目标是什么？",
        "玩家点击气泡后会发生什么？",
        "Unity中控制发射泡泡的脚本是哪个？"
    ]

    for i, q in enumerate(test_questions, 1):
        print(f"\n🧠 测试问答 {i}: {q}")
        try:
            # 根据接口不同可改为 rag.ask(q) 或 rag.chat(q)
            answer = await rag.ask_about_unity_project(q)
            print(f"💬 回答: {answer}\n")
        except AttributeError:
            traceback.print_exc()
            print("❌ 找不到 rag.query() 方法，请检查类定义。")
            methods = [m for m in dir(rag) if not m.startswith("_")]
            print(f"可用方法：{methods}")
            break
        except Exception as e:
            print(f"⚠️ 调用时出错: {e}")
            break

    print("\n🎯 测试完成。")

# ---------------- 主入口 ----------------
if __name__ == "__main__":
    try:
        asyncio.run(test_rag_system())
    except RuntimeError:
        # Notebook / Colab 环境中重复事件循环时使用这种方式
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(test_rag_system())
