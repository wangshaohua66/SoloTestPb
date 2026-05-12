# 自动备份同步工具 - 系统设计文档

## 1. 项目概述

### 1.1 项目背景

随着数据量的不断增长，数据安全和备份变得越来越重要。手动备份不仅费时费力，而且容易遗漏。本项目旨在开发一个自动化的备份同步工具，确保重要数据的安全。

### 1.2 项目目标

开发一个功能完善的自动备份同步工具，支持：
- 增量备份，提高效率
- 定时执行，无需人工干预
- 文件过滤，灵活配置
- 多版本管理，数据可追溯
- 详细报告，便于审计

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      命令行接口 (main.py)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  BackupSync  │ │  Scheduler   │ │   Report     │
│  核心同步模块 │ │  定时调度模块 │ │  报告生成模块 │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|------------|
| backup_sync.py | 核心备份同步逻辑，文件比对，版本管理 | `BackupSync` |
| scheduler.py | 定时任务调度 | `BackupScheduler` |
| report.py | 备份报告生成 | `BackupReport` |
| main.py | 命令行接口，参数解析 | `main()` |

## 3. 核心模块设计

### 3.1 BackupSync 类

#### 3.1.1 功能概述

`BackupSync` 是核心类，负责：
- 文件变更检测（新增、修改、删除）
- 增量同步
- 历史版本管理
- 文件过滤
- 版本压缩

#### 3.1.2 类结构

```python
class BackupSync:
    def __init__(self, source_dir, target_dir, exclude_patterns=None, 
                 exclude_extensions=None, exclude_dirs=None, version_count=5):
        """初始化备份同步器"""
    
    def _should_exclude(self, path, base_dir=None):
        """检查文件是否应该被排除"""
    
    def _get_all_files(self, base_dir):
        """获取目录下所有文件（应用过滤规则）"""
    
    def get_changed_files(self):
        """检测文件变更：新增、修改、删除"""
    
    def sync(self):
        """执行增量备份同步"""
    
    def _cleanup_old_versions(self):
        """清理过期的历史版本"""
    
    def compress_version(self, version_name=None):
        """压缩版本为ZIP文件"""
```

#### 3.1.3 增量备份算法

1. **首次备份**：
   - 复制源目录所有文件到新版本目录
   - 创建 `current` 符号链接指向新版本

2. **增量备份**：
   - 获取 `current` 指向的目录作为基准
   - 使用 `filecmp.cmp()` 比对文件（深度比对，不基于时间戳）
   - 分类为：新增、修改、删除
   - 复制 `current` 到新版本目录
   - 应用变更（复制新增/修改，删除已删除的文件）
   - 更新 `current` 符号链接
   - 清理过期版本

#### 3.1.4 文件过滤策略

支持三种过滤方式：
1. **扩展名过滤**：如 `log`, `tmp`, `bak`
2. **目录名过滤**：如 `node_modules`, `__pycache__`
3. **模式匹配**：使用 `Path.match()` 进行通配符匹配

### 3.2 BackupScheduler 类

#### 3.2.1 功能概述

基于 `schedule` 库的定时任务调度器，支持：
- 每日定时
- 每小时定时
- 每分钟间隔
- 每周定时

#### 3.2.2 类结构

```python
class BackupScheduler:
    def __init__(self, backup_func):
        """初始化调度器，传入备份函数"""
    
    def schedule_daily(self, time_str):
        """设置每日定时"""
    
    def schedule_hourly(self, minute=0):
        """设置每小时定时"""
    
    def schedule_minutely(self, interval=1):
        """设置间隔分钟"""
    
    def schedule_weekly(self, day, time_str):
        """设置每周定时"""
    
    def start(self, check_interval=1):
        """启动调度器（阻塞）"""
    
    def stop(self):
        """停止调度器"""
```

### 3.3 BackupReport 类

#### 3.3.1 功能概述

生成备份报告，支持：
- 文本格式报告
- HTML 格式报告
- 备份历史查询

#### 3.3.2 类结构

```python
class BackupReport:
    def __init__(self, target_dir):
        """初始化报告生成器"""
    
    def generate_text_report(self, stats):
        """生成文本格式报告"""
    
    def generate_html_report(self, stats):
        """生成HTML格式报告"""
    
    def save_report(self, stats, report_type='text', filename=None):
        """保存报告到文件"""
    
    def get_backup_history(self):
        """获取备份历史记录"""
```

## 4. 数据结构设计

### 4.1 同步统计信息 (stats)

```python
{
    "timestamp": "20240101_020000",
    "version_dir": "/backup/v_20240101_020000",
    "added_count": 5,
    "modified_count": 3,
    "deleted_count": 1,
    "total_copied": 8,
    "total_size_bytes": 102400,
    "added_files": ["/source/file1.txt", ...],
    "modified_files": ["/source/file2.txt", ...],
    "deleted_files": ["/backup/current/old.txt", ...]
}
```

### 4.2 备份历史记录

```python
[
    {
        "version": "v_20240102_020000",
        "timestamp": "20240102_020000",
        "file_count": 150,
        "total_size": 10485760,
        "total_size_formatted": "10.00 MB"
    },
    ...
]
```

## 5. 目录结构设计

### 5.1 备份目标目录结构

```
backup_root/
├── v_20240101_020000/          # 历史版本目录
│   ├── file1.txt
│   └── subdir/
│       └── file2.txt
├── v_20240102_020000/          # 最新版本目录
├── current/                    # 指向最新版本的符号链接（或副本）
├── v_20240102_020000.zip       # 可选：压缩版本
└── reports/                    # 报告目录
    ├── backup_report_20240101_020000.txt
    └── backup_report_20240102_020000.html
```

## 6. 关键算法设计

### 6.1 文件比对算法

使用 Python 标准库 `filecmp.cmp()`：

```python
def _files_are_different(self, file1, file2):
    try:
        # shallow=False：深度比对文件内容
        return not filecmp.cmp(str(file1), str(file2), shallow=False)
    except (OSError, IOError):
        return True
```

**优点**：
- 准确：基于文件内容比对，不依赖时间戳
- 高效：先比较文件大小，再比较内容

### 6.2 版本清理算法

```python
def _cleanup_old_versions(self):
    version_dirs = sorted(
        [d for d in target_dir.iterdir() if d.name.startswith('v_')],
        key=lambda d: d.name,  # 按时间戳排序
        reverse=True            # 最新的在前
    )
    
    # 只保留最近的 N 个版本
    for old_dir in version_dirs[self.version_count:]:
        shutil.rmtree(old_dir)
```

## 7. 测试策略

### 7.1 测试覆盖范围

| 模块 | 测试用例数 | 覆盖率 |
|------|-----------|--------|
| backup_sync.py | 12 | 84% |
| scheduler.py | 10 | 80% |
| report.py | 8 | 91% |
| **总计** | **30** | **86%** |

### 7.2 核心测试场景

1. **初始化测试**：验证参数正确设置
2. **首次备份测试**：验证所有文件被复制
3. **增量备份测试**：
   - 新增文件检测
   - 修改文件检测
   - 删除文件检测
4. **文件过滤测试**：
   - 扩展名过滤
   - 目录名过滤
5. **版本清理测试**：验证只保留指定数量的版本
6. **压缩测试**：验证 ZIP 文件正确生成
7. **定时任务测试**：验证各种调度方式
8. **报告生成测试**：验证文本和 HTML 报告

### 7.3 增量备份准确率测试

专门的测试用例 `test_incremental_accuracy` 验证：
- 4 个初始文件 → 全部备份
- 新增 1 个 → 检测为新增
- 修改 1 个 → 检测为修改
- 删除 1 个 → 检测为删除
- 验证 `current` 目录正确反映所有变更

**目标**：100% 准确率，不遗漏任何变更

## 8. 错误处理

### 8.1 异常处理策略

| 场景 | 处理方式 |
|------|---------|
| 源目录不存在 | 抛出 `ValueError` |
| 文件比对失败 | 视为不同文件（安全策略） |
| 符号链接创建失败 | 降级为目录副本（macOS 兼容） |
| 备份函数异常 | 捕获并记录，调度器继续运行 |

### 8.2 边界情况

- 空源目录
- 空目标目录
- 同名文件快速连续修改
- 磁盘空间不足（依赖系统级错误）

## 9. 性能考虑

### 9.1 时间复杂度

| 操作 | 时间复杂度 |
|------|-----------|
| 文件扫描 | O(n)，n 为文件数 |
| 文件比对 | O(k)，k 为变更文件数 |
| 版本清理 | O(m)，m 为版本数 |

### 9.2 优化策略

1. **增量备份**：只复制变更文件
2. **深度比对**：`filecmp.cmp()` 先比较大小再比较内容
3. **符号链接**：`current` 使用符号链接避免重复复制

## 10. 安全考虑

1. **路径规范化**：使用 `Path.resolve()` 处理路径
2. **异常捕获**：防止单个文件错误导致整体失败
3. **无日志敏感信息**：不在日志中输出文件内容

## 11. 依赖说明

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.12+ | 运行时 |
| schedule | >=1.2.0 | 定时任务 |
| pytest | >=8.0.0 | 测试框架 |
| pytest-cov | >=5.0.0 | 覆盖率报告 |
| allure-pytest | >=2.13.0 | Allure 报告 |

## 12. 未来扩展

1. **远程备份**：支持 FTP/SFTP/S3 等远程存储
2. **加密备份**：支持加密压缩
3. **增量压缩**：只存储文件差异（类似 Git）
4. **Web 界面**：提供可视化管理界面
5. **通知系统**：备份完成邮件/微信通知

## 13. 总结

本系统设计遵循了以下原则：
- **模块化**：各模块职责清晰，易于维护
- **可测试**：高覆盖率确保质量
- **用户友好**：提供命令行和编程两种接口
- **健壮性**：完善的错误处理和边界情况考虑
- **效率**：增量备份和深度比对平衡了效率和准确性
