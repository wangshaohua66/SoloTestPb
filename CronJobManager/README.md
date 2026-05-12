# 定时任务调度器 (CronJobManager)

一个功能完善的Python定时任务调度器，支持多种调度策略，帮助用户自动化日常任务。

## 功能特性

### 1. 多种调度策略

- **Cron表达式调度：支持标准Cron表达式定义任务执行时间
- **周期性任务**：支持按固定时间间隔周期性执行任务
- **一次性任务**：支持指定时间点执行一次性任务

### 2. 任务依赖管理

- 支持配置任务之间的依赖关系
- 任务B在任务A完成后自动触发执行
- 支持多种依赖条件（成功后触发、完成后触发、总是触发）

### 3. 任务执行日志

- 完整记录任务执行历史
- 支持按任务、时间、状态查询执行日志
- 提供任务执行统计信息

### 4. 失败重试机制

- 可配置重试次数
- 可配置重试间隔
- 支持指数退避策略

### 5. 状态监控与告警

- 实时任务状态监控
- 支持邮件告警通知
- 支持Webhook告警通知

## 技术栈

- **编程语言**：Python 3.12
- **调度框架**：APScheduler 3.10.4
- **持久化**：SQLite + SQLAlchemy 2.0.25
- **日志**：logging
- **测试框架**：pytest + pytest-cov + allure-pytest
- **代码规范**：PEP8

## 项目结构

```
CronJobManager/
├── cronjobmanager/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # 配置管理
│   │   ├── database.py      # 数据库管理
│   │   ├── scheduler.py     # 任务调度器
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py              # 任务模型
│   │   │   ├── execution_log.py       # 执行日志模型
│   │   │   └── task_dependency.py  # 任务依赖模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py       # 任务服务
│   │   │   ├── dependency_service.py   # 依赖服务
│   │   │   ├── log_service.py      # 日志服务
│   │   │   └── alert_service.py    # 告警服务
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py           # 日志工具
│   │       └── function_loader.py  # 函数加载工具
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py       # pytest配置
│   │   ├── test_helpers.py   # 测试辅助函数
│   │   ├── test_config.py
│   │   ├── test_task_service.py
│   │   ├── test_dependency_service.py
│   │   ├── test_log_service.py
│   │   ├── test_function_loader.py
│   │   └── test_scheduler.py
│   └── docs/
│       └── system_design.md      # 系统设计文档
├── requirements.txt
└── README.md
```

## 安装与使用

### 环境要求

- Python 3.12 或更高版本
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 快速开始

```python
from datetime import datetime, timedelta
from cronjobmanager import TaskScheduler, TaskType


def my_task_function():
    print("任务执行成功！")


if __name__ == "__main__":
    scheduler = TaskScheduler()
    
    try:
        scheduler.start()
        
        scheduler.add_task(
            name="示例Cron任务",
            func_path="__main__.my_task_function",
            task_type=TaskType.CRON,
            cron_expression="* * * * *",  # 每分钟执行
        )
        
        scheduler.add_task(
            name="示例间隔任务",
            func_path="__main__.my_task_function",
            task_type=TaskType.INTERVAL,
            interval_seconds=30,  # 每30秒执行
        )
        
        future_time = datetime.utcnow() + timedelta(minutes=5)
        scheduler.add_task(
            name="示例一次性任务",
            func_path="__main__.my_task_function",
            task_type=TaskType.DATE,
            run_date=future_time,
        )
        
        print("调度器已启动，按 Ctrl+C 退出...")
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        scheduler.stop()
        print("调度器已停止")
```

### 任务依赖配置

```python
from cronjobmanager import TaskScheduler, TaskType


def task_a():
    print("任务A执行")


def task_b():
    print("任务B执行，在任务A完成后执行")


scheduler = TaskScheduler()
scheduler.start()

task_a = scheduler.add_task(
    name="任务A",
    func_path="__main__.task_a",
    task_type=TaskType.CRON,
    cron_expression="0 * * * *",  # 每小时执行
)

scheduler.add_task(
    name="任务B",
    func_path="__main__.task_b",
    task_type=TaskType.CRON,
    cron_expression="0 * * * *",
    dependencies=[
        {
            "dependency_task_id": task_a["id"],
            "condition": "success",  # 任务A成功后执行任务B
        }
    ],
)
```

### 任务失败重试

```python
scheduler.add_task(
    name="带重试的任务",
    func_path="my_module.my_function",
    task_type=TaskType.CRON,
    cron_expression="0 * * * *",
    max_retries=3,      # 最大重试3次
    retry_interval=5,     # 重试间隔5秒
    backoff_factor=2,       # 指数退避因子
)
```

### 配置告警通知

```python
from cronjobmanager import Config, TaskScheduler

config = Config({
    "alert": {
        "enabled": True,
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "sender": "alert@example.com",
            "recipients": ["admin@example.com"],
            "username": "alert@example.com",
            "password": "password",
        },
        "webhook": {
            "url": "https://your-webhook-url.com/alert",
            "headers": {"Content-Type": "application/json"},
        },
    },
})

scheduler = TaskScheduler(config)
```

## 运行测试

### 运行所有测试

```bash
cd cronjobmanager
pytest
```

### 运行测试并生成覆盖率报告

```bash
cd cronjobmanager
pytest --cov=. --cov-report=term-missing
```

### 生成Allure测试报告

```bash
cd cronjobmanager
pytest --alluredir=./allure-results
allure serve ./allure-results
```

## API 参考

### TaskScheduler 类

#### 方法：

- `start()` - 启动调度器
- `stop(wait=True)` - 停止调度器
- `add_task(...)` - 添加新任务
- `remove_task(task_id)` - 移除任务
- `pause_task(task_id)` - 暂停任务
- `resume_task(task_id)` - 恢复任务
- `run_task_now(task_id)` - 立即执行任务
- `get_task_status(task_id)` - 获取任务状态
- `list_tasks(**kwargs)` - 列出任务

### TaskType 枚举

- `CRON` - Cron表达式任务
- `INTERVAL` - 周期性任务
- `DATE` - 一次性任务

### TaskStatus 枚举

- `PENDING` - 待执行
- `RUNNING` - 运行中
- `SUCCESS` - 执行成功
- `FAILED` - 执行失败
- `PAUSED` - 已暂停
- `COMPLETED` - 已完成

## 许可证

MIT License

## 性能特性

- 支持同时运行至少50个定时任务
- 使用线程池执行器，支持高并发任务执行
- 任务持久化到SQLite数据库，支持重启恢复
- 完善的错误处理和重试机制
- 完整的日志记录和状态监控
