# Cyber Nutritionist Pro

智能营养师应用，支持AI视觉识别食物和营养追踪。

## 功能特性

- 📸 AI视觉识别：拍照或上传图片，自动识别菜品和营养成分
- ✍️ 手动记账：支持手动添加食物记录
- 📊 营养追踪：实时追踪每日热量、蛋白质、碳水、脂肪摄入
- 🎯 个性化配额：根据身高、体重、年龄、性别、运动量计算每日热量配额

## 本地运行

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
.\venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`，并填入你的API密钥：

```toml
ZHIPU_API_KEY = "your_zhipu_api_key_here"
APP_PASSWORD = "your_app_password_here"
```

### 5. 启动应用

```bash
streamlit run app.py
```

## 部署到 Streamlit Cloud

### 使用 Streamlit Community Cloud (share.streamlit.io)

Streamlit Cloud 会自动读取你的 secrets.toml 文件中的配置，无需在代码中硬编码密码。

1. 将代码推送到 GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 点击 "New app"
4. 连接你的 GitHub 仓库
5. 在 "Secrets" 部分添加以下配置：

```
ZHIPU_API_KEY=your_zhipu_api_key_here
APP_PASSWORD=your_app_password_here
```

6. 点击 "Deploy"

## 安全说明

- ⚠️ **不要**将 `.streamlit/secrets.toml` 提交到 Git
- ⚠️ **不要**在代码中硬编码任何密钥或密码
- ✅ 使用 `.gitignore` 文件排除敏感文件
- ✅ 在 Streamlit Cloud 中通过 Secrets 管理配置

## 技术栈

- Streamlit - Web应用框架
- ZhipuAI (GLM-4V) - AI视觉识别
- SQLite - 数据存储
- Altair - 数据可视化

## 许可证

MIT License
