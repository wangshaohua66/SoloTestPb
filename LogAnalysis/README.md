# 日志聚合分析平台

面向运维人员的日志管理工具，用于收集、解析、聚合多源日志数据，支持日志检索、统计分析、异常告警，帮助快速定位系统问题。

## 功能特性

- **日志收集**: 支持从文件、标准输出、网络端口等多种来源收集日志
- **日志解析**: 自动解析日志时间、级别、模块、内容等字段，支持自定义解析规则
- **日志聚合**: 按时间窗口、服务、级别等维度聚合日志，统计错误率、响应时间等指标
- **日志检索**: 支持关键词搜索、时间范围过滤、多条件组合查询
- **异常告警**: 根据规则检测异常日志，触发告警通知
- **报表导出**: 生成日志分析报告，支持导出文本和JSON格式

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.13 + Flask + SQLAlchemy |
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 数据库 | SQLite |

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 18+
- npm

### 安装依赖

#### 后端

```bash
cd backend
pip install -r requirements.txt
```

#### 前端

```bash
cd frontend
npm install
```

### 启动服务

#### 启动后端 (端口 5001)

```bash
cd backend
python run.py
```

后端服务地址: http://localhost:5001

#### 启动前端 (端口 8001)

```bash
cd frontend
npm run dev
```

### 访问系统

打开浏览器访问: http://localhost:8001

## 项目结构

```
LogAnalysis/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   ├── modules/           # 业务模块
│   │   └── routes/            # API路由
│   ├── config.py              # 系统配置
│   ├── run.py                 # 启动入口
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   └── utils/             # 工具函数
│   ├── package.json           # Node依赖
│   └── vite.config.js         # Vite配置
├── examples/                   # 示例日志文件
│   ├── sample_nginx.log
│   ├── sample_python.log
│   └── sample_java.log
├── docs/                       # 文档
│   ├── 系统设计文档.md
│   └── 使用说明.md
└── README.md
```

## 功能页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 仪表盘 | /dashboard | 数据概览、趋势图表 |
| 日志浏览 | /logs | 查看日志列表 |
| 日志检索 | /search | 多条件搜索 |
| 统计分析 | /stats | 多维度统计 |
| 告警管理 | /alerts | 告警列表、规则管理 |
| 报表导出 | /reports | 生成和导出报表 |
| 配置管理 | /config | 日志来源、解析规则 |

## API接口

### 日志接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/logs | 获取日志列表 |
| POST | /api/logs | 接收单条日志 |
| POST | /api/logs/batch | 批量接收日志 |

### 其他接口

- `/api/search` - 日志检索
- `/api/stats/*` - 统计分析
- `/api/alerts/*` - 告警管理
- `/api/reports/*` - 报表管理
- `/api/collect/*` - 收集配置

## 示例日志

项目提供三种常见日志格式示例，位于 `examples/` 目录：

- `sample_nginx.log` - Nginx访问日志
- `sample_python.log` - Python logging格式
- `sample_java.log` - Java Logback格式

## 文档

- [系统设计文档](docs/系统设计文档.md)
- [使用说明](docs/使用说明.md)

## License

MIT
