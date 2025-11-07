# 提示词构建器
class PromptBuilder:
    @staticmethod
    def build_unity_project_prompt(game_description: str) -> str:
        """构建Unity项目生成提示词"""
        return f"""
请为一个Unity游戏生成完整的项目结构和代码。

游戏描述：{game_description}

请按照以下要求生成：
1. 首先生成一个完整的Unity项目文件夹结构（树状图）
2. 然后为每个必要的C#脚本生成完整代码
3. 代码需要包含：
   - 必要的using语句
   - 清晰的类结构
   - [SerializeField]属性暴露Inspector变量
   - 完整的Unity生命周期方法
   - 基本的错误处理
   - 详细的注释

请按以下格式返回：
## 项目结构
项目根目录/
├── Assets/
│ ├── Scripts/
│ │ ├── PlayerController.cs
│ │ ├── GameManager.cs
│ │ └── ...
│ ├── Scenes/
│ │ └── Main.unity
│ └── ...
├── Packages/
└── ...

## 代码文件

### Assets/Scripts/PlayerController.cs
```csharp
// 详细的C#代码...
请确保所有代码都是完整且可运行的。
"""