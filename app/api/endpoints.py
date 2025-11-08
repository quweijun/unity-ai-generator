from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import asyncio
from datetime import datetime
import json
import shutil

# ！！！重要：必须先定义 router，然后才能使用装饰器！！！
router = APIRouter()

# 项目构建器类（简化版）
class ProjectBuilder:
    def __init__(self):
        self.temp_dir = "temp_projects"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def create_unity_project(self, request_data: dict) -> str:
        """创建Unity项目并返回zip文件路径"""
        try:
            # 生成项目名称和时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = f"UnityProject_{timestamp}"
            project_path = os.path.join(self.temp_dir, project_name)
            
            # 创建项目目录结构
            await self._create_project_structure(project_path, request_data)
            
            # 生成项目文件
            await self._generate_project_files(project_path, request_data)
            
            # 创建zip包
            zip_path = f"{project_path}.zip"
            await self._create_zip_file(project_path, zip_path)
            
            # 清理原始项目目录
            shutil.rmtree(project_path)
            
            return zip_path
            
        except Exception as e:
            raise Exception(f"项目创建失败: {str(e)}")
    
    async def _create_project_structure(self, project_path: str, request_data: dict):
        """创建Unity项目目录结构"""
        directories = [
            "Assets/Scripts",
            "Assets/Scenes",
            "Assets/Sprites", 
            "Assets/Audio",
            "Assets/Materials",
            "Assets/Prefabs",
            "Assets/Animations",
            "Packages",
            "ProjectSettings"
        ]
        
        for directory in directories:
            dir_path = os.path.join(project_path, directory)
            os.makedirs(dir_path, exist_ok=True)
    
    async def _generate_project_files(self, project_path: str, request_data: dict):
        """生成项目文件"""
        # 1. 生成manifest.json
        await self._create_manifest_file(project_path)
        
        # 2. 根据游戏类型生成对应的脚本
        game_type = request_data.get("game_type", "general")
        description = request_data.get("description", "")
        
        if game_type == "2d_platformer":
            await self._generate_2d_platformer_files(project_path, description)
        elif game_type == "shooter":
            await self._generate_shooter_files(project_path, description)
        elif game_type == "rpg":
            await self._generate_rpg_files(project_path, description)
        else:
            await self._generate_general_files(project_path, description)
        
        # 3. 生成场景文件
        await self._create_scene_file(project_path)
        
        # 4. 生成README文件
        await self._create_readme_file(project_path, request_data)
    
    async def _create_manifest_file(self, project_path: str):
        """创建Unity包管理文件"""
        manifest = {
            "dependencies": {
                "com.unity.collab-proxy": "2.0.4",
                "com.unity.ide.rider": "3.0.21",
                "com.unity.ide.visualstudio": "2.0.18",
                "com.unity.test-framework": "1.1.33",
                "com.unity.textmeshpro": "3.0.6",
                "com.unity.timeline": "1.7.4",
                "com.unity.ugui": "1.0.0",
                "com.unity.2d.sprite": "1.0.0",
                "com.unity.2d.tilemap": "1.0.0",
                "com.unity.modules.ai": "1.0.0",
                "com.unity.modules.androidjni": "1.0.0",
                "com.unity.modules.animation": "1.0.0",
                "com.unity.modules.assetbundle": "1.0.0",
                "com.unity.modules.audio": "1.0.0",
                "com.unity.modules.cloth": "1.0.0",
                "com.unity.modules.director": "1.0.0",
                "com.unity.modules.imageconversion": "1.0.0",
                "com.unity.modules.imgui": "1.0.0",
                "com.unity.modules.jsonserialize": "1.0.0",
                "com.unity.modules.particlesystem": "1.0.0",
                "com.unity.modules.physics": "1.0.0",
                "com.unity.modules.physics2d": "1.0.0",
                "com.unity.modules.screencapture": "1.0.0",
                "com.unity.modules.terrain": "1.0.0",
                "com.unity.modules.terrainphysics": "1.0.0",
                "com.unity.modules.tilemap": "1.0.0",
                "com.unity.modules.ui": "1.0.0",
                "com.unity.modules.uielements": "1.0.0",
                "com.unity.modules.umbra": "1.0.0",
                "com.unity.modules.unityanalytics": "1.0.0",
                "com.unity.modules.unitywebrequest": "1.0.0",
                "com.unity.modules.unitywebrequestassetbundle": "1.0.0",
                "com.unity.modules.unitywebrequestaudio": "1.0.0",
                "com.unity.modules.unitywebrequesttexture": "1.0.0",
                "com.unity.modules.unitywebrequestwww": "1.0.0",
                "com.unity.modules.vehicles": "1.0.0",
                "com.unity.modules.video": "1.0.0",
                "com.unity.modules.vr": "1.0.0",
                "com.unity.modules.wind": "1.0.0",
                "com.unity.modules.xr": "1.0.0"
            }
        }
        
        manifest_path = os.path.join(project_path, "Packages/manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    async def _generate_2d_platformer_files(self, project_path: str, description: str):
        """生成2D平台游戏文件"""
        scripts_dir = os.path.join(project_path, "Assets/Scripts")
        
        # PlayerController.cs
        player_controller_code = '''using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private LayerMask groundLayer;
    
    private Rigidbody2D rb;
    private bool isGrounded;
    private float horizontalInput;
    
    void Start()
    {
        rb = GetComponent<Rigidbody2D>();
    }
    
    void Update()
    {
        horizontalInput = Input.GetAxis("Horizontal");
        
        // 跳跃检测
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            rb.velocity = new Vector2(rb.velocity.x, jumpForce);
        }
    }
    
    void FixedUpdate()
    {
        // 移动
        rb.velocity = new Vector2(horizontalInput * moveSpeed, rb.velocity.y);
    }
    
    void OnCollisionEnter2D(Collision2D collision)
    {
        if (((1 << collision.gameObject.layer) & groundLayer) != 0)
        {
            isGrounded = true;
        }
    }
    
    void OnCollisionExit2D(Collision2D collision)
    {
        if (((1 << collision.gameObject.layer) & groundLayer) != 0)
        {
            isGrounded = false;
        }
    }
}
'''
        with open(os.path.join(scripts_dir, "PlayerController.cs"), 'w', encoding='utf-8') as f:
            f.write(player_controller_code)
        
        # GameManager.cs
        game_manager_code = '''using UnityEngine;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;
    
    [SerializeField] private Text scoreText;
    [SerializeField] private GameObject gameOverPanel;
    
    private int score = 0;
    private bool isGameOver = false;
    
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }
    
    void Start()
    {
        UpdateScoreUI();
    }
    
    public void AddScore(int points)
    {
        if (!isGameOver)
        {
            score += points;
            UpdateScoreUI();
        }
    }
    
    public void GameOver()
    {
        isGameOver = true;
        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(true);
        }
    }
    
    public void RestartGame()
    {
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name);
    }
    
    private void UpdateScoreUI()
    {
        if (scoreText != null)
        {
            scoreText.text = "Score: " + score;
        }
    }
}
'''
        with open(os.path.join(scripts_dir, "GameManager.cs"), 'w', encoding='utf-8') as f:
            f.write(game_manager_code)
        
        # CameraController.cs
        camera_controller_code = '''using UnityEngine;

public class CameraController : MonoBehaviour
{
    [SerializeField] private Transform player;
    [SerializeField] private float smoothSpeed = 0.125f;
    [SerializeField] private Vector3 offset;
    
    void LateUpdate()
    {
        if (player != null)
        {
            Vector3 desiredPosition = player.position + offset;
            Vector3 smoothedPosition = Vector3.Lerp(transform.position, desiredPosition, smoothSpeed);
            transform.position = new Vector3(smoothedPosition.x, smoothedPosition.y, transform.position.z);
        }
    }
}
'''
        with open(os.path.join(scripts_dir, "CameraController.cs"), 'w', encoding='utf-8') as f:
            f.write(camera_controller_code)
    
    async def _generate_shooter_files(self, project_path: str, description: str):
        """生成射击游戏文件"""
        scripts_dir = os.path.join(project_path, "Assets/Scripts")
        
        shooter_code = '''using UnityEngine;

public class ShooterPlayer : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 8f;
    [SerializeField] private GameObject bulletPrefab;
    [SerializeField] private Transform firePoint;
    [SerializeField] private float fireRate = 0.2f;
    
    private float nextFireTime = 0f;
    private Vector2 movement;
    
    void Update()
    {
        // 移动输入
        movement.x = Input.GetAxisRaw("Horizontal");
        movement.y = Input.GetAxisRaw("Vertical");
        
        // 射击输入
        if (Input.GetButton("Fire1") && Time.time >= nextFireTime)
        {
            Shoot();
            nextFireTime = Time.time + fireRate;
        }
    }
    
    void FixedUpdate()
    {
        // 移动
        transform.Translate(movement * moveSpeed * Time.fixedDeltaTime);
    }
    
    void Shoot()
    {
        if (bulletPrefab != null && firePoint != null)
        {
            Instantiate(bulletPrefab, firePoint.position, firePoint.rotation);
        }
    }
}

public class Bullet : MonoBehaviour
{
    [SerializeField] private float speed = 10f;
    [SerializeField] private float lifetime = 3f;
    
    void Start()
    {
        Destroy(gameObject, lifetime);
    }
    
    void Update()
    {
        transform.Translate(Vector3.up * speed * Time.deltaTime);
    }
    
    void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Enemy"))
        {
            Destroy(other.gameObject);
            Destroy(gameObject);
        }
    }
}
'''
        with open(os.path.join(scripts_dir, "ShooterController.cs"), 'w', encoding='utf-8') as f:
            f.write(shooter_code)
    
    async def _generate_rpg_files(self, project_path: str, description: str):
        """生成RPG游戏文件"""
        scripts_dir = os.path.join(project_path, "Assets/Scripts")
        
        rpg_code = '''using UnityEngine;

public class RPGPlayer : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private int attackDamage = 10;
    
    private int currentHealth;
    private Vector2 movement;
    private Animator animator;
    
    void Start()
    {
        currentHealth = maxHealth;
        animator = GetComponent<Animator>();
    }
    
    void Update()
    {
        movement.x = Input.GetAxisRaw("Horizontal");
        movement.y = Input.GetAxisRaw("Vertical");
        
        // 动画控制
        if (animator != null)
        {
            animator.SetFloat("Horizontal", movement.x);
            animator.SetFloat("Vertical", movement.y);
            animator.SetFloat("Speed", movement.sqrMagnitude);
        }
        
        // 攻击
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Attack();
        }
    }
    
    void FixedUpdate()
    {
        transform.Translate(movement * moveSpeed * Time.fixedDeltaTime);
    }
    
    void Attack()
    {
        // 攻击逻辑
        if (animator != null)
        {
            animator.SetTrigger("Attack");
        }
    }
    
    public void TakeDamage(int damage)
    {
        currentHealth -= damage;
        if (currentHealth <= 0)
        {
            Die();
        }
    }
    
    void Die()
    {
        // 死亡逻辑
        Debug.Log("Player died!");
    }
}
'''
        with open(os.path.join(scripts_dir, "RPGPlayer.cs"), 'w', encoding='utf-8') as f:
            f.write(rpg_code)
    
    async def _generate_general_files(self, project_path: str, description: str):
        """生成通用游戏文件"""
        scripts_dir = os.path.join(project_path, "Assets/Scripts")
        
        general_code = '''using UnityEngine;

public class GameController : MonoBehaviour
{
    void Start()
    {
        Debug.Log("游戏启动成功！");
    }
    
    void Update()
    {
        // 基础游戏循环
    }
}

public class Player : MonoBehaviour
{
    [SerializeField] private float speed = 5f;
    
    void Update()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, vertical, 0) * speed * Time.deltaTime;
        transform.Translate(movement);
    }
}
'''
        with open(os.path.join(scripts_dir, "GameController.cs"), 'w', encoding='utf-8') as f:
            f.write(general_code)
    
    async def _create_scene_file(self, project_path: str):
        """创建基础场景文件"""
        scene_content = '''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {fileID: 0}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: 0
  m_FogColor: {r: 0.5, g: 0.5, b: 0.5, a: 1}
  m_FogMode: 3
  m_FogDensity: 0.01
  m_LinearFogStart: 0
  m_LinearFogEnd: 300
  m_AmbientSkyColor: {r: 0.212, g: 0.227, b: 0.259, a: 1}
  m_AmbientEquatorColor: {r: 0.114, g: 0.125, b: 0.133, a: 1}
  m_AmbientGroundColor: {r: 0.047, g: 0.043, b: 0.035, a: 1}
  m_AmbientIntensity: 1
  m_AmbientMode: 0
  m_SubtractiveShadowColor: {r: 0.42, g: 0.478, b: 0.627, a: 1}
  m_SkyboxMaterial: {fileID: 0}
  m_HaloStrength: 0.5
  m_FlareStrength: 1
  m_FlareFadeSpeed: 3
  m_HaloTexture: {fileID: 0}
  m_SpotCookie: {fileID: 1000, guid: 0000000000000000e000000000000000, type: 0}
  m_DefaultReflectionMode: 0
  m_DefaultReflectionResolution: 128
  m_ReflectionBounces: 1
  m_ReflectionIntensity: 1
  m_CustomReflection: {fileID: 0}
  m_Sun: {fileID: 0}
  m_IndirectSpecularColor: {r: 0.44657898, g: 0.4964133, b: 0.5748178, a: 1}
  m_UseRadianceAmbientProbe: 0
'''
        scene_path = os.path.join(project_path, "Assets/Scenes/Main.unity")
        with open(scene_path, 'w', encoding='utf-8') as f:
            f.write(scene_content)
    
    async def _create_readme_file(self, project_path: str, request_data: dict):
        """创建项目说明文件"""
        readme_content = f'''# Unity 项目说明

## 项目信息
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **游戏类型**: {request_data.get('game_type', '通用')}
- **项目描述**: {request_data.get('description', '无')}

## 项目结构
{project_path}/
├── Assets/
│ ├── Scripts/ # C# 脚本文件
│ ├── Scenes/ # 场景文件
│ ├── Sprites/ # 精灵图资源
│ ├── Audio/ # 音频资源
│ └── Materials/ # 材质文件
├── Packages/ # Unity 包管理
└── ProjectSettings/ # 项目设置

## 使用说明
1. 使用 Unity Hub 打开此项目
2. 打开 Assets/Scenes/Main.unity 场景
3. 根据需要修改脚本和资源

## 生成内容
- 基础的游戏控制器脚本
- 玩家控制脚本
- 相机控制器（如适用）
- 游戏管理器
- 必要的Unity配置文件

## 注意事项
- 这是一个AI生成的起始项目
- 请根据实际需求进一步完善代码
- 建议添加错误处理和更多功能

---
*由 Unity AI Generator 生成*
'''
        readme_path = os.path.join(project_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    async def _create_zip_file(self, source_dir: str, output_zip: str):
        """创建zip压缩包"""
        import zipfile
        
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

# 创建项目构建器实例
project_builder = ProjectBuilder()

# 现在可以安全地使用 @router 装饰器了
@router.post("/generate-unity-project")
async def generate_unity_project(request: dict, background_tasks: BackgroundTasks):
    """生成Unity项目API端点 - 完整版本"""
    try:
        print(f"收到生成请求: {request}")
        
        print("验证必要字段")
        # 验证必要字段
        if not request.get("description") or not request.get("game_type"):
            raise HTTPException(
                status_code=400, 
                detail="缺少必要字段: description 和 game_type"
            )
        
        print("生成项目")        
        # 生成项目
        zip_path = await project_builder.create_unity_project(request)
        
        print("获取文件名")
        # 获取文件名
        filename = os.path.basename(zip_path)
        
        print("设置后台清理任务")
        # 设置后台清理任务
        background_tasks.add_task(cleanup_temp_files, zip_path)
        
        return {
            "status": "success",
            "message": "Unity项目生成完成",
            "download_url": f"/api/v1/download-project/{filename}",
            "filename": filename,
            "game_type": request.get("game_type"),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"项目生成失败: {str(e)}")

# @router.get("/download-project/{filename}")
# async def download_project(filename: str):
#     """下载项目zip包"""
#     file_path = os.path.join("temp_projects", filename)
    
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
#     # 返回文件下载
#     return FileResponse(
#         file_path,
#         filename=f"UnityProject_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
#         media_type='application/zip'
#     )
@router.get("/download-project/{filename}")
async def download_project(filename: str):
    """下载项目zip包"""
    try:
        # 安全检查：防止路径遍历攻击
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="无效的文件名")
        
        # 构建完整的文件路径
        file_path = os.path.join("temp_projects", filename)
        
        print(f"🔍 查找文件: {file_path}")  # 调试信息
        print(f"📁 当前工作目录: {os.getcwd()}")  # 调试信息
        print(f"📂 目录内容: {os.listdir('temp_projects') if os.path.exists('temp_projects') else '目录不存在'}")  # 调试信息
        
        if not os.path.exists(file_path):
            # 提供更详细的错误信息
            available_files = []
            if os.path.exists("temp_projects"):
                available_files = os.listdir("temp_projects")
            
            raise HTTPException(
                status_code=404, 
                detail={
                    "message": "文件不存在或已过期",
                    "requested_file": filename,
                    "available_files": available_files,
                    "search_path": file_path
                }
            )
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        print(f"📦 文件大小: {file_size} bytes")
        
        if file_size == 0:
            raise HTTPException(status_code=500, detail="文件为空")
        
        # 返回文件下载 - 使用原始文件名
        return FileResponse(
            file_path,
            filename=filename,  # 使用原始文件名，避免重复时间戳
            media_type='application/zip',
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 下载错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "status": "success", 
        "message": "API端点工作正常",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "项目生成",
            "文件下载", 
            "多游戏类型支持"
        ]
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy", 
        "service": "Unity AI Generator",
        "version": "1.0.0"
    }

# 清理函数
async def cleanup_temp_files(file_path: str):
    """清理临时文件"""
    await asyncio.sleep(300)  # 5分钟后清理
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"已清理临时文件: {file_path}")