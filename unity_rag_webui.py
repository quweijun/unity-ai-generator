import gradio as gr
import asyncio
import nest_asyncio
import traceback
from app.services.unity_rag_system import UnityRAGSystem

# 允许在 Jupyter / Colab 环境中重复使用事件循环
nest_asyncio.apply()

PROJECT_PATH = "/content/unity-ai-generator/unity_projects/ShootBubble/"

class UnityRAGWebUI:
    def __init__(self):
        self.rag_system = None
        self.is_initialized = False
        self.initialization_status = "未初始化"
    
    async def initialize_system(self):
        """初始化RAG系统"""
        try:
            self.initialization_status = "正在初始化..."
            print("🟢 开始初始化 UnityRAGSystem ...")
            
            self.rag_system = UnityRAGSystem(PROJECT_PATH)
            await self.rag_system.initialize()
            
            self.is_initialized = True
            self.initialization_status = "✅ 系统就绪"
            print("✅ Unity RAG系统就绪")
            return self.initialization_status, "系统初始化成功！可以开始提问了。"
            
        except Exception as e:
            error_msg = f"初始化失败: {str(e)}"
            self.initialization_status = "❌ 初始化失败"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return self.initialization_status, error_msg
    
    async def ask_question(self, question, history):
        """处理用户提问"""
        if not self.is_initialized or self.rag_system is None:
            return "请先初始化系统！", history
        
        if not question.strip():
            return "请输入问题！", history
        
        try:
            # 添加到历史记录
            history.append([question, ""])
            
            # 获取回答
            answer = await self.rag_system.ask_about_unity_project(question)
            
            # 更新历史记录
            history[-1][1] = answer
            
            return "", history
            
        except Exception as e:
            error_msg = f"回答问题时出错: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            history[-1][1] = error_msg
            return "", history
    
    def clear_chat(self):
        """清空聊天记录"""
        return []
    
    def get_system_info(self):
        """获取系统信息"""
        info = f"""
## Unity RAG 系统信息

**项目路径**: {PROJECT_PATH}
**系统状态**: {self.initialization_status}
**初始化状态**: {'✅ 已初始化' if self.is_initialized else '❌ 未初始化'}

### 功能说明：
1. 点击「初始化系统」按钮加载Unity项目
2. 在下方输入问题并发送
3. 系统将基于Unity项目代码和文档进行回答

### 示例问题：
- 这个游戏的主要目标是什么？
- 玩家点击气泡后会发生什么？
- Unity中控制发射泡泡的脚本是哪个？
- 这个游戏代码有什么地方需要优化？
        """
        return info

# 创建UI实例
ui_manager = UnityRAGWebUI()

def create_gradio_interface():
    """创建Gradio界面"""
    
    with gr.Blocks(
        title="Unity RAG 测试系统",
        theme=gr.themes.Soft(),
        css="""
        .chat-container { max-height: 500px; overflow-y: auto; }
        .system-info { background-color: #f0f8ff; padding: 15px; border-radius: 10px; }
        """
    ) as demo:
        
        gr.Markdown("# 🎮 Unity RAG 系统测试界面")
        gr.Markdown("基于Unity项目的智能问答系统")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 系统信息区域
                gr.Markdown("## 系统控制")
                
                init_btn = gr.Button("🚀 初始化系统", variant="primary")
                init_status = gr.Textbox(
                    label="初始化状态",
                    value=ui_manager.initialization_status,
                    interactive=False
                )
                init_output = gr.Textbox(
                    label="初始化输出",
                    interactive=False,
                    lines=3
                )
                
                # 系统信息显示
                system_info = gr.Markdown(ui_manager.get_system_info())
                
                clear_btn = gr.Button("🗑️ 清空对话", variant="secondary")
                
            with gr.Column(scale=2):
                # 聊天区域
                gr.Markdown("## 💬 问答对话")
                
                chatbot = gr.Chatbot(
                    label="Unity RAG 对话",
                    height=400,
                    show_copy_button=True
                )
                
                with gr.Row():
                    question_input = gr.Textbox(
                        label="输入您的问题",
                        placeholder="请输入关于Unity项目的问题...",
                        lines=2,
                        scale=4
                    )
                    submit_btn = gr.Button("发送", variant="primary", scale=1)
                
                examples = gr.Examples(
                    examples=[
                        "这个游戏的主要目标是什么？",
                        "玩家点击气泡后会发生什么？",
                        "Unity中控制发射泡泡的脚本是哪个？",
                        "这个游戏代码有什么地方需要优化？"
                    ],
                    inputs=question_input,
                    label="示例问题"
                )
        
        # 事件处理
        init_btn.click(
            fn=ui_manager.initialize_system,
            outputs=[init_status, init_output]
        ).then(
            fn=ui_manager.get_system_info,
            outputs=system_info
        )
        
        # 提问处理
        submit_btn.click(
            fn=ui_manager.ask_question,
            inputs=[question_input, chatbot],
            outputs=[question_input, chatbot]
        )
        
        # 回车键提交
        question_input.submit(
            fn=ui_manager.ask_question,
            inputs=[question_input, chatbot],
            outputs=[question_input, chatbot]
        )
        
        # 清空对话
        clear_btn.click(
            fn=ui_manager.clear_chat,
            outputs=chatbot
        )
        
        # 初始化完成后更新信息
        init_btn.click(
            fn=ui_manager.get_system_info,
            outputs=system_info
        )
    
    return demo

# 启动函数
def launch_web_ui(share=True, inbrowser=True):
    """启动Web UI"""
    print("🚀 启动 Unity RAG Web 界面...")
    demo = create_gradio_interface()
    demo.launch(
        share=share,
        inbrowser=inbrowser,
        show_error=True
    )

# 直接运行测试
if __name__ == "__main__":
    # 创建并启动界面
    demo = create_gradio_interface()
    
    # 在Colab中运行时设置share=True
    try:
        import google.colab
        in_colab = True
    except:
        in_colab = False
    
    demo.launch(
        share=in_colab,
        inbrowser=not in_colab,
        server_name="0.0.0.0" if in_colab else None,
        server_port=7860,
        show_error=True
    )