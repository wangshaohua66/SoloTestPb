# 自动化报表生成工具 - 系统设计文档

## 1. 项目概述

### 1.1 项目背景

自动化报表生成工具是一个用于提高报表制作效率的Python脚本工具。它支持从多种数据源读取数据，进行灵活的数据处理，并生成多种格式的报表。

### 1.2 项目目标

- 支持从CSV、Excel、JSON文件读取数据
- 支持从MySQL、SQLite数据库读取数据
- 支持使用Jinja2模板自定义报表格式
- 支持生成Excel、HTML、PDF格式报表
- 支持数据聚合、排序、筛选处理
- 支持定时自动生成并发送报表
- 处理10万行数据生成报表耗时不超过30秒

### 1.3 技术选型

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | Python 3.12 | 最新稳定版Python |
| 数据处理 | pandas | 强大的数据处理库 |
| Excel处理 | openpyxl | Excel读写支持 |
| 模板引擎 | Jinja2 | 灵活的模板系统 |
| PDF生成 | WeasyPrint | HTML转PDF支持 |
| 数据库 | SQLAlchemy + pymysql | ORM框架和MySQL驱动 |
| 定时任务 | schedule | 轻量级定时任务库 |
| 测试框架 | pytest + Allure | 测试和报告生成 |

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │
│  │  Python API │  │  CLI 工具   │  │   定时任务调度器   │  │
│  └─────────────┘  └─────────────┘  └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     核心层 (ReportGenerator)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              报表生成协调器                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│   数据层       │   │   处理层       │   │   输出层       │
│                │   │                │   │                │
│ - DataReader   │   │ - DataProcessor│   │ - ExcelOutput │
│ - 数据源读取   │   │ - 数据处理     │   │ - HtmlOutput  │
│ - CSV/Excel/  │   │ - 筛选/排序/   │   │ - PdfOutput   │
│   JSON/MySQL/ │   │   聚合等       │   │                │
│   SQLite      │   │                │   │                │
└────────────────┘   └────────────────┘   └────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         ▼                                         ▼
┌────────────────┐                      ┌────────────────┐
│  模板引擎层    │                      │  外部服务      │
│                │                      │                │
│ - TemplateEngine│                     │ - 邮件服务     │
│ - Jinja2模板   │                      │ - SMTP        │
│ - 自定义过滤器 │                      │                │
└────────────────┘                      └────────────────┘
```

### 2.2 模块职责

#### 2.2.1 数据层 (Data Layer)

**DataReader** - 数据读取器
- 职责：从多种数据源读取数据并返回DataFrame
- 支持的数据源：
  - CSV文件
  - Excel文件
  - JSON文件
  - MySQL数据库
  - SQLite数据库

**DataProcessor** - 数据处理器
- 职责：对DataFrame进行各种数据处理操作
- 支持的操作：
  - 数据筛选（精确匹配、范围、包含、列表等）
  - 数据排序（升序、降序、多列排序）
  - 数据聚合（分组、聚合函数）
  - 列选择和重命名
  - 去重
  - 缺失值处理

#### 2.2.2 模板引擎层 (Template Layer)

**TemplateEngine** - 模板引擎
- 职责：提供Jinja2模板渲染功能
- 功能：
  - 加载和渲染模板文件
  - 渲染模板字符串
  - 内置常用过滤器（数字、货币、日期、百分比格式化）
  - 支持自定义过滤器和全局变量
  - 提供默认报表模板

#### 2.2.3 输出层 (Output Layer)

**ExcelOutput** - Excel输出
- 职责：将DataFrame导出为Excel文件
- 功能：
  - 基本导出
  - 多工作表导出
  - 带格式导出（表头样式、冻结窗格、列宽）

**HtmlOutput** - HTML输出
- 职责：将DataFrame导出为HTML文件
- 功能：
  - 基本HTML导出
  - 使用Jinja2模板导出
  - 使用模板字符串导出

**PdfOutput** - PDF输出
- 职责：将数据转换为PDF文件
- 功能：
  - 从HTML文件转换
  - 从HTML字符串转换
  - 从DataFrame直接转换

#### 2.2.4 调度器层 (Scheduler Layer)

**ReportScheduler** - 报表调度器
- 职责：管理定时任务和邮件发送
- 功能：
  - 每日定时任务
  - 每小时定时任务
  - 每周定时任务
  - 间隔分钟任务
  - 邮件发送（支持附件）
  - 报表邮件发送

#### 2.2.5 核心层 (Core Layer)

**ReportGenerator** - 报表生成器
- 职责：协调整个报表生成流程
- 功能：
  - 根据配置自动生成报表
  - 从DataFrame直接生成报表
  - 批量生成多个报表
  - 性能计时和统计

## 3. 数据流程设计

### 3.1 完整的报表生成流程

```
用户配置
    │
    ▼
┌─────────────┐
│ 读取数据源   │ ──→ DataReader
│ (CSV/Excel/ │
│  JSON/DB)   │
└─────────────┘
    │
    ▼
┌─────────────┐
│ 数据处理     │ ──→ DataProcessor
│ (筛选/排序/ │
│  聚合等)    │
└─────────────┘
    │
    ▼
┌─────────────┐
│ 模板渲染     │ ──→ TemplateEngine
│ (可选)      │
└─────────────┘
    │
    ▼
┌─────────────┐
│ 报表输出     │ ──→ ExcelOutput/HtmlOutput/PdfOutput
│ (Excel/     │
│  HTML/PDF)  │
└─────────────┘
    │
    ▼
输出文件
```

### 3.2 配置格式说明

报表生成配置采用JSON格式，包含以下主要部分：

```json
{
    "source": {
        "type": "csv",
        "params": {
            "file_path": "data/input.csv"
        }
    },
    "processing": {
        "operations": [
            {
                "type": "filter",
                "params": {
                    "conditions": {
                        "salary": {"min": 5000}
                    }
                }
            },
            {
                "type": "sort",
                "params": {
                    "sort_by": "salary",
                    "ascending": false
                }
            }
        ]
    },
    "output": {
        "format": "excel",
        "path": "output/report.xlsx",
        "title": "报表标题"
    },
    "template": {
        "use_template": true,
        "template_path": "templates/report.html",
        "context": {
            "report_title": "自定义标题"
        }
    }
}
```

## 4. 关键设计决策

### 4.1 数据处理管道模式

采用管道模式处理数据，每个处理步骤独立且可配置：

```python
operations = [
    {"type": "filter", "params": {...}},
    {"type": "sort", "params": {...}},
    {"type": "aggregate", "params": {...}},
]

result = processor.process_data(df, operations)
```

优点：
- 灵活性高：可以任意组合处理步骤
- 可扩展性：容易添加新的处理操作
- 可读性：处理流程清晰可见

### 4.2 统一数据源接口

所有数据源通过统一接口读取：

```python
df = reader.read_from_source(source_type, source_params)
```

支持的source_type：
- `csv`
- `excel`
- `json`
- `mysql`
- `sqlite`

优点：
- 上层代码无需关心具体数据源类型
- 容易添加新的数据源支持

### 4.3 模板引擎设计

模板引擎基于Jinja2，提供：
- 默认过滤器（数字、货币、日期、百分比）
- 默认模板（完整报表模板、简单模板）
- 支持自定义过滤器和全局变量

### 4.4 性能优化策略

为满足10万行数据30秒内完成的要求：

1. **使用pandas原生操作**：所有数据处理使用pandas内置函数
2. **避免不必要的数据复制**：在关键路径上使用in-place操作
3. **分块处理大文件**：对于超大文件可以考虑分块读取
4. **使用高效的Excel写入**：使用openpyxl引擎

## 5. 错误处理设计

### 5.1 异常层次

```
ValueError
├── 数据源读取错误
│   ├── 文件不存在
│   ├── 文件格式错误
│   └── 数据库连接错误
├── 数据处理错误
│   ├── 列不存在
│   ├── 无效的处理参数
│   └── 聚合错误
├── 模板渲染错误
│   ├── 模板文件不存在
│   └── 模板语法错误
└── 输出错误
    ├── 写入权限错误
    └── 格式不支持
```

### 5.2 错误处理原则

- 所有对外接口都有明确的异常类型
- 错误信息包含足够的上下文
- 批量操作时记录错误但继续处理其他任务

## 6. 测试策略

### 6.1 单元测试覆盖

| 模块 | 测试重点 |
|------|---------|
| DataReader | 各数据源读取、异常处理 |
| DataProcessor | 各处理操作、边界条件 |
| TemplateEngine | 模板渲染、过滤器、异常处理 |
| ExcelOutput | 导出功能、格式设置 |
| HtmlOutput | HTML导出、模板集成 |
| ReportGenerator | 完整流程、配置解析、性能 |

### 6.2 性能测试

- 测试10万行数据的处理和导出
- 确保总耗时不超过30秒
- 包含在单元测试中自动执行

## 7. 扩展点设计

### 7.1 添加新的数据源

1. 在`DataReader`类中添加新的读取方法
2. 在`read_from_source`方法中添加对应的case

### 7.2 添加新的处理操作

1. 在`DataProcessor`类中添加处理方法
2. 在`process_data`方法中添加对应的case

### 7.3 添加新的输出格式

1. 创建新的输出类（如`XmlOutput`）
2. 在`ReportGenerator`中添加对新格式的支持

## 8. 部署建议

### 8.1 依赖安装

```bash
pip install -r requirements.txt
```

### 8.2 PDF生成注意事项

WeasyPrint需要系统级依赖：
- Linux: `apt-get install libpango1.0-0 libcairo2 libpangocairo-1.0-0`
- macOS: `brew install pango cairo`
- Windows: 需要安装GTK+运行时

### 8.3 生产环境配置

1. 使用配置文件管理数据库连接信息
2. 敏感信息（密码）使用环境变量
3. 日志记录到文件
4. 监控定时任务执行情况

## 9. 维护指南

### 9.1 代码结构

```
reportgen/
├── __init__.py          # 包导出
├── main.py              # CLI入口
├── core/
│   └── generator.py     # 核心报表生成器
├── data/
│   ├── reader.py        # 数据读取
│   └── processor.py     # 数据处理
├── output/
│   ├── excel_output.py  # Excel输出
│   ├── html_output.py   # HTML输出
│   └── pdf_output.py    # PDF输出
├── templates/
│   └── engine.py        # 模板引擎
└── scheduler/
    └── scheduler.py     # 定时任务和邮件
```

### 9.2 版本管理

- 遵循语义化版本控制（SemVer）
- 主要版本：破坏性变更
- 次要版本：新增功能
- 补丁版本：Bug修复

## 10. 附录

### 10.1 数据处理操作参考

| 操作类型 | 说明 | 参数 |
|---------|------|------|
| filter | 筛选数据 | conditions |
| sort | 排序数据 | sort_by, ascending |
| aggregate | 聚合数据 | group_by, aggregations |
| select_columns | 选择列 | columns |
| rename_columns | 重命名列 | column_mapping |
| drop_duplicates | 去重 | subset, keep |
| handle_missing | 处理缺失值 | strategy, fill_value |

### 10.2 筛选条件参考

| 条件类型 | 说明 | 示例 |
|---------|------|------|
| 精确匹配 | 等于指定值 | {"col": "value"} |
| min | 大于等于 | {"col": {"min": 100}} |
| max | 小于等于 | {"col": {"max": 100}} |
| in | 在列表中 | {"col": {"in": ["a", "b"]}} |
| notin | 不在列表中 | {"col": {"notin": ["a", "b"]}} |
| contains | 包含字符串 | {"col": {"contains": "abc"}} |
| startswith | 以...开头 | {"col": {"startswith": "abc"}} |
| endswith | 以...结尾 | {"col": {"endswith": "xyz"}} |
