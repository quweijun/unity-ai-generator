from pydantic import BaseModel, Field
from typing import Optional, List

class GameGenerationRequest(BaseModel):
    """游戏生成请求模型"""
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="游戏描述，至少10个字符",
        examples=["创建一个2D平台跳跃游戏，玩家控制角色跳跃躲避障碍物，收集金币，到达终点"]
    )
    game_type: str = Field(
        ...,
        description="游戏类型",
        examples=["2d_platformer", "shooter", "rpg", "puzzle", "adventure"]
    )
    complexity: str = Field(
        default="simple",
        description="复杂度级别",
        examples=["simple", "medium", "complex"]
    )
    include_assets: bool = Field(
        default=True,
        description="是否包含生成的资源文件"
    )
    asset_style: Optional[str] = Field(
        default="pixel_art",
        description="资源风格",
        examples=["pixel_art", "cartoon", "realistic", "low_poly"]
    )

    class Config:
        schema_extra = {
            "example": {
                "description": "创建一个2D平台跳跃游戏，玩家控制角色跳跃躲避障碍物，收集金币",
                "game_type": "2d_platformer",
                "complexity": "simple",
                "include_assets": True,
                "asset_style": "pixel_art"
            }
        }