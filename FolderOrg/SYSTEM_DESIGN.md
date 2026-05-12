# 文件夹自动整理工具 - 系统设计文档

## 目录

- [1. 项目概述](#1-项目概述)
  - [1.1 项目背景](#11-项目背景)
  - [1.2 目标](#12-目标)
  - [1.3 技术栈](#13-技术栈)
- [2. 系统架构](#2-系统架构)
  - [2.1 整体架构](#21-整体架构)
  - [2.2 模块关系图](#22-模块关系图)
- [3. 核心模块设计](#3-核心模块设计)
- [4. 数据流程](#4-数据流程)
- [5. 性能设计](#5-性能设计)
- [6. 测试策略](#6-测试策略)
- [7. 安全设计](#7-安全设计)
- [8. 部署和使用](#8-部署和使用)
- [9. 扩展和维护](#9-扩展和维护)
- [10. 版本历史](#10-版本历史)

---

## 架构概览

FolderOrg 是一个模块化的文件整理工具，采用分层架构设计：

```
┌─────────────────────────────────────────────────────────────────┐
│                        命令行接口层                              │
│  main.py (organize, restore, history, cleanup, schedule, config)│
└──────────────────────────┬──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────┐
│  配置管理层       │ │ 任务调度层 │ │ 日志记录层    │
│  ConfigManager   │ │ Scheduler│ │    Logger    │
└────────┬─────────┘ └────┬─────┘ └──────────────┘
         │                │
         ▼                ▼
┌──────────────────┐ ┌────────────────────────────┐
│  文件分类层       │ │     文件整理层             │
│  FileClassifier  │ │      FileOrganizer         │
│  (扩展名映射)      │ │ (扫描/移动/历史/清理)      │
└────────┬─────────┘ └──────────┬─────────────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
         ┌──────────────────┐
         │   文件还原层      │
         │   FileRestorer   │
         └──────────────────┘
```

**核心数据流：**
1. **用户输入** → CLI层解析参数
2. **配置加载** → ConfigManager读取配置
3. **文件扫描** → FileOrganizer递归/非递归扫描
4. **类型识别** → FileClassifier根据扩展名分类
5. **文件移动** → 保持结构或扁平化模式
6. **历史记录** → 每个源目录独立存储
7. **清理维护** → 保守/激进两种清理模式

---

## 1. 项目概述

### 1.1 项目背景
文件夹自动整理工具是一个基于Python的自动化脚本，用于帮助用户自动整理文件夹内容。通过识别文件类型并根据配置规则将文件移动到对应目录，保持文件夹的整洁有序。

### 1.2 目标
- 自动识别文件类型（文档、图片、视频、音频、压缩包等）
- 根据配置规则将文件移动到对应分类目录
- 支持递归处理子目录，保持相对路径结构
- 支持自定义分类规则和目标目录
- 支持定时自动执行整理任务
- 生成整理日志，记录移动的文件信息
- 提供还原功能，可将文件移回原位置
- 支持历史记录清理，提供保守/激进两种模式
- 每个源目录使用独立的历史记录文件，实现多目录隔离

### 1.3 技术栈
- **编程语言**: Python 3.12
- **配置管理**: json（标准库）
- **定时任务**: schedule
- **测试框架**: pytest + Allure
- **代码规范**: PEP8

## 2. 系统架构

### 2.1 整体架构

```
FolderOrg/
├── config/                    # 配置文件目录
│   └── default_config.json    # 默认配置文件
├── folder_organizer/          # 核心包
│   ├── __init__.py            # 包初始化
│   ├── config_manager.py      # 配置管理模块
│   ├── file_classifier.py     # 文件类型识别模块
│   ├── file_organizer.py      # 文件整理核心模块
│   ├── file_restorer.py       # 文件还原模块
│   ├── logger.py              # 日志记录模块
│   └── scheduler.py           # 定时任务模块
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py            # pytest配置和夹具
│   ├── test_config_manager.py
│   ├── test_file_classifier.py
│   ├── test_file_organizer.py
│   └── test_file_restorer.py
├── main.py                    # 主入口脚本
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明文档
```

### 2.2 模块关系图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        main.py (CLI)                                │
│         命令行界面/入口控制 (organize, restore, history, cleanup)   │
└──────────────┬──────────────────┬──────────────────┬───────────────┘
               │                  │                  │
               ▼                  ▼                  ▼
┌──────────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   ConfigManager      │  │    Scheduler     │  │     Logger      │
│   (配置管理)          │  │   (定时任务)      │  │   (日志记录)     │
└──────────┬───────────┘  └────────┬─────────┘  └─────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────────┐  ┌────────────────────────────────────────┐
│   FileClassifier     │  │         FileOrganizer                   │
│   (文件分类)          │  │  (文件整理 + 递归扫描 + 历史清理)        │
└──────────┬───────────┘  └────────┬───────────────┬───────────────┘
           │                       │               │
           └──────────┬────────────┘               ▼
                      ▼                  ┌────────────────────────┐
           ┌──────────────────┐         │  History Management    │
           │   FileRestorer   │         │  (独立历史文件 + 清理)   │
           │   (文件还原)      │         └────────────────────────┘
           └──────────────────┘
```

## 3. 核心模块设计

### 3.1 ConfigManager（配置管理模块）

**职责**: 管理配置文件的加载、保存和验证

**类结构**:
```python
class ConfigManager:
    def __init__(self, config_path: Optional[str] = None)
    def get_config(self) -> Dict[str, Any]
    def set_config(self, key: str, value: Any) -> None
    def get(self, key: str, default: Any = None) -> Any
    def save_config(self, path: Optional[str] = None) -> None
    def add_category(self, name: str, extensions: list, target_dir: str) -> None
    def remove_category(self, name: str) -> bool
    def validate_config(self) -> bool
```

**配置格式**:
```json
{
    "source_dir": "",
    "categories": {
        "documents": {
            "extensions": [".pdf", ".doc", ".docx"],
            "target_dir": "Documents"
        },
        "images": {
            "extensions": [".jpg", ".png", ".gif"],
            "target_dir": "Images"
        }
    },
    "schedule": {
        "enabled": false,
        "interval": {
            "type": "daily",
            "value": "00:00"
        }
    },
    "logging": {
        "log_dir": "logs",
        "log_level": "INFO",
        "max_log_size": 10485760,
        "backup_count": 5
    }
}
```

### 3.2 FileClassifier（文件类型识别模块）

**职责**: 根据文件扩展名识别文件类型并匹配到对应的分类

**类结构**:
```python
class FileClassifier:
    def __init__(self, categories: Dict[str, Dict])
    def get_file_extension(self, file_path: str) -> str
    def classify_file(self, file_path: str) -> Tuple[str, Optional[str]]
    def get_category_target_dir(self, category_name: str) -> Optional[str]
    def list_categories(self) -> List[str]
    def get_category_extensions(self, category_name: str) -> List[str]
    def is_extension_in_category(self, extension: str, category_name: str) -> bool
    def update_categories(self, categories: Dict[str, Dict]) -> None
```

**核心逻辑**:
1. 构建扩展名到分类名称的映射表
2. 根据文件扩展名查找对应的分类
3. 支持大小写不敏感的扩展名匹配
4. 未匹配的文件归类为 "others"

### 3.3 FileOrganizer（文件整理核心模块）

**职责**: 扫描文件、移动文件到目标目录、记录移动历史、清理历史记录

**类结构**:
```python
class FileOrganizer:
    def __init__(self, source_dir: str, classifier: FileClassifier, 
                 move_history_file: Optional[str] = None, recursive: bool = False)
    def _ensure_history_dir_exists(self) -> None
    def _load_move_history(self) -> None
    def _save_move_history(self) -> None
    def scan_files(self) -> List[str]
    def move_file(self, file_path: str, relative_dir: Optional[str] = None) -> Tuple[bool, Optional[str], str]
    def organize(self, recursive: bool = None) -> Dict[str, Any]
    def get_move_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]
    def clear_history(self) -> None
    def cleanup_invalid_history(self, mode: str = "conservative", dry_run: bool = False) -> Dict[str, Any]
```

**核心逻辑**:

1. **递归扫描**
   - 支持 `recursive` 参数控制是否递归扫描子目录
   - 递归模式使用 `os.walk()` 遍历所有子目录
   - 扫描时自动排除 `.folderorg_history.json` 文件
   - 记录每个文件相对于源目录的路径

2. **保持路径结构**
   - 递归整理时在目标分类目录中保持相同的相对路径结构
   - 避免不同子目录中的同名文件冲突
   - 还原时能准确恢复到原位置

3. **历史记录管理**
   - **默认路径**: `{source_dir}/.folderorg_history.json`
   - **设计优势**: 
     - 每个源目录使用独立的历史文件
     - 实现多目录操作隔离
     - 历史文件与源数据一起存储，便于备份迁移
   - **权限处理**: 捕获 PermissionError 和 OSError，避免源目录只读时初始化失败

4. **历史清理功能**

   支持两种清理模式：

   | 模式 | 清理范围 | 使用场景 |
   |------|---------|---------|
   | conservative | 只清理格式不完整的记录 | 日常维护，不影响还原 |
   | aggressive | 清理格式不完整和目标文件不存在的记录 | 释放存储空间 |

   **保守模式清理条件**:
   - 缺少 `source_path` 字段
   - 缺少 `target_path` 字段
   - 缺少 `timestamp` 字段

   **激进模式额外清理条件**:
   - 目标文件已不存在于文件系统中

5. **预览机制**
   - 支持 `dry_run=True` 参数预览要清理的记录
   - 不实际修改历史文件
   - 帮助用户确认清理范围

**移动历史格式**:
```json
[
    {
        "source_path": "/path/to/source/file.pdf",
        "target_path": "/path/to/target/Documents/file.pdf",
        "category": "documents",
        "timestamp": "2024-01-01T12:00:00",
        "relative_dir": "subdir/nested"
    }
]
```

**递归整理示例**:

源目录结构:
```
/source/
├── file1.pdf
├── subdir/
│   ├── file2.jpg
│   └── nested/
│       └── file3.txt
```

递归整理后 (`--recursive`):
```
/source/
├── Documents/
│   ├── file1.pdf
│   └── subdir/
│       └── nested/
│           └── file3.txt
├── Images/
│   └── subdir/
│       └── file2.jpg
└── .folderorg_history.json
```

### 3.4 FileRestorer（文件还原模块）

**职责**: 根据移动历史记录将文件还原到原位置

**类结构**:
```python
class FileRestorer:
    def __init__(self, move_history: List[Dict[str, Any]])
    def restore_file(self, history_entry: Dict[str, Any]) -> bool
    def restore_last(self, count: int = 1) -> Dict[str, Any]
    def restore_by_category(self, category: str) -> Dict[str, Any]
    def restore_all(self) -> Dict[str, Any]
    def get_restore_history(self) -> List[Dict[str, Any]]
    def update_history(self, move_history: List[Dict[str, Any]]) -> None
```

**核心逻辑**:
1. 从历史记录中获取源路径和目标路径
2. 验证目标文件是否存在
3. 生成唯一的还原路径（避免文件覆盖）
4. 移动文件回原位置
5. 提供按分类还原和全部还原功能

### 3.5 Logger（日志记录模块）

**职责**: 提供统一的日志记录功能，支持控制台和文件输出

**类结构**:
```python
class Logger:
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO",
                 max_log_size: int = 10485760, backup_count: int = 5)
    def info(self, message: str) -> None
    def debug(self, message: str) -> None
    def warning(self, message: str) -> None
    def error(self, message: str) -> None
    def critical(self, message: str) -> None
    def log_organize_result(self, result: dict) -> None
    def log_file_moved(self, source: str, target: str, category: str) -> None
    def log_file_restore(self, source: str, target: str) -> None
    def log_schedule_start(self) -> None
    def log_schedule_stop(self) -> None
```

**核心特性**:
1. 使用RotatingFileHandler实现日志文件轮转
2. 同时输出到控制台和日志文件
3. 支持自定义日志级别和文件大小限制
4. 提供专用方法记录整理结果和文件操作

### 3.6 Scheduler（定时任务模块）

**职责**: 基于schedule库实现定时文件整理功能

**类结构**:
```python
class Scheduler:
    def __init__(self, organize_func: Callable[[], Dict[str, Any]])
    def set_logger(self, logger: Any) -> None
    def start(self) -> bool
    def stop(self) -> bool
    def schedule_daily(self, time_str: str = "00:00") -> None
    def schedule_hourly(self, interval: int = 1) -> None
    def schedule_minutes(self, interval: int = 30) -> None
    def schedule_weekly(self, day: str = "monday", time_str: str = "00:00") -> None
    def is_running(self) -> bool
    def get_pending_jobs(self) -> list
```

**核心逻辑**:
1. 支持多种定时类型：每日、每小时、每分钟、每周
2. 使用后台线程运行定时任务
3. 与Logger集成记录任务执行情况
4. 提供启动、停止和状态查询接口

## 4. 数据流程

### 4.1 文件整理流程（普通模式）

```
1. 用户运行 python main.py organize -s /path/to/dir
   │
   ▼
2. CLI 初始化 ConfigManager、Logger、FileClassifier
   │
   ▼
3. 创建 FileOrganizer 实例（使用源目录下的历史文件）
   │
   ▼
4. scan_files() 扫描源目录（只扫描直接文件）
   │
   ▼
5. 遍历文件，对每个文件：
   ├── classify_file() 识别文件类型
   ├── _generate_unique_path() 生成唯一目标路径
   ├── shutil.move() 移动文件
   └── _add_to_history() 记录移动历史
   │
   ▼
6. 返回整理结果
   │
   ▼
7. Logger 记录整理统计信息
   │
   ▼
8. CLI 输出结果到控制台
```

### 4.2 文件整理流程（递归模式）

```
1. 用户运行 python main.py organize -s /path/to/dir --recursive
   │
   ▼
2. CLI 初始化各组件，设置 recursive=True
   │
   ▼
3. 创建 FileOrganizer 实例
   │
   ▼
4. scan_files() 使用 os.walk() 递归扫描所有子目录
   ├── 记录每个文件的相对路径
   └── 排除 .folderorg_history.json 文件
   │
   ▼
5. 遍历文件，对每个文件：
   ├── classify_file() 识别文件类型
   ├── 构建目标路径（分类目录 + 相对路径）
   ├── _generate_unique_path() 生成唯一目标路径
   ├── 确保目标目录存在
   ├── shutil.move() 移动文件
   └── _add_to_history() 记录移动历史（含 relative_dir）
   │
   ▼
6. 返回整理结果
   │
   ▼
7. CLI 输出结果到控制台
```

**路径保持设计说明**:
- 递归模式保持相对路径结构的原因：
  1. **文件定位**: 用户可以在分类目录中找到原有的子目录结构
  2. **避免冲突**: 不同子目录中的同名文件不会冲突
  3. **准确还原**: 还原时能精确恢复到原位置
- 相对路径示例：`subdir/nested/file.txt` → `Documents/subdir/nested/file.txt`

### 4.3 历史记录清理流程

```
1. 用户运行 python main.py cleanup --mode aggressive --dry-run
   │
   ▼
2. CLI 解析参数：mode=aggressive, dry_run=True
   │
   ▼
3. 创建 FileOrganizer 实例，加载历史文件
   │
   ▼
4. cleanup_invalid_history(mode="aggressive", dry_run=True)
   │
   ▼
5. 遍历所有历史记录，判断是否为无效记录：
   ├── 保守模式检查：格式是否完整？
   │   ├── 缺少 source_path? → 无效
   │   ├── 缺少 target_path? → 无效
   │   └── 缺少 timestamp? → 无效
   │
   └── 激进模式额外检查：
       └── os.path.exists(target_path)? → 不存在则无效
   │
   ▼
6. 统计待清理记录
   │
   ▼
7. dry_run=True → 不保存，返回预览结果
   │
   ▼
8. CLI 输出预览信息：
   ├── 保守模式：直接执行
   └── 激进模式：
       ├── 检查 --yes/--force 参数
       ├── 无参数 → 询问用户确认
       └── 用户确认 → 执行清理
```

### 4.2 文件还原流程

```
1. 用户运行 python main.py restore --last 5
   │
   ▼
2. CLI 初始化各组件
   │
   ▼
3. FileOrganizer 加载移动历史
   │
   ▼
4. 创建 FileRestorer 实例
   │
   ▼
5. restore_last() 处理最近5条记录：
   ├── 检查目标文件是否存在
   ├── 生成唯一还原路径
   ├── shutil.move() 移动文件
   └── 记录还原操作日志
   │
   ▼
6. 返回还原结果
   │
   ▼
7. CLI 输出结果到控制台
```

## 5. 性能设计

### 5.1 性能目标
- 处理1000个文件时，整理时间不超过30秒

### 5.2 性能优化策略

1. **批量操作**: 一次性扫描所有文件，避免重复I/O
2. **内存优化**: 使用生成器和迭代器，避免一次性加载所有数据
3. **高效的映射表**: 使用字典构建扩展名映射，O(1)复杂度查找
4. **异常处理**: 捕获并记录异常，避免单个文件失败导致整体崩溃
5. **历史记录管理**: 限制历史记录大小，定期清理

### 5.3 测试验证
- 单元测试中包含 `test_performance_large_files` 用例
- **测试设计**: 
  - 同一目录多次运行（3次取平均）
  - 每次运行后清理并重新创建测试文件
  - 消除文件系统缓存影响
  - 测试不同大小的文件（1KB, 10KB, 100KB, 1MB）
- **验证目标**: 处理1000个文件平均时间 ≤ 30秒

## 6. 测试策略

### 6.1 测试框架
- **pytest**: 核心测试框架
- **allure-pytest**: 生成可视化测试报告
- **pytest-cov**: 计算代码覆盖率

### 6.2 测试覆盖

**单元测试覆盖**:
1. **ConfigManager**: 配置加载、保存、增删改查、验证
2. **FileClassifier**: 文件分类、扩展名处理、分类管理
3. **FileOrganizer**: 
   - 文件扫描（递归/非递归）
   - 文件移动、整理
   - 历史记录管理
   - 历史记录清理（保守/激进模式）
   - 多目录隔离
   - 性能测试
4. **FileRestorer**: 
   - 单个文件还原
   - 批量还原
   - 按分类还原
   - 递归还原

**新增测试文件**:
- `tests/test_recursive_and_isolation.py` (9个测试用例)
  - 递归扫描测试
  - 非递归扫描测试
  - 递归整理保持结构测试
  - 多目录历史隔离测试
- `tests/test_cleanup_history.py` (11个测试用例)
  - 保守模式清理测试
  - 激进模式清理测试
  - dry-run预览测试

**覆盖率目标**: ≥80%

### 6.3 测试夹具 (Fixtures)
- `temp_dir`: 创建临时测试目录，测试后自动清理
- `test_categories`: 提供标准测试分类配置
- `test_files`: 在临时目录中创建测试文件

## 7. 安全设计

### 7.1 安全考虑

1. **路径验证**: 确保所有操作都在预期目录内
2. **文件权限**: 检查文件读写权限
3. **异常处理**: 捕获所有可能的IO异常
4. **日志安全**: 不记录敏感信息
5. **配置验证**: 验证配置文件的有效性

### 7.2 风险缓解

1. **文件覆盖保护**: 使用 `_generate_unique_path()` 避免文件覆盖
2. **原子操作**: 使用 `shutil.move()` 确保操作原子性
3. **历史记录**: 所有移动操作都有记录，可追溯
4. **还原功能**: 提供还原机制，可回滚操作
5. **权限错误处理**: 
   - `_ensure_history_dir_exists()` 捕获 PermissionError 和 OSError
   - 源目录只读时不会导致初始化失败
   - 优雅的降级处理，保持工具可用性
6. **历史文件隔离**: 
   - 每个源目录独立历史文件
   - 不会因一个目录的问题影响其他目录
   - 备份和迁移更方便

## 8. 部署和使用

### 8.1 安装依赖
```bash
pip install -r requirements.txt
```

### 8.2 基本使用

**整理文件夹**:
```bash
# 只整理当前目录的直接文件
python main.py organize -s /path/to/your/folder

# 递归整理所有子目录（保持相对路径结构）
python main.py organize -s /path/to/your/folder -r
# 或者
python main.py organize -s /path/to/your/folder --recursive
```

**清理历史记录**:
```bash
# 预览要清理的内容
python main.py cleanup --dry-run

# 保守模式（默认，只清理格式不完整的记录）
python main.py cleanup --mode conservative

# 激进模式（需要确认）
python main.py cleanup --mode aggressive

# 激进模式（跳过确认）
python main.py cleanup --mode aggressive --yes
# 或者
python main.py cleanup --mode aggressive --force
```

**还原文件**:
```bash
# 还原最近5个文件
python main.py restore --last 5

# 还原指定分类的所有文件
python main.py restore --category documents

# 还原所有文件
python main.py restore --all
```

**查看历史**:
```bash
python main.py history --limit 10
```

**定时整理**:
```bash
# 每天凌晨2点执行
python main.py schedule --type daily --time 02:00

# 每小时执行一次
python main.py schedule --type hourly --interval 1
```

**管理配置**:
```bash
# 查看当前配置
python main.py config --list

# 添加新分类
python main.py config --add-category ebooks --extensions ".epub,.mobi,.azw" --target-dir EBooks
```

### 8.3 配置文件

默认配置文件位置: `config/default_config.json`

可通过命令行或直接编辑配置文件来自定义:
- 文件分类规则
- 目标目录名称
- 日志配置
- 定时任务配置

## 9. 扩展和维护

### 9.1 扩展点

1. **自定义分类**: 通过配置文件或命令行添加新的文件分类
2. **自定义规则**: 可扩展FileClassifier支持更复杂的分类规则
3. **通知机制**: 可添加邮件、微信等通知功能
4. **云存储集成**: 可扩展支持云存储文件夹整理

### 9.2 维护指南

1. **日志管理**: 定期检查日志文件，清理过期日志
2. **配置备份**: 定期备份配置文件
3. **历史记录**: 定期清理不需要的历史记录
4. **性能监控**: 监控整理时间，确保在性能目标内

## 10. 版本历史

### v1.1.0 (2024)
- ✨ **递归整理功能**: 新增 `--recursive` / `-r` 参数
- 🔧 **路径保持设计**: 递归模式保持相对路径结构
- 📁 **历史文件隔离**: 每个源目录使用独立的 `.folderorg_history.json`
- ✨ **历史清理功能**: 新增 `cleanup` 命令
- 🔧 **双模式清理**: 保守模式和激进模式
- ✨ **预览功能**: `--dry-run` 参数预览清理效果
- 🔧 **交互设计**: `--yes` / `--force` 参数跳过确认
- 🔧 **权限处理**: 增强权限错误处理，避免只读目录初始化失败
- 🔧 **性能测试**: 改进测试设计，同一目录反复运行消除缓存影响
- 📝 **文档更新**: 更新README和SYSTEM_DESIGN文档
- 🧪 **测试增强**: 新增20+测试用例，覆盖率保持92%

### v1.0.0 (2024)
- 初始版本发布
- 实现文件分类和整理功能
- 实现文件还原功能
- 实现定时任务功能
- 实现日志记录功能
- 完整的单元测试（覆盖率≥80%）
- Allure测试报告支持
