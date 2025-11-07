# 资源生成服务
import os
import aiofiles
from typing import List, Dict, Optional
import logging
from app.core.ali_client import AliClient

logger = logging.getLogger(__name__)

class AssetGenerator:
    def __init__(self):
        self.ali_client = AliClient()
        self.asset_descriptions = {
            "player": "游戏主角角色",
            "enemy": "敌人或障碍物", 
            "coin": "可收集的金币或物品",
            "background": "游戏背景",
            "platform": "平台或地面"
        }
    
    async def generate_project_assets(self, project_path: str, game_request: dict) -> Dict[str, List[str]]:
        """为项目生成所有必要的资源文件"""
        generated_assets = {}
        
        try:
            # 根据游戏类型生成相应的资源
            game_type = game_request.get("game_type", "general")
            asset_style = game_request.get("asset_style", "pixel_art")
            
            # 生成精灵图资源
            sprites = await self._generate_sprite_assets(project_path, game_type, asset_style)
            generated_assets["sprites"] = sprites
            
            # 生成UI资源
            ui_assets = await self._generate_ui_assets(project_path, game_type, asset_style)
            generated_assets["ui"] = ui_assets
            
            logger.info(f"成功生成 {len(sprites)} 个精灵图和 {len(ui_assets)} 个UI资源")
            
        except Exception as e:
            logger.error(f"资源生成失败: {str(e)}")
            # 创建占位符资源
            await self._create_placeholder_assets(project_path)
            generated_assets["sprites"] = ["placeholder.png"]
            generated_assets["ui"] = ["ui_placeholder.png"]
        
        return generated_assets
    
    async def _generate_sprite_assets(self, project_path: str, game_type: str, style: str) -> List[str]:
        """生成精灵图资源"""
        sprites_path = os.path.join(project_path, "Assets/Sprites")
        os.makedirs(sprites_path, exist_ok=True)
        
        generated_files = []
        
        # 根据游戏类型定义需要生成的精灵图
        sprite_definitions = self._get_sprite_definitions(game_type, style)
        
        for sprite_name, description in sprite_definitions.items():
            try:
                # 调用通义万相生成图片
                image_data = await self.ali_client.generate_image(
                    prompt=description,
                    size="256x256"  # 适合游戏精灵图的尺寸
                )
                
                # 保存图片文件
                filename = f"{sprite_name}.png"
                filepath = os.path.join(sprites_path, filename)
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(image_data)
                
                generated_files.append(filename)
                logger.info(f"成功生成精灵图: {filename}")
                
            except Exception as e:
                logger.warning(f"生成精灵图 {sprite_name} 失败: {str(e)}")
                # 创建占位符
                await self._create_sprite_placeholder(sprites_path, sprite_name)
                generated_files.append(f"{sprite_name}.png")
        
        return generated_files
    
    async def _generate_ui_assets(self, project_path: str, game_type: str, style: str) -> List[str]:
        """生成UI资源"""
        ui_path = os.path.join(project_path, "Assets/UI")
        os.makedirs(ui_path, exist_ok=True)
        
        ui_elements = [
            ("start_button", f"游戏开始按钮，{style}风格"),
            ("restart_button", f"重新开始按钮，{style}风格"), 
            ("score_panel", f"分数显示面板，{style}风格")
        ]
        
        generated_files = []
        
        for element_name, description in ui_elements:
            try:
                image_data = await self.ali_client.generate_image(
                    prompt=description,
                    size="512x128"  # UI元素通常需要不同的尺寸
                )
                
                filename = f"{element_name}.png"
                filepath = os.path.join(ui_path, filename)
                
                async with aiofiles.open(filepath, 'wb') as f:
                    await f.write(image_data)
                
                generated_files.append(filename)
                
            except Exception as e:
                logger.warning(f"生成UI元素 {element_name} 失败: {str(e)}")
                # 跳过UI资源生成，不是关键资源
        
        return generated_files
    
    def _get_sprite_definitions(self, game_type: str, style: str) -> Dict[str, str]:
        """根据游戏类型获取精灵图定义"""
        base_description = f"，{style}风格，游戏资源，透明背景"
        
        definitions = {
            "player": f"游戏主角角色{base_description}",
            "enemy": f"游戏敌人角色{base_description}",
            "coin": f"可收集的金币物品{base_description}",
        }
        
        # 根据游戏类型添加特定的精灵图
        if game_type == "2d_platformer":
            definitions.update({
                "platform": f"平台或地面{base_description}",
                "background": f"游戏背景{base_description}",
            })
        elif game_type == "shooter":
            definitions.update({
                "bullet": f"子弹或投射物{base_description}",
                "powerup": f"能量提升物品{base_description}",
            })
        elif game_type == "rpg":
            definitions.update({
                "npc": f"非玩家角色{base_description}",
                "item": f"游戏物品{base_description}",
            })
        
        return definitions
    
    async def _create_placeholder_assets(self, project_path: str):
        """创建占位符资源"""
        sprites_path = os.path.join(project_path, "Assets/Sprites")
        os.makedirs(sprites_path, exist_ok=True)
        
        placeholder_files = ["player.png", "enemy.png", "coin.png", "background.png"]
        
        for filename in placeholder_files:
            await self._create_sprite_placeholder(sprites_path, filename.replace('.png', ''))
    
    async def _create_sprite_placeholder(self, directory: str, sprite_name: str):
        """创建单个精灵图占位符"""
        from PIL import Image, ImageDraw
        import io
        
        # 创建简单的彩色占位图
        colors = {
            "player": (0, 120, 255),     # 蓝色
            "enemy": (255, 50, 50),      # 红色  
            "coin": (255, 215, 0),       # 金色
            "platform": (100, 200, 100), # 绿色
        }
        
        color = colors.get(sprite_name, (200, 200, 200))  # 默认灰色
        
        # 创建图像
        img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单形状
        if sprite_name == "player":
            draw.rectangle([16, 16, 48, 48], fill=color)
        elif sprite_name == "coin":
            draw.ellipse([16, 16, 48, 48], fill=color)
        else:
            draw.rectangle([8, 8, 56, 56], fill=color)
        
        # 保存图像
        filename = os.path.join(directory, f"{sprite_name}.png")
        img.save(filename, "PNG")
        
        logger.info(f"创建占位符资源: {sprite_name}.png")