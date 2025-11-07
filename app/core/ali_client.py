# 阿里云API客户端
import aiohttp
import json
from app.core.config import settings

class AliClient:
    def __init__(self):
        self.api_key = settings.ALI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_code(self, prompt: str) -> str:
        """调用通义千问-Coder生成代码"""
        data = {
            "model": settings.ALI_MODEL_CODER,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的Unity游戏开发工程师。请根据用户需求生成完整、可运行的Unity C#代码。代码要规范，包含必要的注释，使用Unity最佳实践。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "max_tokens": 4000,
                "temperature": 0.3
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.ALI_API_BASE}model/invoke",
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                return result["output"]["choices"][0]["message"]["content"]
    
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> bytes:
        """调用通义万相生成图片"""
        data = {
            "model": settings.ALI_MODEL_ART,
            "input": {
                "prompt": prompt,
                "size": size
            },
            "parameters": {
                "n": 1,
                "style": "digital_art"  # 适合游戏资源的风格
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.ALI_API_BASE}image/generation",
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                image_url = result["output"]["image_urls"][0]
                
                # 下载图片
                async with session.get(image_url) as img_response:
                    return await img_response.read()