# 文件夹自动整理工具 (FolderOrg)

一个基于Python的自动化文件夹整理工具，能够根据文件类型自动将文件移动到对应分类目录，保持文件夹整洁有序。

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
  - [环境要求](#1-环境要求)
  - [安装依赖](#2-安装依赖)
  - [基本使用](#3-基本使用)
- [核心功能](#核心功能)
  - [整理文件夹](#整理文件夹)
  - [递归整理](#递归整理说明)
  - [扁平化模式](#扁平化模式)
  - [还原文件](#还原文件)
  - [清理历史记录](#清理历史记录)
- [配置说明](#配置说明)
- [测试和性能](#测试和性能)
- [常见问题](#常见问题)
- [更新日志](#更新日志)

## 功能特性

- ✅ **自动文件分类**: 识别文档、图片、视频、音频、压缩包等多种文件类型
- ✅ **递归整理**: 支持递归处理子目录，保持相对路径结构
- ✅ **扁平化模式**: 可选的扁平化整理，所有文件直接放到分类目录
- ✅ **自定义规则**: 支持自定义分类规则和目标目录
- ✅ **定时任务**: 支持每日、每小时、每分钟、每周定时自动执行整理
- ✅ **操作日志**: 生成详细的整理日志，记录所有移动的文件信息
- ✅ **还原功能**: 可将文件一键还原到原位置
- ✅ **历史记录清理**: 支持清理无效历史记录，提供保守/激进两种模式
- ✅ **多目录隔离**: 每个源目录使用独立的历史记录文件
- ✅ **高性能**: 处理1000个文件不超过30秒
- ✅ **完整测试**: 单元测试覆盖率≥80%，支持Allure测试报告

## 快速入门指南

### 30秒上手

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 整理当前目录
python main.py organize

# 3. 递归整理子目录（保持结构）
python main.py organize -r

# 4. 递归整理并扁平化
python main.py organize -r -f
```

### 最佳实践

| 场景 | 推荐参数 | 说明 |
|------|---------|------|
| 日常下载文件夹整理 | `-r` | 保持子目录结构，便于查找 |
| 照片/视频批量整理 | `-r -f` | 扁平化，按类型集中管理 |
| 临时文件夹清理 | 无参数 | 只处理直接文件 |
| 脚本自动化 | `cleanup --mode aggressive --yes` | 无人值守清理 |

## 技术栈

- **编程语言**: Python 3.12
- **配置管理**: JSON（标准库）
- **定时任务**: schedule
- **测试框架**: pytest + Allure
- **代码规范**: PEP8

## 快速开始

### 1. 环境要求

- Python 3.12 或更高版本
- pip 包管理工具

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd FolderOrg

# 安装依赖
pip install -r requirements.txt
```

### 3. 基本使用

#### 整理文件夹

```bash
# 整理当前目录（只处理直接文件）
python main.py organize

# 整理指定目录
python main.py organize -s /path/to/your/folder

# 递归整理子目录（保持相对路径结构）
python main.py organize -s /path/to/your/folder -r
# 或者使用长选项
python main.py organize -s /path/to/your/folder --recursive
```

#### 递归整理说明

递归整理模式会扫描源目录下的所有子目录中的文件，并在目标分类目录中保持相同的目录结构。

**示例：**
```
源目录结构：
/path/to/folder/
├── file1.pdf
├── subdir/
│   ├── file2.jpg
│   └── nested/
│       └── file3.txt
```

使用 `--recursive` 整理后：
```
/path/to/folder/
├── Documents/
│   ├── file1.pdf
│   └── subdir/
│       └── nested/
│           └── file3.txt
└── Images/
    └── subdir/
        └── file2.jpg
```

**设计原因：**
- 保持原始目录结构，方便文件定位
- 避免不同子目录中的同名文件冲突
- 还原时能准确恢复到原位置

#### 扁平化模式

使用 `--flatten` 或 `-f` 参数可以将所有文件直接放到分类目录，不保持子目录结构。

**使用方法：**
```bash
# 递归整理并扁平化
python main.py organize -s /path/to/your/folder -r -f
# 或者
python main.py organize -s /path/to/your/folder --recursive --flatten
```

**示例：**
```
源目录结构：
/path/to/folder/
├── file1.pdf
├── subdir/
│   ├── file2.jpg
│   └── nested/
│       └── file3.txt
```

使用 `--recursive --flatten` 整理后：
```
/path/to/folder/
├── Documents/
│   ├── file1.pdf
│   └── file3.txt
└── Images/
    └── file2.jpg
```

**适用场景：**
- 照片/视频批量整理，按类型集中管理
- 不需要保持分类目录结构简单
- 不介意同名文件自动重命名

**两种模式对比：**

| 特性 | 保持结构模式（默认） | 扁平化模式 |
|------|----------------|---------|
| 参数 | `-r` | `-r -f` |
| 目录结构 | 保持子目录结构 | 所有文件直接在分类目录 |
| 同名文件 | 不会冲突（不同目录） | 自动重命名（`file.pdf`, `file_1.pdf`） |
| 文件定位 | 容易找到原位置 | 集中但需要搜索 |
| 适用场景 | 下载文件夹、文档整理 | 照片、视频批量整理 |

#### 还原文件

```bash
# 还原最近移动的文件（默认1个）
python main.py restore

# 还原最近5个文件
python main.py restore --last 5

# 还原指定分类的所有文件
python main.py restore --category documents

# 还原所有文件
python main.py restore --all
```

#### 查看移动历史

```bash
# 查看所有历史记录
python main.py history

# 查看最近10条记录
python main.py history --limit 10
```

#### 清理历史记录

历史记录文件存储在每个源目录下的 `.folderorg_history.json` 中。使用 `cleanup` 命令清理无效记录。

```bash
# 预览要清理的内容（不实际删除）
python main.py cleanup --dry-run

# 保守模式（默认）：只清理格式不完整的记录
python main.py cleanup
# 或显式指定
python main.py cleanup --mode conservative

# 激进模式：清理格式不完整和目标文件不存在的记录
# 需要交互式确认
python main.py cleanup --mode aggressive

# 跳过确认（适用于脚本自动化）
python main.py cleanup --mode aggressive --yes
# 或使用别名
python main.py cleanup --mode aggressive --force
```

**清理模式说明：**
- **保守模式 (conservative)**：只删除格式不完整的记录（缺少 `source_path`、`target_path` 或 `timestamp` 字段）。这种模式不会影响还原功能。
- **激进模式 (aggressive)**：除了删除格式不完整的记录外，还删除目标文件已不存在的记录。这种模式会释放存储空间，但可能影响部分还原操作。

**历史记录文件说明：**
- 每个源目录使用独立的历史记录文件，文件名：`.folderorg_history.json`
- 存储位置：源目录根目录下
- 扫描时自动排除，不会被误整理

#### 定时整理

```bash
# 每天凌晨2点执行整理
python main.py schedule --type daily --time 02:00

# 每小时执行一次
python main.py schedule --type hourly --interval 1

# 每30分钟执行一次
python main.py schedule --type minutes --interval 30

# 每周一早上9点执行
python main.py schedule --type weekly --day monday --time 09:00
```

#### 管理配置

```bash
# 查看当前配置
python main.py config --list

# 设置配置项
python main.py config --set "schedule.enabled=true"

# 添加新的文件分类
python main.py config --add-category ebooks --extensions ".epub,.mobi,.azw" --target-dir EBooks

# 删除分类
python main.py config --remove-category ebooks
```

## 项目结构

```
FolderOrg/
├── config/                    # 配置文件目录
│   └── default_config.json    # 默认配置文件
├── folder_organizer/          # 核心代码包
│   ├── __init__.py
│   ├── config_manager.py      # 配置管理模块
│   ├── file_classifier.py     # 文件类型识别模块
│   ├── file_organizer.py      # 文件整理核心模块
│   ├── file_restorer.py       # 文件还原模块
│   ├── logger.py              # 日志记录模块
│   └── scheduler.py           # 定时任务模块
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config_manager.py
│   ├── test_file_classifier.py
│   ├── test_file_organizer.py
│   └── test_file_restorer.py
├── logs/                      # 日志目录（运行时自动创建）
├── main.py                    # 主入口脚本
├── requirements.txt           # 依赖列表
├── README.md                  # 项目说明文档
└── SYSTEM_DESIGN.md           # 系统设计文档
```

## 配置说明

默认配置文件位于 `config/default_config.json`，可根据需要修改：

```json
{
    "source_dir": "",
    "categories": {
        "documents": {
            "extensions": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
            "target_dir": "Documents"
        },
        "images": {
            "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "target_dir": "Images"
        },
        "videos": {
            "extensions": [".mp4", ".avi", ".mkv", ".mov"],
            "target_dir": "Videos"
        },
        "audio": {
            "extensions": [".mp3", ".wav", ".flac", ".aac"],
            "target_dir": "Audio"
        },
        "archives": {
            "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "target_dir": "Archives"
        },
        "programs": {
            "extensions": [".exe", ".msi", ".dmg", ".pkg"],
            "target_dir": "Programs"
        },
        "others": {
            "extensions": [],
            "target_dir": "Others"
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

### 配置项说明

- **source_dir**: 默认源目录（留空表示使用当前目录）
- **categories**: 文件分类规则
  - `extensions`: 该分类对应的文件扩展名列表
  - `target_dir`: 该分类文件的目标目录名称
- **schedule**: 定时任务配置
  - `enabled`: 是否启用定时任务
  - `interval.type`: 定时类型（daily/hourly/minutes/weekly）
  - `interval.value`: 定时值（时间或间隔）
- **logging**: 日志配置
  - `log_dir`: 日志文件目录
  - `log_level`: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
  - `max_log_size`: 单个日志文件最大大小（字节）
  - `backup_count`: 保留的备份日志文件数量

## 支持的文件类型

默认支持以下文件类型分类：

| 分类 | 文件扩展名 |
|------|-----------|
| 文档 (Documents) | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .md, .rtf |
| 图片 (Images) | .jpg, .jpeg, .png, .gif, .bmp, .tiff, .tif, .webp, .svg |
| 视频 (Videos) | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm, .m4v |
| 音频 (Audio) | .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a |
| 压缩包 (Archives) | .zip, .rar, .7z, .tar, .gz, .bz2, .xz |
| 程序 (Programs) | .exe, .msi, .dmg, .pkg, .deb, .rpm, .apk |
| 其他 (Others) | 未匹配的所有文件 |

## 测试

### 运行单元测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细信息
pytest -v

# 运行指定测试文件
pytest tests/test_file_organizer.py -v
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=folder_organizer --cov-report=term-missing

# 生成HTML覆盖率报告
pytest --cov=folder_organizer --cov-report=html
```

### 生成Allure测试报告

```bash
# 运行测试并生成Allure结果
pytest --alluredir=allure-results

# 生成并打开Allure报告（需要先安装Allure命令行工具）
allure serve allure-results
```

> 注意：需要先安装Allure命令行工具才能查看报告。安装方法请参考 [Allure官方文档](https://docs.qameta.io/allure/)。

## 性能

工具经过优化，处理1000个文件的时间不超过30秒。性能优化策略包括：

- 批量文件扫描，减少I/O操作
- 使用字典映射表实现O(1)复杂度的文件类型查找
- 高效的异常处理，避免单个文件失败影响整体
- 内存友好的设计，避免一次性加载大量数据

## 安全性

- **文件保护**: 自动避免文件覆盖，重名文件会自动添加序号
- **操作可追溯**: 所有移动操作都有详细记录
- **回滚机制**: 提供完整的还原功能
- **配置验证**: 启动时验证配置文件有效性
- **异常处理**: 捕获并记录所有IO异常

## 扩展功能

### 添加自定义文件分类

1. 通过命令行添加：
```bash
python main.py config --add-category ebooks --extensions ".epub,.mobi,.azw" --target-dir EBooks
```

2. 或直接编辑配置文件 `config/default_config.json`

### 集成到其他项目

```python
from folder_organizer.config_manager import ConfigManager
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer

# 初始化
config_manager = ConfigManager()
categories = config_manager.get("categories", {})
classifier = FileClassifier(categories)
organizer = FileOrganizer("/path/to/your/folder", classifier)

# 执行整理
result = organizer.organize()
print(f"移动了 {result['moved_files']} 个文件")
```

## 常见问题

### Q: 整理时会删除文件吗？
A: 不会。工具只是移动文件，不会删除任何文件。

### Q: 如果目标目录已有同名文件怎么办？
A: 工具会自动重命名文件，例如 `file.pdf` 会变成 `file_1.pdf`。

### Q: 可以整理子目录吗？
A: 可以！使用 `--recursive` 或 `-r` 参数可以递归处理所有子目录。

```bash
python main.py organize -s /path/to/folder --recursive
```

### Q: 递归整理会保持目录结构吗？
A: 是的。递归整理会在目标分类目录中保持与源目录相同的相对路径结构，这样可以：
- 方便文件定位
- 避免同名文件冲突
- 准确还原到原位置

### Q: 历史记录文件存储在哪里？
A: 每个源目录使用独立的历史记录文件，存储在源目录根目录下的 `.folderorg_history.json`。

### Q: 清理历史记录会影响还原功能吗？
A: 取决于清理模式：
- **保守模式**：不会影响，只清理格式不完整的记录
- **激进模式**：可能影响，如果目标文件已被手动删除，相关记录会被清理

### Q: 如何跳过激进模式的确认提示？
A: 使用 `--yes` 或 `--force` 参数：
```bash
python main.py cleanup --mode aggressive --yes
```

### Q: 如何停止定时任务？
A: 在运行定时任务的终端按 `Ctrl+C` 即可停止。

### Q: 日志文件在哪里？
A: 默认在 `logs/organizer.log`，可以在配置文件中修改。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

## 更新日志

### v1.1.0 (2024)
- ✨ 新增递归整理子目录功能（`--recursive` / `-r`）
- ✨ 新增历史记录清理功能（`cleanup` 命令）
- ✨ 支持保守/激进两种清理模式（`--mode`）
- ✨ 支持预览清理效果（`--dry-run`）
- ✨ 支持跳过确认（`--yes` / `--force`）
- 🔧 改进历史记录存储（每个源目录独立文件）
- 🔧 增强权限错误处理
- 🔧 改进性能测试设计
- 📝 更新README和SYSTEM_DESIGN文档
- 🧪 新增9个递归和隔离测试用例
- 🧪 增强11个清理功能测试用例
- 📊 测试覆盖率保持92%

### v1.0.0 (2024)
- 初始版本发布
- 实现文件分类和整理功能
- 实现文件还原功能
- 实现定时任务功能
- 实现日志记录功能
- 完整的单元测试（覆盖率≥80%）
- Allure测试报告支持
