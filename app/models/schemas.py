# 数据模型
from pydantic import BaseModel
from typing import Optional, List

class GameGenerationRequest(BaseModel):
    description: str
    game_type: str
    complexity: str = "simple"
    include_assets: bool = True
    asset_style: Optional[str] = "pixel_art"