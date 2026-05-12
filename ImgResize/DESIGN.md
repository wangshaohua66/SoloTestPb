# 系统设计文档

## 1. 项目概述

### 1.1 项目名称
图片批量压缩调整工具 (ImgResize)

### 1.2 项目简介
一个基于Python的图片批量处理自动化工具，支持压缩、调整尺寸、格式转换、添加水印等功能。采用模块化设计，支持并发处理，能够高效处理大量图片。

### 1.3 目标用户
- 摄影师、电商运营人员
- 网站开发人员
- 需要批量处理图片的用户

---

## 2. 需求分析

### 2.1 功能需求

| 功能模块 | 功能描述 | 优先级 |
|---------|---------|--------|
| 尺寸调整 | 支持设置宽度和高度，多种缩放模式 | 高 |
| 比例缩放 | 按比例放大或缩小图片 | 高 |
| 质量压缩 | 控制输出质量，优化文件大小 | 高 |
| 格式转换 | 支持JPG、PNG、WEBP、GIF等格式互转 | 高 |
| 文字水印 | 支持自定义文字水印，支持位置、透明度、旋转、平铺 | 中 |
| 图片水印 | 支持自定义图片水印，支持位置、透明度、缩放、平铺 | 中 |
| EXIF处理 | 可选保留或清除原图EXIF信息，支持自动方向校正 | 中 |
| 并发处理 | 多进程/多线程并发处理，提高处理效率 | 高 |

### 2.2 非功能需求

| 需求类型 | 具体描述 | 指标 |
|---------|---------|------|
| 性能 | 处理100张图片 | ≤60秒 |
| 代码规范 | 遵循PEP8规范 | 100% |
| 测试覆盖率 | 单元测试覆盖率 | ≥80% |
| 可扩展性 | 模块化设计，易于扩展 | 满足 |
| 文档完整性 | 提供完整的使用文档和API文档 | 满足 |

---

## 3. 系统架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户层                          │
│  ┌────────────────────────────────────────────┐    │
│  │              CLI命令行接口                     │    │
│  └────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────┐    │
│  │              Python API                 │    │
│  └────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              业务逻辑层                    │
│  ┌────────────┐  ┌────────────┐        │
│  │批量处理器   │  │配置管理       │        │
│  │(BatchProcessor) │  │(ProcessingConfig)│        │
│  └────────────┘  └────────────┘        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              核心处理层                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │图像处理器   │ │水印处理器   │ │EXIF处理器   ││
│  │(ImageProc) │ │(Watermark) │ │(ExifHandler)││
│  └────────────┘ └────────────┘ └────────────┘│
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              基础设施层                    │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │Pillow     │ │concurrent │ │pathlib    ││
│  │(PIL)    │ │.futures   │ │(路径处理)  ││
│  └────────────┘ └────────────┘ └────────────┘│
└─────────────────────────────────────────────────┘
```

### 3.2 模块划分

#### 3.2.1 核心处理层

##### ImageProcessor（图像处理模块

**职责**: 
- 图片加载与保存
- 尺寸调整（多种模式）
- 比例缩放
- 质量压缩
- 格式转换

**关键类**: `ImageProcessor`

**主要方法**:
- `load_image()`: 加载图片
- `save_image()`: 保存图片
- `resize_image()`: 调整尺寸
- `scale_image()`: 比例缩放
- `compress_image()`: 压缩图片
- `convert_format()`: 格式转换

---

##### Watermark（水印模块）

**职责**:
- 文字水印添加
- 图片水印添加
- 水印位置计算
- 水印透明度、缩放处理

**关键类**: `Watermark`

**主要方法**:
- `add_text_watermark()`: 添加文字水印
- `add_image_watermark()`: 添加图片水印
- `_calculate_position()`: 计算水印位置

---

##### ExifHandler（EXIF模块）

**职责**:
- EXIF信息读取
- EXIF信息复制
- EXIF信息清除
- 图片方向自动校正

**关键类**: `ExifHandler`

**主要方法**:
- `read_exif()`: 读取EXIF信息
- `copy_exif()`: 复制EXIF信息
- `strip_exif()`: 清除EXIF信息
- `apply_orientation()`: 应用方向校正

---

#### 3.2.2 业务逻辑层

##### BatchProcessor（批量处理模块）

**职责**:
- 批量图片文件扫描
- 并发任务调度
- 进度跟踪
- 结果统计

**关键类**: `BatchProcessor`

**主要方法**:
- `get_image_files()`: 获取图片文件列表
- `process_single_image()`: 处理单张图片
- `process_batch()`: 批量处理

**关键数据结构**:
- `ProcessingConfig`: 处理配置
- `ProcessingResult`: 单张处理结果
- `BatchResult`: 批量处理结果

---

#### 3.2.3 用户接口层

##### CLI（命令行接口

**职责**:
- 命令行参数解析
- 用户交互
- 进度显示
- 错误处理

**主要函数**:
- `parse_args()`: 解析命令行参数
- `create_config_from_args()`: 转换为处理配置
- `main()`: 主入口

---

## 4. 核心设计模式

### 4.1 模块间的关键设计决策

### 4.1 类设计

**单例模式？不使用，允许多个实例独立处理不同的可扩展性

### 4.2 处理流程

```
输入目录
    │
    ▼
┌─────────────┐
│ 扫描文件   │
└──────┬────┘
       │
       ▼
┌─────────────┐
│ 创建任务列表 │
└──────┬────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ 并发执行 (ProcessPoolExecutor / ThreadPoolExecutor) │
│  ┌─────┐  ┌─────┐  ┌─────┐        │
│  │Worker│  │Worker│  │Worker│        │
│  └─────┘  └─────┘  └─────┘        │
└──────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│ 收集处理结果     │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 输出到目录      │
└──────────────────┘
```

### 4.3 关键数据结构

#### ProcessingConfig（处理配置）

```python
@dataclass
class ProcessingConfig:
    # 尺寸调整
    width: Optional[int] = None
    height: Optional[int] = None
    resize_mode: ResizeMode = ResizeMode.FIT
    scale: Optional[float] = None
    
    # 格式与压缩
    quality: int = 85
    output_format: Optional[ImageFormat] = None
    
    # EXIF处理
    keep_exif: bool = True
    auto_orient: bool = True
    
    # 水印配置
    # ...
```

#### BatchResult（批量结果

```python
@dataclass
class BatchResult:
    total_count: int          # 总文件数
    success_count: int       # 成功数
    failed_count: int        # 失败数
    total_time: float      # 总耗时
    results: List[ProcessingResult]  # 详细结果
    
    @property
    def success_rate(self) -> float: 成功率
    @property
    def average_time(self) -> float: 平均耗时
```

---

## 5. 接口设计

### 5.1 公共API

```python
# 命令行接口
img-resize -i INPUT -o OUTPUT [OPTIONS]

# Python API
from img_resize import BatchProcessor, ProcessingConfig

processor = BatchProcessor(max_workers=4)
config = ProcessingConfig(
    width=1920,
    quality=85,
    output_format=ImageFormat.WEBP
)
result = processor.process_batch(
    input_dir="./input",
    output_dir="./output",
    config=config
)
```

### 5.2 模块依赖关系

```
cli.py
    ├── image_processor.py
    ├── watermark.py
    ├── exif_handler.py
    └── batch_processor.py
            ├── image_processor.py
            ├── watermark.py
            └── exif_handler.py
```

---

## 6. 技术选型

### 6.1 技术栈

| 组件 | 技术 | 选型理由 |
|------|------|---------|
| 编程语言 | Python 3.12 | 现代Python特性，类型提示支持 |
| 图像处理 | Pillow 10.x | Python生态最成熟的图像处理库 |
| 并发处理 | concurrent.futures | 标准库，易于使用 |
| 测试框架 | pytest + Allure | 功能强大，支持Allure报告 |
| 代码规范 | PEP8 | Python官方规范 |

### 6.2 依赖关系

```
┌────────────────────────────────────────┐
│         项目代码 (img_resize)     │
└────────┬───────────────────────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
┌──────┐ ┌──────┐ ┌──────┐
│Pillow│ │concurrent│ │pathlib│
└──────┘ └──────┘ └──────┘
```

---

## 7. 性能优化策略

### 7.1 并发优化

1. **多进程并发: 图片处理是CPU密集型任务，使用ProcessPoolExecutor
2. **工作线程数: 默认使用CPU核心数，可自定义
3. **任务粒度: 单张图片为一个任务

### 7.2 内存优化

1. **流式处理: 单张图片处理完成后立即释放
2. **延迟加载: 按需加载图片
3. **及时保存: 处理完成后立即保存到磁盘

### 7.3 I/O优化

1. **目录扫描: 使用pathlib高效路径处理
2. **批量写入: 并发写入不同文件

---

## 8. 错误处理

### 8.1 异常类型

| 异常类型 | 触发场景 | 处理方式 |
|---------|---------|---------|
| FileNotFoundError | 输入文件不存在 | 记录错误，跳过处理失败计数 |
| IOError | 文件读写错误 | 记录错误，跳过 |
| ValueError | 参数错误 | 记录错误，提示用户 |
| Exception | 其他异常 | 统一捕获，记录详细错误 |

### 8.2 错误处理策略

```python
try:
    # 处理图片
except Exception as e:
    logger.error(f"处理图片失败: {input_path}, 错误: {e}")
    result.success = False
    result.error_message = str(e)
```

---

## 9. 测试策略

### 9.1 测试分层

| 测试类型 | 测试目标 | 覆盖率 |
|---------|---------|--------|
| 单元测试 | 模块功能测试 | 87% |
| 集成测试 | 模块间交互 | 包含 |
| 性能测试 | 100张图片 <60秒 | 验证 |

### 9.2 测试用例设计

**ImageProcessor测试**
- 测试用例数: 27个
- 覆盖: 加载、保存、缩放、格式转换等

**Watermark测试**
- 测试用例数: 18个
- 覆盖: 文字水印、图片水印、位置计算等

**ExifHandler测试**
- 测试用例数: 14个
- 覆盖: EXIF读取、复制、清除等

**BatchProcessor测试**
- 测试用例数: 19个
- 覆盖: 文件扫描、单张处理、批量处理等

**CLI测试**
- 测试用例数: 10个
- 覆盖: 参数解析、配置转换、主流程等

---

## 10. 部署与使用

### 10.1 安装步骤

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 开发模式安装
```bash
pip install -e .
```

3. 运行测试
```bash
pytest tests/
```

### 10.2 使用方式

**命令行方式
```bash
img-resize -i ./input -o ./output --width 800 --quality 80
```

**Python API方式
```python
from img_resize import BatchProcessor, ProcessingConfig

processor = BatchProcessor(max_workers=4)
config = ProcessingConfig(width=800, quality=80)
result = processor.process_batch("./input", "./output", config)
```

---

## 11. 扩展规划

### 11.1 可扩展点

1. **新格式支持**: 可扩展支持更多图片格式
2. **智能压缩算法: 可扩展自定义压缩算法
3. **新水印类型: 可扩展更多水印类型
4. **Web界面: 可扩展Web管理界面

### 11.2 后续功能规划

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 动态GIF支持 | 支持动画GIF处理 | 中 |
| 批量重命名 | 自定义输出文件名 | 低 |
| 图像处理流水线 | 支持更复杂的处理流水线 | 低 |

---

## 12. 附录

### 12.1 术语表

| 术语 | 说明 |
|------|------|
| EXIF | 可交换图像文件格式，存储照片元数据 |
| 缩放模式 | 图片尺寸调整的策略 |
| 并发处理 | 同时处理多个任务 |
| 多进程 | 使用多个进程并发处理 |
| 多线程 | 使用多个线程并发处理 |

### 12.2 参考资料

- Pillow官方文档: https://pillow.readthedocs.io
- Python官方文档: https://docs.python.org
- concurrent.futures文档: https://docs.python.org/3/library/concurrent.futures.html
