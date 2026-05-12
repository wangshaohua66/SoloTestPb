# 批量文件重命名工具 - 系统设计文档

## 1. 项目概述

### 1.1 项目名称
批量文件重命名工具 (Batch Rename Tool)

### 1.2 项目目标
提供一个功能强大、易于使用的批量文件重命名命令行工具，支持多种命名规则和模式，帮助用户快速整理大量文件。

### 1.3 目标用户
- 需要整理大量照片的摄影爱好者
- 需要统一命名规范的开发人员
- 需要归档文件的办公人员
- 需要批量处理文件的任何用户

## 2. 需求分析

### 2.1 功能需求

| 编号 | 功能名称 | 功能描述 | 优先级 |
|------|----------|----------|--------|
| FR-01 | 按序号重命名 | 按照指定的起始序号和填充位数批量重命名文件 | 高 |
| FR-02 | 按日期时间戳重命名 | 使用当前日期时间或自定义格式重命名文件 | 高 |
| FR-03 | 查找替换 | 查找并替换文件名中的特定字符串 | 高 |
| FR-04 | 添加前缀/后缀 | 为文件名添加前缀或后缀 | 高 |
| FR-05 | 正则表达式匹配替换 | 支持复杂的正则匹配和替换，包括反向引用 | 高 |
| FR-06 | 预览功能 | 在执行重命名前显示重命名结果 | 高 |
| FR-07 | 撤销功能 | 可恢复最近一次批量重命名操作 | 高 |
| FR-08 | 扩展名过滤 | 只处理指定扩展名的文件 | 中 |

### 2.2 非功能需求

| 编号 | 需求描述 | 优先级 |
|------|----------|--------|
| NFR-01 | 代码遵循PEP8规范 | 高 |
| NFR-02 | 所有函数和类有中文注释说明 | 高 |
| NFR-03 | 单元测试覆盖率不低于80% | 高 |
| NFR-04 | 所有单元测试用例通过 | 高 |
| NFR-05 | 提供Allure测试报告 | 中 |

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        命令行界面 (CLI)                          │
│                     src/batch_rename/cli.py                      │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BatchRenamer (主控制器)                       │
│                   src/batch_rename/core.py                       │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────┐          ┌───────────────────────────┐
│   重命名策略 (Strategies)  │          │   历史记录管理器           │
│  - SequenceRename      │          │   HistoryManager          │
│  - TimestampRename     │          │  - 保存/加载/清除历史       │
│  - ReplaceRename       │          │  - JSON格式持久化存储      │
│  - PrefixRename        │          └───────────────────────────┘
│  - SuffixRename        │
│  - RegexRename         │
└───────────────────────┘
```

### 3.2 目录结构

```
BatchRename/
├── src/
│   └── batch_rename/
│       ├── __init__.py      # 包初始化文件
│       ├── __main__.py      # 模块入口
│       ├── core.py          # 核心功能模块
│       └── cli.py           # 命令行界面
├── tests/
│   ├── conftest.py          # pytest配置
│   ├── test_strategies.py   # 策略测试
│   ├── test_renamer.py      # 主类测试
│   └── test_cli.py          # CLI测试
├── docs/
│   └── system_design.md     # 系统设计文档
├── pytest.ini               # pytest配置文件
├── requirements.txt         # 依赖列表
└── README.md                # 项目说明文档
```

## 4. 详细设计

### 4.1 设计模式

本项目采用**策略模式 (Strategy Pattern)** 来实现不同的重命名算法。

#### 4.1.1 策略模式的优势
- **开闭原则**: 可以在不修改现有代码的情况下添加新的重命名策略
- **可测试性**: 每个策略可以独立进行单元测试
- **灵活性**: 可以在运行时动态切换重命名策略
- **代码复用**: 相似的算法可以共享基类的公共逻辑

### 4.2 核心类设计

#### 4.2.1 RenameStrategy (抽象基类)

**位置**: `src/batch_rename/core.py`

**职责**: 定义所有重命名策略的公共接口

**方法**:
- `generate_new_name(old_name: str, index: int) -> str`: 根据策略生成新文件名

#### 4.2.2 SequenceRenameStrategy (序列重命名策略)

**位置**: `src/batch_rename/core.py:26-52`

**职责**: 按序号批量重命名文件

**参数**:
- `name`: 基础名称
- `start`: 起始序号 (默认: 1)
- `padding`: 序号填充位数 (默认: 3)

**命名格式**: `{name}_{填充序号}.{扩展名}`

**示例**:
- `name="photo"`, `start=1`, `padding=3` → `photo_001.jpg`, `photo_002.jpg`

#### 4.2.3 TimestampRenameStrategy (时间戳重命名策略)

**位置**: `src/batch_rename/core.py:55-85`

**职责**: 按日期时间戳重命名文件

**参数**:
- `timestamp`: 指定的时间戳 (默认: 当前时间)
- `format_str`: 时间格式字符串 (默认: `%Y%m%d_%H%M%S`)

**命名格式**: `{时间戳}_{序号}.{扩展名}`

**示例**:
- `format_str="%Y%m%d"` → `20240115_1.jpg`, `20240115_2.jpg`

#### 4.2.4 ReplaceRenameStrategy (查找替换策略)

**位置**: `src/batch_rename/core.py:88-116`

**职责**: 替换文件名中的特定字符串

**参数**:
- `find`: 要查找的字符串
- `replace`: 替换的字符串

**示例**:
- `find="_backup"`, `replace=""` → `document_backup.txt` → `document.txt`

#### 4.2.5 PrefixRenameStrategy (前缀策略)

**位置**: `src/batch_rename/core.py:119-146`

**职责**: 为文件名添加前缀

**参数**:
- `prefix`: 要添加的前缀

**示例**:
- `prefix="2024_"` → `file.txt` → `2024_file.txt`

#### 4.2.6 SuffixRenameStrategy (后缀策略)

**位置**: `src/batch_rename/core.py:149-177`

**职责**: 为文件名(不含扩展名)添加后缀

**参数**:
- `suffix_str`: 要添加的后缀

**示例**:
- `suffix_str="_edited"` → `photo.jpg` → `photo_edited.jpg`

#### 4.2.7 RegexRenameStrategy (正则表达式策略)

**位置**: `src/batch_rename/core.py:180-212`

**职责**: 使用正则表达式匹配和替换文件名

**参数**:
- `pattern`: 正则表达式匹配模式
- `replace`: 替换字符串 (支持反向引用如 `\1`, `\2`)

**示例**:
- `pattern=r"IMG_(\d{4})_(\d{2})_(\d{2})"`, `replace=r"Photo_\1-\2-\3"`
  - `IMG_2024_01_15.jpg` → `Photo_2024-01-15.jpg`

#### 4.2.8 HistoryManager (历史记录管理器)

**位置**: `src/batch_rename/core.py:215-268`

**职责**: 管理重命名操作的历史记录，支持撤销功能

**属性**:
- `HISTORY_FILE`: 历史记录文件名 (`.rename_history.json`)

**方法**:
- `save_history(operations)`: 保存重命名操作历史
- `load_history()`: 加载重命名操作历史
- `clear_history()`: 清除历史记录
- `has_history()`: 检查是否有可撤销的历史

**历史记录格式 (JSON)**:
```json
[
  {
    "old_path": "/path/to/old_file.txt",
    "new_path": "/path/to/new_file.txt"
  }
]
```

#### 4.2.9 BatchRenamer (批量重命名主类)

**位置**: `src/batch_rename/core.py:271-366`

**职责**: 协调各种重命名策略，提供预览和执行功能

**参数**:
- `directory`: 文件所在目录
- `strategy`: 重命名策略实例
- `file_extensions`: 可选的文件扩展名过滤列表

**方法**:
- `get_files()`: 获取目录下的文件列表
- `preview()`: 预览重命名结果 (不执行)
- `execute(preview=False)`: 执行批量重命名
- `undo()`: 撤销上次批量重命名

### 4.3 命令行接口设计

**位置**: `src/batch_rename/cli.py`

#### 4.3.1 参数设计

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| directory | string | 是 | 文件所在目录 |
| --undo | flag | 否 | 撤销上次操作 |
| --mode | choice | 否 | 重命名模式 (sequence/timestamp/replace/prefix/suffix/regex) |
| --preview | flag | 否 | 预览模式 |
| --name | string | 序列模式 | 基础名称 |
| --start | int | 否 | 起始序号 (默认: 1) |
| --padding | int | 否 | 序号填充位数 (默认: 3) |
| --format | string | 否 | 日期格式 (默认: %Y%m%d_%H%M%S) |
| --find | string | 替换模式 | 查找的字符串 |
| --replace | string | 替换/正则模式 | 替换的字符串 |
| --prefix | string | 前缀模式 | 要添加的前缀 |
| --suffix | string | 后缀模式 | 要添加的后缀 |
| --pattern | string | 正则模式 | 正则表达式模式 |
| --ext | list | 否 | 文件扩展名过滤 |

#### 4.3.2 执行流程

```
用户输入命令
    │
    ▼
解析命令行参数
    │
    ▼
┌───────────┐      ┌──────────────┐
│  --undo?  │──────│ 撤销操作      │
│   (是)    │      │ 加载历史记录  │
└─────┬─────┘      │ 反向执行重命名 │
      │ 否         └──────────────┘
      ▼
┌───────────┐      ┌──────────────┐
│ --mode?   │──────│ 显示帮助      │
│  (未指定) │      │ 退出程序      │
└─────┬─────┘      └──────────────┘
      │ 已指定
      ▼
根据模式创建策略对象
      │
      ▼
创建BatchRenamer实例
      │
      ▼
┌───────────┐
│--preview? │──┬──是──▶ 显示预览并退出
└─────┬─────┘  │
      │ 否     │
      ▼        │
显示预览       │
      │        │
      ▼        │
用户确认? ─────┘
      │ 是
      ▼
执行重命名
      │
      ▼
保存历史记录
      │
      ▼
显示执行结果
```

## 5. 工作流程

### 5.1 正常重命名流程

```
1. 用户指定目录和重命名模式
2. 系统读取目录下的文件列表
3. 系统根据策略生成预览列表
4. 系统显示预览结果供用户确认
5. 用户确认后执行重命名
6. 系统保存重命名历史
7. 系统显示执行结果
```

### 5.2 撤销流程

```
1. 用户使用 --undo 参数
2. 系统检查是否存在历史记录
3. 如果存在，加载历史记录
4. 按相反顺序执行重命名 (new_path → old_path)
5. 清除历史记录
6. 显示撤销结果
```

## 6. 异常处理

### 6.1 异常类型

| 异常类型 | 场景 | 处理方式 |
|----------|------|----------|
| FileNotFoundError | 指定的目录不存在 | 显示错误信息并退出 |
| OSError | 文件重命名失败 (如权限问题) | 记录失败，继续处理其他文件 |
| ValueError | 无效的参数值 | 显示错误信息并退出 |
| re.error | 无效的正则表达式 | 显示错误信息并退出 |

### 6.2 异常处理策略

- **输入验证**: 在执行重命名前验证所有参数
- **操作记录**: 记录成功和失败的操作
- **原子性**: 单个文件失败不影响其他文件的处理
- **可恢复**: 所有操作都可以通过撤销功能恢复

## 7. 测试策略

### 7.1 测试框架

- **pytest**: 测试框架
- **allure-pytest**: 生成美观的测试报告
- **pytest-cov**: 代码覆盖率分析

### 7.2 测试覆盖率目标

- 总体覆盖率: ≥ 80%
- 核心模块 (core.py): ≥ 90%
- CLI模块 (cli.py): ≥ 60%

### 7.3 测试用例分类

#### 7.3.1 策略测试 (test_strategies.py)

| 测试类 | 测试方法 | 说明 |
|--------|----------|------|
| TestSequenceRenameStrategy | test_default_sequence | 测试默认参数 |
| TestSequenceRenameStrategy | test_custom_start | 测试自定义起始序号 |
| TestSequenceRenameStrategy | test_custom_padding | 测试不同填充位数 |
| TestSequenceRenameStrategy | test_different_extensions | 测试不同扩展名 |
| TestSequenceRenameStrategy | test_no_extension | 测试无扩展名文件 |
| TestTimestampRenameStrategy | test_fixed_timestamp | 测试固定时间戳 |
| TestTimestampRenameStrategy | test_custom_format | 测试自定义日期格式 |
| TestReplaceRenameStrategy | test_basic_replace | 测试基础替换 |
| TestReplaceRenameStrategy | test_replace_with_empty | 测试删除字符串 |
| TestReplaceRenameStrategy | test_no_match | 测试无匹配情况 |
| TestPrefixRenameStrategy | test_add_prefix | 测试添加前缀 |
| TestSuffixRenameStrategy | test_add_suffix | 测试添加后缀 |
| TestRegexRenameStrategy | test_simple_regex | 测试简单正则 |
| TestRegexRenameStrategy | test_backreference | 测试反向引用 |
| TestRegexRenameStrategy | test_extract_numbers | 测试提取数字 |

#### 7.3.2 主类测试 (test_renamer.py)

| 测试类 | 测试方法 | 说明 |
|--------|----------|------|
| TestHistoryManager | test_save_history | 测试保存历史 |
| TestHistoryManager | test_load_history | 测试加载历史 |
| TestHistoryManager | test_clear_history | 测试清除历史 |
| TestBatchRenamer | test_get_files | 测试获取文件列表 |
| TestBatchRenamer | test_get_files_with_extension_filter | 测试扩展名过滤 |
| TestBatchRenamer | test_preview | 测试预览功能 |
| TestBatchRenamer | test_execute | 测试执行重命名 |
| TestBatchRenamer | test_execute_preview_mode | 测试预览模式 |
| TestBatchRenamer | test_undo | 测试撤销功能 |
| TestBatchRenamer | test_nonexistent_directory | 测试目录不存在 |
| TestBatchRenamer | test_empty_directory | 测试空目录 |

#### 7.3.3 CLI测试 (test_cli.py)

| 测试类 | 测试方法 | 说明 |
|--------|----------|------|
| TestCLI | test_help | 测试帮助信息 |
| TestCLI | test_missing_mode | 测试缺少模式参数 |
| TestCLI | test_nonexistent_directory | 测试目录不存在 |
| TestCLI | test_sequence_missing_name | 测试序列模式缺少name |
| TestCLI | test_replace_missing_find | 测试替换模式缺少find |
| TestCLI | test_preview_mode | 测试预览模式 |
| TestCLI | test_extension_filter | 测试扩展名过滤 |
| TestCLI | test_undo_no_history | 测试无历史撤销 |

## 8. 安全性考虑

### 8.1 文件系统安全

- **权限检查**: 在执行重命名前检查文件权限
- **冲突检测**: 确保不会覆盖已存在的文件
- **事务性**: 虽然不是完全原子的，但提供撤销功能

### 8.2 输入验证

- **目录验证**: 检查目录是否存在且可访问
- **文件名验证**: 确保生成的文件名有效
- **正则表达式验证**: 在使用前验证正则表达式的有效性

## 9. 扩展性设计

### 9.1 添加新的重命名策略

要添加新的重命名策略，只需:

1. 继承 `RenameStrategy` 抽象基类
2. 实现 `generate_new_name` 方法
3. 在 CLI 中添加新的模式选项

### 9.2 示例: 添加一个新策略

```python
class UpperCaseRenameStrategy(RenameStrategy):
    """
    转换为大写的重命名策略
    """
    
    def generate_new_name(self, old_name: str, index: int) -> str:
        path = Path(old_name)
        return path.stem.upper() + path.suffix
```

## 10. 部署说明

### 10.1 环境要求

- Python 3.8+
- pip 或 pip3

### 10.2 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd BatchRename

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行测试
pytest

# 4. 使用工具
python -m batch_rename /path/to/files --mode sequence --name "file"
```

### 10.3 生成Allure报告

```bash
# 运行测试并生成结果
pytest

# 启动Allure服务器查看报告
allure serve allure_results
```

## 11. 使用示例

### 11.1 基本使用

```bash
# 按序号重命名
python -m batch_rename ./photos --mode sequence --name "vacation" --padding 4

# 按日期重命名
python -m batch_rename ./docs --mode timestamp --format "%Y-%m-%d"

# 查找替换
python -m batch_rename ./files --mode replace --find "_v1" --replace "_v2"

# 添加前缀
python -m batch_rename ./images --mode prefix --prefix "2024_"

# 预览模式
python -m batch_rename ./test --mode sequence --name "test" --preview

# 撤销上次操作
python -m batch_rename ./files --undo
```

### 11.2 高级使用

```bash
# 正则表达式匹配替换
python -m batch_rename ./photos \
    --mode regex \
    --pattern "IMG_(\d{4})_(\d{2})_(\d{2})" \
    --replace "Photo_\1-\2-\3"

# 只处理特定扩展名的文件
python -m batch_rename ./media --mode sequence --name "media" --ext .jpg .png .mp4
```

## 12. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.0 | 2024-01-15 | 初始版本，实现所有核心功能 |

## 13. 维护说明

### 13.1 代码规范

- 遵循 PEP 8 编码规范
- 使用类型注解
- 所有类和函数都有中文文档字符串

### 13.2 测试维护

- 添加新功能时同步添加测试
- 保持测试覆盖率 ≥ 80%
- 所有测试必须通过

## 14. 技术栈总结

| 类别 | 技术 | 版本/要求 |
|------|------|----------|
| 编程语言 | Python | 3.8+ |
| 标准库 | os, re, json, datetime, pathlib | 内置 |
| 测试框架 | pytest | ≥ 7.0.0 |
| 测试报告 | allure-pytest | ≥ 2.13.0 |
| 覆盖率 | pytest-cov | ≥ 4.0.0 |
| 代码规范 | PEP 8 | 严格遵循 |

---

**文档版本**: 1.0.0  
**最后更新**: 2024-01-15  
**作者**: BatchRename Team
