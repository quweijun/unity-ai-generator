import gradio as gr
import asyncio
import nest_asyncio
import traceback
import os
import warnings

# 过滤TensorFlow的警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

from app.services.unity_rag_system import UnityRAGSystem

# 允许在 Jupyter / Colab 环境中重复使用事件循环
nest_asyncio.apply()

PROJECT_PATH = "/content/unity-ai-generator/unity_projects/ShootBubble/"

class UnityRAGWebUI:
    def __init__(self):
        self.rag_system = None
        self.is_initialized = False
        self.initialization_status = "未初始化"
    
    async def initialize_system(self, progress=gr.Progress()):
        """初始化RAG系统"""
        try:
            self.initialization_status = "正在初始化..."
            progress(0.1, desc="开始初始化 UnityRAGSystem...")
            
            self.rag_system = UnityRAGSystem(PROJECT_PATH)
            progress(0.5, desc="加载项目文件...")
            
            await self.rag_system.initialize()
            progress(0.8, desc="构建索引...")
            
            self.is_initialized = True
            self.initialization_status = "✅ 系统就绪"
            progress(1.0, desc="初始化完成！")
            
            return self.initialization_status, "🎉 系统初始化成功！可以开始提问了。"
            
        except Exception as e:
            error_msg = f"❌ 初始化失败: {str(e)}"
            self.initialization_status = "❌ 初始化失败"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return self.initialization_status, error_msg
    
    async def ask_question(self, question, chat_history):
        """处理用户提问 - 修复格式问题"""
        if not self.is_initialized or self.rag_system is None:
            chat_history.append({"role": "user", "content": question})
            chat_history.append({"role": "assistant", "content": "请先初始化系统！"})
            return chat_history
        
        if not question.strip():
            chat_history.append({"role": "user", "content": question})
            chat_history.append({"role": "assistant", "content": "请输入有效的问题！"})
            return chat_history
        
        try:
            # 添加用户消息到历史
            chat_history.append({"role": "user", "content": question})
            
            # 获取回答（返回的是字典）
            response = await self.rag_system.ask_about_unity_project(question)
            
            # 提取纯文本回答
            if isinstance(response, dict):
                answer = self._format_response(response)
            else:
                answer = str(response)
            
            # 添加助手回答到历史
            chat_history.append({"role": "assistant", "content": answer})
            
            return chat_history
            
        except Exception as e:
            error_msg = f"❌ 回答问题时出错: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history
    
    def _format_response(self, response_dict):
        """格式化RAG系统返回的字典为可读文本"""
        try:
            # 提取主要信息
            question = response_dict.get('question', '')
            answer = response_dict.get('answer', '')
            relevant_sources = response_dict.get('relevant_sources', [])
            
            # 构建格式化响应
            formatted_response = f"**问题**: {question}\n\n"
            formatted_response += f"**回答**: {answer}\n\n"
            
            # 添加相关来源
            if relevant_sources:
                formatted_response += "**相关来源**:\n"
                for i, source in enumerate(relevant_sources[:5], 1):  # 只显示前5个
                    file_path = source.get('file', '未知文件')
                    score = source.get('score', 0)
                    file_type = source.get('type', '未知类型')
                    
                    formatted_response += f"{i}. `{file_path}` "
                    formatted_response += f"({file_type}, 相关性: {score:.3f})\n"
            
            return formatted_response
            
        except Exception as e:
            return f"格式化响应时出错: {str(e)}\n原始响应: {response_dict}"
    
    def clear_chat(self):
        """清空聊天记录"""
        return []
    
    def get_system_info(self):
        """获取系统信息"""
        info = f"""
## 🎮 Unity RAG 系统信息

**📁 项目路径**: `{PROJECT_PATH}`
**🔄 系统状态**: {self.initialization_status}
**✅ 初始化状态**: {'✅ 已初始化' if self.is_initialized else '❌ 未初始化'}

### 📋 功能说明：
1. 点击「🚀 初始化系统」按钮加载Unity项目
2. 在下方输入问题并发送
3. 系统将基于Unity项目代码和文档进行回答

### 💡 示例问题：
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
        .warning { color: #ff6b35; font-weight: bold; }
        .assistant-message { white-space: pre-wrap; }
        """
    ) as demo:
        
        gr.Markdown("# 🎮 Unity RAG 系统测试界面")
        gr.Markdown("基于Unity项目的智能问答系统")
        
        with gr.Row():
            with gr.Column(scale=1):
                # 系统信息区域
                gr.Markdown("## ⚙️ 系统控制")
                
                with gr.Group():
                    init_btn = gr.Button(
                        "🚀 初始化系统", 
                        variant="primary",
                        size="lg"
                    )
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
                
                # 警告信息
                gr.Markdown("""
                <div class="warning">
                ⚠️ 注意：上方的CUDA警告是正常的，不影响系统功能
                </div>
                """)
                
            with gr.Column(scale=2):
                # 聊天区域
                gr.Markdown("## 💬 问答对话")
                
                chatbot = gr.Chatbot(
                    label="Unity RAG 对话",
                    height=500,
                    show_copy_button=True,
                    type="messages",  # 使用新的消息格式
                    placeholder="系统初始化后可以开始对话...",
                    bubble_full_width=False
                )
                
                with gr.Row():
                    question_input = gr.Textbox(
                        label="输入您的问题",
                        placeholder="请输入关于Unity项目的问题...",
                        lines=2,
                        scale=4,
                        max_lines=3
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
                    label="💡 示例问题（点击快速输入）"
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
        def submit_question(question, history):
            return asyncio.run(ui_manager.ask_question(question, history))
        
        submit_btn.click(
            fn=submit_question,
            inputs=[question_input, chatbot],
            outputs=chatbot
        ).then(
            lambda: "",  # 清空输入框
            outputs=question_input
        )
        
        # 回车键提交
        question_input.submit(
            fn=submit_question,
            inputs=[question_input, chatbot],
            outputs=chatbot
        ).then(
            lambda: "",  # 清空输入框
            outputs=question_input
        )
        
        # 清空对话
        clear_btn.click(
            fn=ui_manager.clear_chat,
            outputs=chatbot
        )
    
    return demo

def launch_web_ui():
    """启动Web UI"""
    print("🚀 启动 Unity RAG Web 界面...")
    print("⚠️  忽略上方的CUDA警告，这是正常的TensorFlow/PyTorch初始化信息")
    
    demo = create_gradio_interface()
    
    # 检测运行环境
    try:
        import google.colab
        in_colab = True
        print("🌐 检测到Colab环境，生成公开链接...")
    except:
        in_colab = False
        print("💻 本地环境运行...")
    
    demo.launch(
        share=in_colab,
        inbrowser=not in_colab,
        server_name="0.0.0.0" if in_colab else "127.0.0.1",
        server_port=7860,
        show_error=True,
        quiet=True  # 减少控制台输出
    )

# 直接运行
if __name__ == "__main__":
    launch_web_ui()