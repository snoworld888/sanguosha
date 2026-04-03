# GEO 智能优化平台

国内首个全栈自研的生成式引擎优化 SaaS 系统，帮助企业在 AI 搜索时代实现品牌在 AI 生成答案中的可见性提升与转化归因。

## 核心功能

- 🤖 **AI平台监测** - 实时监测 DeepSeek/Kimi/豆包等 9+ 平台的品牌引用情况
- 📊 **智能分析** - GEM评分模型、引用特征分析、竞品差距诊断
- ✍️ **内容生成** - 多平台 GEO 优化内容自动生成
- 🔗 **ROI归因** - 跨平台 ID-Mapping，全链路转化追踪

## 技术栈

- **后端**: Python 3.10+ / FastAPI + PostgreSQL + Redis + Elasticsearch
- **前端**: React 18 + TypeScript + Ant Design
- **AI**: DeepSeek API / 火山方舟 / Ollama 本地部署
- **基础设施**: Docker + K8s

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/geo-platform.git
cd geo-platform

# 安装后端依赖
pip install -e ".[dev]"

# 安装前端依赖
cd src/web && npm install

# 配置环境变量
cp configs/.env.example configs/.env
```

### 启动服务

```bash
# 启动后端API
uvicorn src.api.main:app --reload --port 8000

# 启动前端开发服务器
cd src/web && npm run dev
```

### 运行测试

```bash
pytest tests/ -v --cov=src
```

## 项目结构

```
geo-platform/
├── src/
│   ├── api/              # API层
│   │   ├── main.py       # FastAPI应用入口
│   │   ├── routers/      # 路由定义
│   │   └── middleware/   # 中间件
│   ├── core/             # 核心模块
│   │   ├── config.py     # 配置管理
│   │   ├── security.py   # 安全认证
│   │   └── exceptions.py # 异常定义
│   ├── models/           # 数据模型
│   │   ├── database.py   # SQLAlchemy模型
│   │   └── schemas.py    # Pydantic模型
│   ├── services/         # 业务逻辑
│   │   ├── monitoring/    # 监测服务
│   │   ├── analysis/      # 分析服务
│   │   ├── content/       # 内容生成服务
│   │   └── attribution/   # 归因服务
│   ├── infrastructure/    # 基础设施
│   │   ├── ai/            # AI模型接入
│   │   ├── storage/       # 存储服务
│   │   └── crawler/       # 数据采集
│   └── worker/            # 异步任务
├── tests/                 # 测试文件
├── configs/               # 配置文件
└── scripts/               # 脚本工具
```

## 许可证

MIT License
