# 🤖 AI 智能助手平台 (AI Assistant Platform)

> Vue 3 + Django 全栈智能辅助平台，集成论文助手与代码助手，支持 DeepSeek / Ollama 等多种 LLM 后端。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![Django](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)

---

## ✨ 功能特性

### 📝 论文助手
- **大纲生成** — 根据主题描述自动生成详细论文大纲（章节+要点）
- **润色优化** — 学术风 / 简洁风 / 降重风三种模式润色论文
- **论文点评** — 从结构、逻辑、技术、语言四个维度审阅论文

### 💻 代码助手
- **代码审查** — 查找 Bug、性能问题、安全隐患、代码风格问题
- **Bug 修复** — 分析报错信息并给出修复后的完整代码
- **代码生成** — 根据自然语言描述生成代码

### 🔐 用户系统
- JWT 注册/登录（Access Token 24h，Refresh Token 7天）
- 个人中心：论文/代码历史记录分开管理
- 分页查看、删除、查看详情
- 频率限制：代码端点 5次/分钟

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Vite + Pinia + Element Plus + Vue Router + Monaco Editor |
| **后端 (Django)** | Django 5 + Django REST Framework + SimpleJWT + SQLite |
| **后端 (FastAPI)** | FastAPI + SQLAlchemy + SQLite（轻量替代方案） |
| **LLM** | DeepSeek API（OpenAI 兼容） / Ollama 本地模型 |
| **样式** | SCSS + Element Plus 暗色主题 |

---

## 📁 项目结构

```
ai-assistant-platform/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/                 # Axios API 封装
│   │   ├── components/          # 通用组件
│   │   ├── composables/         # 组合式函数
│   │   ├── router/              # Vue Router 路由
│   │   ├── stores/              # Pinia 状态管理
│   │   ├── styles/              # 全局样式 & 主题
│   │   └── views/               # 页面视图
│   └── vite.config.js
├── backend_django/              # Django 5 后端（推荐）
│   ├── config/                  # Django 配置
│   │   ├── settings.py          # 核心设置
│   │   └── urls.py              # 路由入口
│   ├── assistant/               # 核心应用
│   │   ├── paper_views.py       # 论文助手 API
│   │   ├── code_views.py        # 代码助手 API
│   │   ├── views.py             # 认证 & 历史 API
│   │   ├── models.py            # 数据模型
│   │   ├── serializers.py       # DRF 序列化器
│   │   └── services/
│   │       └── llm_service.py   # LLM 调用服务（支持重试/流式）
│   └── manage.py
├── backend/                     # FastAPI 后端（轻量替代）
│   ├── main.py                  # API 入口
│   ├── models.py                # SQLAlchemy 模型
│   ├── auth.py                  # JWT 认证
│   └── database.py              # 数据库连接
├── start.py                     # 一键启动脚本
├── start.sh                     # Linux/Mac 启动脚本
├── .gitignore
└── README.md
```

---

## 🚀 快速开始

### 前置要求

- **Python** >= 3.12
- **Node.js** >= 18
- **DeepSeek API Key**（[免费注册获取](https://platform.deepseek.com/)）或本地 Ollama

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/ai-assistant-platform.git
cd ai-assistant-platform
```

### 2. 配置环境变量

```bash
# Django 后端
cp backend_django/.env.example backend_django/.env
# 编辑 backend_django/.env，填入你的 API Key

# FastAPI 后端（可选）
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 API Key
```

### 3. 启动 Django 后端

```bash
cd backend_django

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行迁移
python manage.py migrate

# 启动服务
python manage.py runserver 8001
```

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问平台

打开浏览器访问 **http://localhost:5173**

### 🎯 一键启动

```bash
# Windows / Linux / Mac
python start.py
```

---

## 🔌 API 端点

### 认证
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register/` | POST | 用户注册 |
| `/api/auth/login/` | POST | 用户登录 |
| `/api/user/me/` | GET | 获取当前用户信息 |

### 论文助手
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/paper/outline` | POST | 生成论文大纲 |
| `/api/paper/polish` | POST | 润色论文内容 |
| `/api/paper/feedback` | POST | 论文审阅点评 |

### 代码助手
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/code/review` | POST | 代码审查 |
| `/api/code/debug` | POST | Bug 修复 |
| `/api/code/generate` | POST | 代码生成 |

### 历史记录
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/history/paper/` | GET | 论文历史（分页） |
| `/api/history/code/` | GET | 代码历史（分页） |
| `/api/history/{id}/` | DELETE | 删除记录 |

---

## 🎨 截图

> 运行 `npm run dev` 后访问 http://localhost:5173 体验

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 开源协议

本项目采用 [MIT 许可证](LICENSE)。

---

## ⚠️ 安全提示

- **绝不提交 `.env` 文件到版本控制** — 已在 `.gitignore` 中排除
- 生产环境请设置 `DEBUG=False` 并配置 `ALLOWED_HOSTS`
- 生产环境请修改 Django `SECRET_KEY` 为强随机值
- 建议定期轮换 LLM API Key

---

*Made with ❤️ by 陈俊宇 | 2024-2026*
