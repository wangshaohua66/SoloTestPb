# 自动备份同步工具

一个基于 Python 的自动备份和同步文件工具，支持增量备份、定时任务、文件过滤和多版本管理。

## 功能特性

1. **文件同步**：支持指定源目录和目标目录进行同步
2. **增量备份**：仅复制新增或修改的文件，提高备份效率
3. **定时任务**：支持每日、每小时、每分钟、每周等多种定时方式
4. **文件过滤**：排除特定类型、目录或符合模式的文件
5. **备份报告**：生成文本或 HTML 格式的备份报告，包含文件数量和大小统计
6. **多版本备份**：保留历史版本，可配置保留数量
7. **版本压缩**：支持将备份版本压缩为 ZIP 文件

## 技术栈

- **编程语言**：Python 3.12+
- **文件比对**：filecmp（标准库）
- **定时任务**：schedule
- **压缩存储**：zipfile（标准库）
- **测试框架**：pytest + Allure
- **代码规范**：PEP8

## 安装

1. 克隆项目：
```bash
git clone <repository_url>
cd BackupSync
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行接口

#### 1. 执行单次备份

```bash
python main.py backup --source /path/to/source --target /path/to/backup
```

可选参数：
- `--exclude-patterns`：要排除的文件/目录模式（如 `*.tmp`）
- `--exclude-extensions`：要排除的文件扩展名（如 `log bak`）
- `--exclude-dirs`：要排除的目录名（如 `node_modules __pycache__`）
- `--version-count`：保留的历史版本数（默认：5）
- `--report`：生成备份报告
- `--report-type`：报告类型，可选 `text` 或 `html`（默认：text）
- `--compress`：压缩备份版本为 ZIP 文件

示例：
```bash
# 备份并生成 HTML 报告
python main.py backup --source /data --target /backup --report --report-type html

# 排除临时文件和日志
python main.py backup --source /data --target /backup \
    --exclude-extensions log tmp \
    --exclude-dirs node_modules __pycache__
```

#### 2. 启动定时备份

```bash
# 每日凌晨 2:00 备份
python main.py schedule --source /data --target /backup --daily 02:00

# 每小时第 30 分钟备份
python main.py schedule --source /data --target /backup --hourly 30

# 每 30 分钟备份一次
python main.py schedule --source /data --target /backup --minutely 30

# 每周一凌晨 2:00 备份
python main.py schedule --source /data --target /backup --weekly "monday 02:00"
```

按 `Ctrl+C` 停止定时备份。

#### 3. 查看备份历史

```bash
python main.py history --target /path/to/backup
```

### 编程接口

```python
from backupsync import BackupSync, BackupScheduler, BackupReport

# 创建备份同步器
backup = BackupSync(
    source_dir='/path/to/source',
    target_dir='/path/to/backup',
    exclude_extensions=['log', 'tmp'],
    exclude_dirs=['node_modules', '__pycache__'],
    version_count=5
)

# 执行同步
stats = backup.sync()
print(f"新增: {stats['added_count']}, 修改: {stats['modified_count']}")

# 生成报告
report = BackupReport('/path/to/backup')
report.save_report(stats, report_type='html')

# 设置定时任务
def backup_task():
    return backup.sync()

scheduler = BackupScheduler(backup_func=backup_task)
scheduler.schedule_daily('02:00')
scheduler.start()
```

## 项目结构

```
BackupSync/
├── backupsync/
│   ├── __init__.py          # 包初始化
│   ├── backup_sync.py       # 核心备份同步模块
│   ├── scheduler.py         # 定时任务调度模块
│   └── report.py            # 备份报告模块
├── tests/
│   ├── __init__.py
│   ├── test_backup_sync.py  # 核心功能测试
│   ├── test_scheduler.py    # 定时任务测试
│   └── test_report.py       # 报告生成测试
├── main.py                  # 命令行入口
├── pytest.ini               # pytest 配置
├── requirements.txt         # 依赖列表
└── README.md                # 本文件
```

## 运行测试

### 运行所有测试并查看覆盖率

```bash
pytest tests/ -v --cov=backupsync --cov-report=term-missing
```

### 生成 Allure 测试报告

```bash
# 生成 Allure 结果
pytest tests/ --alluredir=allure-results

# 查看报告（需要安装 allure 命令行工具）
allure serve allure-results
```

## 测试结果

- **测试用例数**：30 个
- **通过率**：100%
- **代码覆盖率**：86%（目标：≥80%）

## 备份版本管理

备份目录结构：
```
/path/to/backup/
├── v_20240101_020000/    # 历史版本
├── v_20240102_020000/    # 历史版本
├── current/              # 指向最新版本的符号链接（或副本）
├── v_20240102_020000.zip # 可选的压缩版本
└── reports/              # 备份报告目录
    └── backup_report_20240102_020000.html
```

## 注意事项

1. 在 macOS 上，由于权限限制，符号链接可能会降级为目录副本
2. 确保源目录和目标目录有足够的磁盘空间
3. 定时任务以单线程方式运行，不会并发执行

## 许可证

MIT License
