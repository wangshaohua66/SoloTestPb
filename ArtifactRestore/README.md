# 文物修复记录系统

一个面向文物修复师和博物馆管理人员的文物修复记录系统，用于记录文物修复全过程，建立修复档案，便于追溯和研究。

## 项目简介

本系统提供完整的文物修复档案管理功能，包括文物档案录入、修复计划制定、修复过程记录、影像资料管理、材料使用记录、独立管理页面以及档案导出等功能。

## 功能模块

### 核心功能模块

1. **文物档案** - 录入文物基本信息（名称、年代、类别、尺寸、材质、保存状态、病害描述）
2. **修复计划** - 制定修复方案，记录修复目标、方法、材料、预计工期
3. **过程记录** - 按时间顺序记录修复过程（操作步骤、使用材料、工具设备、遇到问题）
4. **影像管理** - 记录修复前、中、后的影像资料，支持文件上传
5. **材料管理** - 记录修复使用的材料信息（名称、来源、用量）
6. **档案导出** - 生成完整的修复档案报告，支持多种格式导出

### 新增独立管理页面

7. **修复计划列表页** - 查看所有文物的修复计划汇总，支持搜索筛选和分页
8. **过程记录时间线页** - 按时间顺序展示所有修复过程，支持时间段和类别筛选
9. **影像资料库页** - 网格形式展示所有影像，支持图片放大预览和阶段筛选
10. **材料管理页** - 显示所有材料汇总，支持搜索和用量统计

## 技术栈

- **后端**: Python 3.13 + Flask + Flask-SQLAlchemy
- **前端**: Vue 3 + Vite + Element Plus
- **数据库**: SQLite（本地文件数据库）
- **代码规范**: PEP8

## 项目结构

```
ArtifactRestore/
├── backend/                 # 后端项目
│   ├── app/                 # Flask应用
│   │   ├── routes/          # API路由
│   │   │   ├── artifacts.py  # 文物档案路由
│   │   │   ├── plans.py      # 修复计划路由
│   │   │   ├── processes.py  # 过程记录路由
│   │   │   ├── images.py     # 影像管理路由
│   │   │   ├── materials.py  # 材料管理路由
│   │   │   └── export.py     # 档案导出路由
│   │   ├── models.py        # 数据库模型
│   │   ├── static/          # 静态资源
│   │   └── __init__.py      # 应用初始化
│   ├── logs/                # 日志目录
│   ├── config.py            # 配置文件
│   ├── requirements.txt     # Python依赖
│   └── run.py               # 启动入口
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── views/           # 页面组件
│   │   │   ├── Home.vue          # 首页
│   │   │   ├── Artifacts.vue     # 文物档案列表
│   │   │   ├── ArtifactDetail.vue # 文物详情
│   │   │   ├── Plans.vue         # 修复计划列表
│   │   │   ├── Processes.vue     # 过程记录时间线
│   │   │   ├── Images.vue        # 影像资料库
│   │   │   ├── Materials.vue     # 材料管理
│   │   │   └── Export.vue        # 档案导出
│   │   ├── api/             # API接口封装
│   │   ├── router/          # 路由配置
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口文件
│   ├── index.html           # HTML模板
│   ├── vite.config.js       # Vite配置
│   └── package.json         # Node依赖
├── docs/                    # 文档目录
│   ├── 系统设计文档.md       # 系统设计文档
│   └── 使用说明.md          # 用户使用说明
└── README.md                # 项目说明
```

## 端口配置

- 后端服务端口：5002
- 前端服务端口：8002

## 后端启动

### 1. 环境准备

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run.py
```

服务启动后访问：http://127.0.0.1:5002

## 前端启动

### 1. 环境准备

```bash
cd frontend

# 安装依赖
npm install
```

### 2. 启动开发服务

```bash
npm run dev
```

服务启动后访问：http://127.0.0.1:8002

### 3. 构建生产版本

```bash
npm run build
```

## 快速开始

1. 先启动后端服务
2. 再启动前端服务
3. 浏览器访问 http://127.0.0.1:8002
4. 首页查看数据统计（点击统计卡片可快速跳转）
5. 在"文物档案"页面新建文物
6. 点击"详情"进入文物详情页面
7. 在详情页可以添加修复计划、过程记录、影像资料、材料使用记录
8. 使用独立管理页面批量查看和管理各模块数据
9. 在"档案导出"页面可以批量导出修复档案报告

## API接口列表

### 文物档案接口
- `GET /api/artifacts/` - 获取文物列表（支持分页和搜索）
- `GET /api/artifacts/:id` - 获取文物详情
- `POST /api/artifacts/` - 新建文物
- `PUT /api/artifacts/:id` - 更新文物
- `DELETE /api/artifacts/:id` - 删除文物

### 修复计划接口
- `GET /api/plans/?artifact_id=:id` - 获取文物的修复计划列表
- `POST /api/plans/` - 新建修复计划
- `PUT /api/plans/:id` - 更新修复计划
- `DELETE /api/plans/:id` - 删除修复计划

### 过程记录接口
- `GET /api/processes/?artifact_id=:id` - 获取文物的过程记录列表
- `POST /api/processes/` - 新建过程记录
- `PUT /api/processes/:id` - 更新过程记录
- `DELETE /api/processes/:id` - 删除过程记录

### 影像管理接口
- `GET /api/images/?artifact_id=:id` - 获取文物的影像列表
- `POST /api/images/` - 新建影像（支持文件上传）
- `PUT /api/images/:id` - 更新影像信息
- `DELETE /api/images/:id` - 删除影像

### 材料管理接口
- `GET /api/materials/?artifact_id=:id` - 获取文物的材料列表
- `POST /api/materials/` - 新建材料记录
- `PUT /api/materials/:id` - 更新材料记录
- `DELETE /api/materials/:id` - 删除材料记录

### 档案导出接口
- `GET /api/export/stats` - 获取系统统计数据
- `GET /api/export/list` - 获取可导出的文物列表
- `GET /api/export/artifact/:id?format=txt|json` - 导出单个文物报告
- `GET /api/export/batch?ids=1,2,3&format=txt|json` - 批量导出文物报告
- `GET /api/export/history` - 获取导出历史记录

## 数据库说明

系统使用 SQLite 数据库，数据库文件为 `backend/app.db`，首次启动时会自动创建数据库表。

数据库包含以下表：
- `artifacts` - 文物档案表
- `repair_plans` - 修复计划表
- `repair_processes` - 修复过程记录表
- `image_records` - 影像记录表
- `materials` - 材料记录表
- `export_history` - 导出历史记录表

## 主要功能特性

### 1. 独立管理页面
- **修复计划列表页**：查看所有文物的修复计划，支持按文物名称、目标关键字搜索
- **过程记录时间线页**：按时间顺序展示所有修复过程，支持按时间段、类别筛选
- **影像资料库页**：网格形式展示所有影像，支持图片放大预览、阶段筛选
- **材料管理页**：显示所有材料汇总，包含统计信息（总数、种类数、关联文物数）

### 2. 批量导出
- 支持多选文物批量导出
- 支持 TXT 和 JSON 两种导出格式
- 自动保存导出历史记录
- 支持查看导出历史

### 3. 首页统计
- 统一的统计API数据来源
- 包含文物、计划、过程、影像、材料五个统计项
- 统计卡片点击可快速跳转到对应页面

### 4. 性能优化
- 文物详情页Tab懒加载：只在用户首次切换时请求数据
- 已加载数据缓存，避免重复请求

### 5. 图片预览
- 使用 Element Plus ImageViewer 组件
- 点击图片放大查看
- 支持幻灯片播放
- 加载失败容错处理

### 6. 表单验证
- 完整的表单验证规则
- 必填验证、长度限制、格式验证
- 友好的错误提示

### 7. 全局错误处理
- 统一的Axios响应拦截器
- HTTP错误码分类处理
- 网络错误友好提示

## 日志文件

日志文件存储在 `backend/logs/` 目录下，按日期命名（如 `app_20260510.log`）。

## 文档

详细文档请参考：
- [系统设计文档](./docs/系统设计文档.md)
- [使用说明](./docs/使用说明.md)
