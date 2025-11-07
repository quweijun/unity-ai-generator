# 代码生成服务

#### 4. 代码生成服务 (`app/services/code_generator.py`)

import re
from app.core.ali_client import AliClient
from app.core.prompt_builder import PromptBuilder

class CodeGenerator:
    def __init__(self):
        self.ali_client = AliClient()
    
    async def generate_unity_project(self, game_description: str) -> dict:
        """生成完整的Unity项目"""
        prompt = PromptBuilder.build_unity_project_prompt(game_description)
        response = await self.ali_client.generate_code(prompt)
        
        return self._parse_project_response(response)
    
    def _parse_project_response(self, response: str) -> dict:
        """解析模型响应，提取项目结构和代码"""
        project = {
            "structure": {},
            "files": {}
        }
        
        # 提取项目结构
        structure_match = re.search(r'```(?:\w+)?\n(.*?)\n```', response, re.DOTALL)
        if structure_match:
            project["structure"] = structure_match.group(1)
        
        # 提取代码文件
        code_blocks = re.findall(r'### (.*?\.cs)\n```csharp\n(.*?)\n```', response, re.DOTALL)
        for filename, code in code_blocks:
            project["files"][filename.strip()] = code.strip()
        
        return project