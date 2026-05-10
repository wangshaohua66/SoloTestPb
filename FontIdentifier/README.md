# 书法字体识别器

面向书法研究者和爱好者的专业书法字体识别工具。

## 项目简介

本工具用于识别书法作品的字体类型，提供字体特征说明和参考信息。支持楷书、行书、草书、隶书、篆书五种常见书法字体的识别。

## 功能特性

- **字体库**：内置常见书法字体信息，记录各字体的笔画特征、结构特点
- **特征提取**：分析输入文字的笔画形态、结构布局、书写风格等特征
- **字体识别**：根据特征匹配字体库，输出最可能的字体类型及置信度
- **图片识别**：支持上传书法作品图片，自动分析图像特征进行识别
- **特征说明**：显示识别字体的主要特征，帮助用户理解判断依据
- **相似字体**：列出相似字体类型，说明区别要点
- **结果导出**：生成识别结果报告，支持导出文本格式

## 技术栈

- **后端**：Python 3.13 + Flask
- **前端**：Vue 3 + Vite
- **数据库**：SQLite（本地文件数据库）
- **代码规范**：PEP8

## 项目结构

```
FontIdentifier/
├── backend/                    # 后端项目
│   ├── app/                    # Flask应用
│   │   ├── __init__.py         # 应用初始化
│   │   ├── routes.py           # API路由
│   │   ├── font_library.py     # 字体库
│   │   ├── feature_extractor.py # 特征提取器
│   │   ├── font_recognizer.py  # 字体识别器
│   │   ├── image_processor.py  # 图像处理模块
│   │   ├── database.py         # 数据库操作
│   │   └── report_generator.py # 报告生成器
│   ├── data/                   # 数据库文件目录
│   ├── requirements.txt        # Python依赖
│   └── run.py                  # 启动入口
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/                # API配置
│   │   │   └── index.js        # axios实例配置
│   │   ├── views/              # 页面视图
│   │   │   ├── Recognize.vue   # 识别页面（支持图片上传）
│   │   │   ├── FontLibrary.vue # 字体库页面
│   │   │   └── History.vue     # 历史记录页面
│   │   ├── assets/
│   │   │   └── style.css       # 全局样式
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── examples/                   # 示例图片目录
│   ├── example_kaishu.svg      # 楷书示例
│   ├── example_xingshu.svg     # 行书示例
│   ├── example_lishu.svg       # 隶书示例
│   └── example_zhuanshu.svg    # 篆书示例
├── logs/                       # 日志目录
│   └── app_20260510.log        # 示例日志
├── 系统设计文档.md             # 系统设计文档
└── README.md
```

## 安装与启动

### 后端启动

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（可选）：
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 启动后端服务：
```bash
python run.py
```

后端服务将在 `http://localhost:5003` 启动。

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端服务将在 `http://localhost:8003` 启动。

## 访问地址

- 前端应用：http://localhost:8003
- 后端API：http://localhost:5003

## API接口

### 健康检查
- `GET /api/health` - 检查服务状态

### 字体库
- `GET /api/fonts` - 获取所有字体信息
- `GET /api/fonts/<font_name>` - 获取指定字体详情
- `GET /api/fonts/names` - 获取字体名称列表

### 字体识别
- `POST /api/recognize` - 通过文字描述识别书法字体
  ```json
  {
    "description": "字体特征描述文本"
  }
  ```
- `POST /api/recognize/image` - 通过上传图片识别书法字体
  - 请求格式：multipart/form-data
  - 参数字段：image (图片文件)
  - 支持格式：JPG、PNG、GIF
  - 大小限制：最大5MB

### 历史记录
- `GET /api/history` - 获取识别历史
- `GET /api/history/<id>` - 获取历史记录详情

### 统计信息
- `GET /api/stats` - 获取识别统计

### 报告导出
- `GET /api/export/<id>` - 导出历史记录报告
- `POST /api/export` - 直接导出报告

## 使用说明

### 1. 字体识别

#### 方式一：文字描述识别

1. 打开浏览器访问 http://localhost:8003
2. 在"文字描述"标签页中输入您观察到的书法作品特征
3. 点击"开始识别"按钮
4. 查看识别结果、特征说明、相似字体比对
5. 可选择导出文本格式的识别报告

#### 方式二：图片上传识别

1. 打开浏览器访问 http://localhost:8003
2. 切换到"图片上传"标签页
3. 点击上传区域或拖拽图片到上传区域
4. 支持格式：JPG、PNG、GIF，大小限制：5MB
5. 点击"开始识别"按钮
6. 查看识别结果，包括图像特征分析、字体特征说明等

**注意**：图片识别功能需要安装Pillow和NumPy库：
```bash
pip3 install Pillow numpy
```

### 2. 特征描述示例

**楷书示例：**
> 这幅作品笔画方正，横平竖直，起笔和收笔都有明显的顿笔，结构规整对称，看起来非常工整。

**行书示例：**
> 这篇书法作品笔画有明显的连带，书写流畅自然，结构灵活，笔画之间有呼应关系。

**隶书示例：**
> 字体结构扁方，横向舒展，横画有蚕头燕尾特征，起笔藏锋，整体风格古朴厚重。

**篆书示例：**
> 笔画圆润流畅，粗细均匀一致，结构对称，纵向长方，没有明显的顿笔。

**草书示例：**
> 笔画大量简化和合并，连笔书写，连绵不断，符号化程度高。

### 3. 字体库浏览

1. 点击导航栏的"字体库"
2. 查看所有内置字体的基本信息
3. 点击任意字体卡片查看详细特征
4. 了解各字体的笔画、结构、风格特征

### 4. 历史记录

1. 点击导航栏的"历史记录"
2. 查看所有识别历史
3. 可查看详情或导出报告

## 代码规范

- 后端代码遵循 PEP8 规范
- 所有函数和类都有中文注释说明
- 数据库使用 SQLite 本地文件

## 许可证

本项目仅供学习研究使用。
