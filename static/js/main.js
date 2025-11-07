// 主要JavaScript逻辑
class UnityAIGenerator {
    constructor() {
        this.initializeEventListeners();
        this.currentProject = null;
    }

    initializeEventListeners() {
        // 表单提交
        const form = document.getElementById('gameForm');
        form.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // 字符计数
        const textarea = document.getElementById('gameDescription');
        textarea.addEventListener('input', (e) => this.updateCharCount(e));

        // 模态框控制
        const closeModal = document.getElementById('closeModal');
        const modal = document.getElementById('detailsModal');
        
        closeModal.addEventListener('click', () => this.hideModal());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.hideModal();
        });

        // 操作按钮
        document.getElementById('newProjectBtn').addEventListener('click', () => this.resetForm());
        document.getElementById('viewDetailsBtn').addEventListener('click', () => this.showProjectDetails());

        // 初始化字符计数
        this.updateCharCount({ target: textarea });
    }

    updateCharCount(e) {
        const count = e.target.value.length;
        document.getElementById('charCount').textContent = count;
        
        // 更新字符计数样式
        const charCount = document.getElementById('charCount');
        if (count < 10) {
            charCount.style.color = '#e53e3e';
        } else if (count < 50) {
            charCount.style.color = '#d69e2e';
        } else {
            charCount.style.color = '#38a169';
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {
            description: formData.get('description'),
            game_type: formData.get('game_type'),
            complexity: formData.get('complexity'),
            asset_style: formData.get('asset_style'),
            include_assets: formData.get('include_assets') === 'on'
        };

        // 验证表单
        if (!this.validateForm(data)) {
            return;
        }

        // 开始生成
        await this.generateProject(data);
    }

    validateForm(data) {
        if (!data.description || data.description.length < 10) {
            this.showError('请提供至少10个字符的游戏描述');
            return false;
        }

        if (!data.game_type) {
            this.showError('请选择游戏类型');
            return false;
        }

        return true;
    }

    async generateProject(data) {
        try {
            this.showLoading();
            
            const response = await fetch('/api/v1/generate-unity-project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || '生成失败');
            }

            this.currentProject = result;
            this.showSuccess(result);
            
        } catch (error) {
            console.error('生成错误:', error);
            this.showError(error.message || '生成过程中出现错误，请重试');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        const generateBtn = document.getElementById('generateBtn');
        const btnText = generateBtn.querySelector('.btn-text');
        const spinner = generateBtn.querySelector('.loading-spinner');

        // 禁用按钮并显示加载状态
        generateBtn.disabled = true;
        btnText.textContent = '生成中...';
        spinner.style.display = 'block';

        // 显示加载覆盖层
        overlay.style.display = 'block';

        // 模拟进度更新
        this.simulateProgress();
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        const generateBtn = document.getElementById('generateBtn');
        const btnText = generateBtn.querySelector('.btn-text');
        const spinner = generateBtn.querySelector('.loading-spinner');

        // 恢复按钮状态
        generateBtn.disabled = false;
        btnText.textContent = '生成Unity项目';
        spinner.style.display = 'none';

        // 隐藏加载覆盖层
        overlay.style.display = 'none';
    }

    simulateProgress() {
        const progressBar = document.getElementById('progressBar');
        const steps = document.querySelectorAll('.loading-steps .step');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            progressBar.style.width = `${progress}%`;

            // 更新步骤状态
            this.updateLoadingSteps(progress, steps);
        }, 500);
    }

    updateLoadingSteps(progress, steps) {
        const stepIndex = Math.floor(progress / 25);
        steps.forEach((step, index) => {
            if (index <= stepIndex) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }

    showSuccess(result) {
        // 更新结果信息
        document.getElementById('projectName').textContent = result.download_url ? 
            result.download_url.split('/').pop() : '未知文件';
        document.getElementById('generateTime').textContent = new Date().toLocaleString();
        document.getElementById('fileSize').textContent = '计算中...';

        // 设置下载链接
        const downloadBtn = document.getElementById('downloadBtn');
        if (result.download_url) {
            downloadBtn.href = result.download_url;
            
            // 获取文件大小
            this.updateFileSize(result.download_url);
        }

        // 显示结果区域
        document.getElementById('resultsSection').style.display = 'block';

        // 滚动到结果区域
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    async updateFileSize(downloadUrl) {
        try {
            const response = await fetch(downloadUrl, { method: 'HEAD' });
            const size = response.headers.get('content-length');
            
            if (size) {
                const sizeMB = (size / (1024 * 1024)).toFixed(2);
                document.getElementById('fileSize').textContent = `${sizeMB} MB`;
            } else {
                document.getElementById('fileSize').textContent = '未知';
            }
        } catch (error) {
            document.getElementById('fileSize').textContent = '未知';
        }
    }

    showError(message) {
        // 这里可以替换为更美观的错误提示
        alert(`错误: ${message}`);
    }

    resetForm() {
        document.getElementById('gameForm').reset();
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('charCount').textContent = '0';
        
        // 滚动到顶部
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async showProjectDetails() {
        if (!this.currentProject) return;

        const modal = document.getElementById('detailsModal');
        const structureElement = document.getElementById('projectStructure');

        try {
            // 这里可以添加获取项目详细结构的API调用
            structureElement.textContent = '正在加载项目结构...';
            modal.style.display = 'block';

            // 模拟获取项目结构
            setTimeout(() => {
                structureElement.textContent = this.generateSampleStructure();
            }, 1000);

        } catch (error) {
            structureElement.textContent = '无法加载项目结构详情';
        }
    }

    hideModal() {
        document.getElementById('detailsModal').style.display = 'none';
    }

    generateSampleStructure() {
        return `UnityProject/
├── Assets/
│   ├── Scripts/
│   │   ├── PlayerController.cs
│   │   ├── GameManager.cs
│   │   ├── EnemyAI.cs
│   │   └── UIManager.cs
│   ├── Scenes/
│   │   └── Main.unity
│   ├── Sprites/
│   │   ├── player.png
│   │   ├── enemy.png
│   │   └── background.png
│   ├── Audio/
│   │   └── effects/
│   └── Materials/
├── Packages/
│   └── manifest.json
├── ProjectSettings/
│   └── ProjectSettings.asset
└── README.txt`;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new UnityAIGenerator();
    
    // 添加一些动画效果
    const cards = document.querySelectorAll('.form-card, .results-card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.6s ease ${index * 0.1}s both`;
    });
});

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);