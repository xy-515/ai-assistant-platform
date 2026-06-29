<p align="center">
  <h1 align="center">🤖 AI 智能助手平台</h1>
  <p align="center"><strong>AI Assistant Platform</strong> — 你的全能学术与编程 AI 助手</p>
</p>

<p align="center">
  <a href="https://github.com/xy-515/ai-assistant-platform/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/django-5.0-green.svg" alt="Django">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/vue-3.5-brightgreen.svg" alt="Vue">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/vite-5.4-purple.svg" alt="Vite">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/LLM-DeepSeek%20%7C%20Ollama-orange.svg" alt="LLM">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/JWT-auth-ff69b4.svg" alt="JWT">
  </a>
</p>

---

## 📖 项目简介

**AI 智能助手平台** 是一个基于 Vue 3 + Django 5 的全栈 Web 应用，集成了 **论文助手** 和 **代码助手** 两大核心模块。用户通过自然语言与 AI 交互，即可完成论文大纲生成、内容润色、代码审查、Bug 修复等任务。

项目支持 **DeepSeek API**（OpenAI 兼容协议）和 **Ollama 本地模型** 两种 LLM 后端，开箱即用。前后端分离架构，提供完整的 JWT 认证体系、历史记录管理和频率限制功能。

> 🎓 本项目同时作为毕业设计作品，全栈自研，适合学习 Vue 3 + Django REST Framework + LLM 集成开发。

---

## ✨ 功能特性

### 📝 论文助手

| 功能 | 说明 |
|------|------|
| ✅ **大纲生成** | 输入论文主题，AI 自动生成包含章节标题和每节要点的详细大纲 |
| ✅ **润色优化** | 支持 **学术风 / 简洁风 / 降重风** 三种模式，提升论文表达质量 |
| ✅ **论文点评** | 从 **结构、逻辑、技术描述、语言表达** 四个维度进行专业审稿 |

### 💻 代码助手

| 功能 | 说明 |
|------|------|
| ✅ **代码审查** | 自动查找 Bug、性能问题、安全隐患、代码风格问题，给出修复建议 |
| ✅ **Bug 修复** | 分析报错信息，定位问题根因并输出修复后的完整代码 |
| ✅ **代码生成** | 根据自然语言描述生成代码，支持多语言 |

### 🔐 用户系统

| 功能 | 说明 |
|------|------|
| ✅ **JWT 认证** | 注册 / 登录，Access Token 24h + Refresh Token 7天 |
| ✅ **历史管理** | 论文 / 代码历史分开管理，分页查看、查看详情、删除 |
| ✅ **频率限制** | 代码端点 5次/分钟，防止 API 滥用 |
| ✅ **暗色主题** | 一键切换亮色 / 暗色主题 |

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────┐
│                    Frontend                      │
│  Vue 3 · Vite · Pinia · Element Plus · Router   │
│         Monaco Editor · Axios · SCSS             │
└──────────────────┬──────────────────────────────┘
                   │  HTTP / REST API
                   │  JWT Bearer Token
                   ↓
┌─────────────────────────────────────────────────┐
│                Backend (Django)                  │
│  Django 5 · DRF · SimpleJWT · CORS Headers       │
│         SQLite · python-dotenv                   │
└────────┬────────────────────┬───────────────────┘
         │                    │
         ↓                    ↓
┌─────────────────┐  ┌──────────────────┐
│   DeepSeek API  │  │  Ollama (Local)  │
│  deepseek-chat  │  │  qwen2.5:7b ...  │
└─────────────────┘  └──────────────────┘
```

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端框架** | Vue 3 + Vite 5 | Composition API + `<script setup>` |
| **状态管理** | Pinia 2 | 轻量级状态管理，替代 Vuex |
| **UI 组件库** | Element Plus 2.14 | 丰富的 Vue 3 组件库 |
| **代码编辑器** | Monaco Editor 0.55 | VS Code 同款编辑器内核 |
| **后端框架** | Django 5 + DRF 3.15 | 成熟的 Python Web 框架 |
| **认证方案** | SimpleJWT 5.4 | JWT 令牌认证 |
| **LLM 服务层** | httpx + SSE 解析 | 支持重试、超时、流式输出 |
| **数据库** | SQLite | 轻量开发，可按需切换 PostgreSQL |
| **样式方案** | SCSS + CSS Variables | 亮色/暗色主题切换 |

---

## 🔄 核心工作流程

### 论文助手流程

```
用户输入主题/内容
        │
        ▼
┌─────────────────┐
│  前端发送请求    │  POST /api/paper/outline
│  JWT Token 认证  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Django 后端接收 │  参数校验 & 频率检查
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Service    │  构建 System Prompt + User Prompt
│  (httpx 异步)   │  调用 DeepSeek Chat API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SSE 流式解析   │  逐 Token 返回前端
│  (Streaming)    │  实时打字机效果展示
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  保存历史记录    │  存入 SQLite
│  返回结果        │  用户可在个人中心查看
└─────────────────┘
```

### 代码助手流程

```
用户粘贴代码 + 描述问题
        │
        ▼
┌─────────────────┐
│  频率限制检查    │  代码端点 5次/分钟
│  (Rate Limiter)  │  超过限制返回 429
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  构建 Prompt     │  代码 + 报错信息 → LLM
│  (代码审查/修复) │  专业 Code Review Prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  重试 & 容错     │  网络异常自动重试（最多3次）
│  (Retry Logic)   │  429/5xx 指数退避
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  返回审查结果    │  Markdown 格式
│  + 修复后代码    │  Monaco Editor 渲染
└─────────────────┘
```

---

## 📁 项目结构

```
ai-assistant-platform/
├── frontend/                          # Vue 3 前端
│   ├── src/
│   │   ├── api/axios.js               # Axios 实例 + 拦截器
│   │   ├── components/
│   │   │   ├── PaperAssistant.vue     # 论文助手主组件
│   │   │   ├── CodeAssistant.vue      # 代码助手主组件
│   │   │   ├── MonacoEditor.vue       # Monaco 编辑器封装
│   │   │   ├── HistoryList.vue        # 历史记录列表
│   │   │   └── ThemeToggle.vue        # 主题切换按钮
│   │   ├── composables/
│   │   │   ├── useStreaming.js        # SSE 流式接收 Hook
│   │   │   └── useTheme.js            # 主题管理 Hook
│   │   ├── router/index.js            # 路由配置
│   │   ├── stores/auth.js             # 认证状态 (Pinia)
│   │   ├── styles/
│   │   │   ├── global.scss            # 全局样式
│   │   │   ├── auth.scss              # 登录/注册页样式
│   │   │   ├── theme.css              # 主题变量
│   │   │   └── micro-interactions.css # 微交互动画
│   │   ├── views/
│   │   │   ├── Home.vue               # 首页（功能导航）
│   │   │   ├── Login.vue              # 登录页
│   │   │   ├── Register.vue           # 注册页
│   │   │   └── Profile.vue            # 个人中心
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js                 # Vite 配置 + 代理
│   └── package.json
├── backend_django/                    # Django 5 后端（推荐）
│   ├── config/
│   │   ├── settings.py                # Django 设置
│   │   ├── urls.py                    # 路由入口
│   │   └── wsgi.py
│   ├── assistant/                     # 核心应用
│   │   ├── paper_views.py             # 论文助手 API（异步视图）
│   │   ├── code_views.py              # 代码助手 API + 频率限制
│   │   ├── views.py                   # 认证 + 用户 + 历史记录
│   │   ├── models.py                  # 数据模型（User/History）
│   │   ├── serializers.py             # DRF 序列化器
│   │   ├── services/
│   │   │   └── llm_service.py         # LLM 调用服务（重试/流式）
│   │   └── migrations/                # 数据库迁移
│   ├── manage.py
│   ├── requirements.txt
│   ├── test_llm.py                    # LLM 服务测试
│   ├── test_paper_api.py              # 论文 API 测试
│   └── test_code_api.py               # 代码 API 测试
├── backend/                           # FastAPI 后端（轻量替代）
│   ├── main.py                        # API 入口（全部端点）
│   ├── models.py                      # SQLAlchemy 模型
│   ├── auth.py                        # JWT 认证
│   ├── database.py                    # 数据库引擎
│   └── requirements.txt
├── start.py                           # 一键启动脚本 (Python)
├── start.sh                           # 一键启动脚本 (Shell)
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

---

## 🚀 快速开始

### 📋 前置要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | ≥ 3.12 | 后端运行环境 |
| Node.js | ≥ 18 | 前端构建工具链 |
| DeepSeek API Key | — | [免费注册获取](https://platform.deepseek.com/) |

### 1️⃣ 克隆项目

```bash
git clone https://github.com/xy-515/ai-assistant-platform.git
cd ai-assistant-platform
```

### 2️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp backend_django/.env.example backend_django/.env
```

编辑 `backend_django/.env`，填入你的 API Key：

```env
# DeepSeek API (OpenAI 兼容协议)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx    # 👈 替换为你的 Key
OPENAI_MODEL=deepseek-chat
OPENAI_BASE_URL=https://api.deepseek.com
```

> 💡 **本地模型替代方案**：如果你有本地部署的 Ollama，可以注释掉 DeepSeek 配置，启用 Ollama 配置。

### 3️⃣ 启动 Django 后端

```bash
cd backend_django

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库
python manage.py migrate

# 启动后端服务
python manage.py runserver 8001
```

### 4️⃣ 启动前端

```bash
# 打开新终端
cd frontend

# 安装 Node 依赖
npm install

# 启动开发服务器
npm run dev
```

### 5️⃣ 访问平台

打开浏览器访问：

```
http://localhost:5173
```

### 🎯 一键启动

```bash
# Windows / Linux / macOS
python start.py
```

---

## 🔌 API 接口文档

### 🔑 认证接口

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/auth/register/` | 用户注册 | — |
| `POST` | `/api/auth/login/` | 用户登录，返回 JWT | — |
| `GET` | `/api/user/me/` | 获取当前用户信息 | Bearer Token |

<details>
<summary>📨 请求/响应示例</summary>

**注册：**
```json
POST /api/auth/register/
{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123"
}

Response:
{
    "token": "eyJhbGciOi...",
    "user": {
        "id": 1,
        "username": "demo",
        "email": "demo@example.com"
    }
}
```

**登录：**
```json
POST /api/auth/login/
{
    "username": "demo",
    "password": "demo123"
}

Response:
{
    "token": "eyJhbGciOi...",
    "user": { ... }
}
```
</details>

### 📝 论文助手接口

| 方法 | 端点 | 说明 | 参数 |
|------|------|------|------|
| `POST` | `/api/paper/outline` | 生成论文大纲 | `{ "content": "主题描述" }` |
| `POST` | `/api/paper/polish` | 润色论文内容 | `{ "content": "论文内容", "style": "academic\|concise\|deweight" }` |
| `POST` | `/api/paper/feedback` | 论文审阅点评 | `{ "content": "论文内容" }` |

### 💻 代码助手接口

| 方法 | 端点 | 说明 | 参数 |
|------|------|------|------|
| `POST` | `/api/code/review` | 代码审查 | `{ "code": "...", "language": "python" }` |
| `POST` | `/api/code/debug` | Bug 修复 | `{ "code": "...", "error": "报错信息" }` |
| `POST` | `/api/code/generate` | 代码生成 | `{ "description": "需求描述", "language": "python" }` |

> ⚠️ 代码端点在 1 分钟内最多调用 5 次，超过限制返回 `429 Too Many Requests`。

### 📋 历史记录接口

| 方法 | 端点 | 说明 |
|------|------|------|
| `GET` | `/api/history/paper/?page=1` | 论文历史（分页） |
| `GET` | `/api/history/code/?page=1` | 代码历史（分页） |
| `DELETE` | `/api/history/{id}/` | 删除指定记录 |

---

## 🎨 界面预览

> 运行项目后访问 `http://localhost:5173` 即可体验完整功能。

| 页面 | 说明 |
|------|------|
| 🏠 **首页** | 功能导航卡片，论文助手 / 代码助手入口 |
| 📝 **论文助手** | 选择功能（大纲/润色/点评），输入内容，实时流式返回结果 |
| 💻 **代码助手** | Monaco Editor 编辑代码，选择审查/修复/生成功能 |
| 👤 **个人中心** | 查看历史记录，分页浏览，删除不需要的记录 |
| 🔑 **登录/注册** | JWT 认证，支持注册新账号 |

---

## 🧪 测试

```bash
cd backend_django

# 测试 LLM 服务连接
python test_llm.py

# 测试论文助手 API
python test_paper_api.py

# 测试代码助手 API
python test_code_api.py
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 开源协议

本项目采用 [MIT 许可证](LICENSE)。你可以自由使用、修改、分发本项目代码。

---

## ⚠️ 注意事项

- 🔒 **绝不提交 `.env` 文件到版本控制** — 已在 `.gitignore` 中排除
- 🚀 生产环境请设置 `DEBUG=False` 并配置 `ALLOWED_HOSTS`
- 🔑 生产环境请修改 Django `SECRET_KEY` 为强随机值
- 🔄 建议定期轮换 LLM API Key
- 🌐 首次使用前请确保 DeepSeek API Key 有效且有可用额度
- 📦 数据库文件 `db.sqlite3` 未提交到仓库，首次运行 `migrate` 会自动创建

---
