# 服务器资源监控工具

一个用于实时监控服务器资源使用情况的自动化工具，支持CPU、内存、磁盘、网络监控，并提供告警和报告功能。

## 功能特性

### 1. CPU监控
- 实时监控CPU使用率
- 支持多核显示
- 提供历史数据记录

### 2. 内存监控
- 实时监控物理内存使用情况
- 监控虚拟内存（交换空间）使用情况

### 3. 磁盘监控
- 监控各分区磁盘使用率
- 监控磁盘IO速度（读写）

### 4. 网络监控
- 监控网络流量（上传/下载）
- 按网卡统计

### 5. 告警功能
- 支持设置各项阈值
- 超过阈值发送邮件通知
- 告警冷却机制避免重复通知

### 6. 报告功能
- 生成资源使用报告
- 包含历史趋势图表
- 支持定时自动生成报告
- HTML格式报告

## 技术栈

- **编程语言**: Python 3
- **系统监控**: psutil
- **图表生成**: matplotlib
- **邮件通知**: smtplib
- **测试框架**: pytest + Allure
- **代码规范**: PEP8

## 安装说明

### 环境要求
- Python 3.7+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用说明

### 快速开始

```bash
python main.py
```

### 命令行参数

```bash
python main.py --config your_config.json  # 使用自定义配置文件
python main.py --version                  # 查看版本信息
python main.py --help                     # 查看帮助信息
```

### 配置说明

首次运行时会自动生成`config.json`配置文件，可根据需要修改：

```json
{
    "interval": 1,                    // 监控间隔（秒），最小支持1秒
    "cpu_threshold": 80.0,           // CPU告警阈值（%）
    "memory_threshold": 80.0,        // 内存告警阈值（%）
    "disk_threshold": 85.0,          // 磁盘告警阈值（%）
    "network_threshold": 100.0,      // 网络告警阈值（MB/s）
    "smtp": {
        "enabled": false,             // 是否启用邮件通知
        "server": "smtp.example.com", // SMTP服务器地址
        "port": 587,                  // SMTP端口
        "username": "user@example.com", // SMTP用户名
        "password": "password",        // SMTP密码
        "from_email": "monitor@example.com", // 发件人邮箱
        "to_emails": ["admin@example.com"], // 收件人邮箱列表
        "use_tls": true               // 是否使用TLS加密
    },
    "report": {
        "enabled": true,              // 是否启用报告功能
        "interval": 3600,             // 报告生成间隔（秒）
        "path": "./reports",          // 报告保存路径
        "format": "html"              // 报告格式
    },
    "data_retention": 86400          // 数据保留时间（秒），默认24小时
}
```

### 输出示例

```
============================================================
服务器资源监控工具
============================================================
监控间隔: 1 秒
报告间隔: 3600 秒
邮件通知: 未启用
============================================================
按 Ctrl+C 停止监控

[2024-01-01 12:00:00] [✓ OK] CPU:  25.3% | 内存:  45.2% | 磁盘:  65.8% | 网络: ↑0.05 ↓0.12 MB/s
[2024-01-01 12:00:01] [✓ OK] CPU:  23.1% | 内存:  45.1% | 磁盘:  65.8% | 网络: ↑0.03 ↓0.08 MB/s
```

## 测试说明

### 运行单元测试

```bash
pytest
```

### 运行测试并生成覆盖率报告

```bash
pytest --cov=monitor --cov-report=html
```

### 生成Allure测试报告

```bash
pytest --alluredir=./allure-results
allure serve ./allure-results
```

## 项目结构

```
ServerMonitor/
├── monitor/                  # 主模块目录
│   ├── __init__.py
│   ├── config.py            # 配置管理模块
│   ├── monitor.py           # 主监控程序
│   ├── core/                # 核心监控模块
│   │   ├── __init__.py
│   │   ├── cpu_monitor.py   # CPU监控
│   │   ├── memory_monitor.py # 内存监控
│   │   ├── disk_monitor.py  # 磁盘监控
│   │   ├── network_monitor.py # 网络监控
│   │   └── data_store.py    # 数据存储
│   ├── notifier/            # 告警通知模块
│   │   ├── __init__.py
│   │   ├── alert_manager.py # 告警管理
│   │   └── email_notifier.py # 邮件通知
│   └── reporter/            # 报告生成模块
│       ├── __init__.py
│       └── report_generator.py # 报告生成
├── tests/                   # 测试目录
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_data_store.py
│   └── test_alert_manager.py
├── reports/                 # 报告输出目录（自动生成）
├── main.py                  # 命令行入口
├── config.json              # 配置文件（自动生成）
├── requirements.txt         # 依赖列表
├── pytest.ini              # pytest配置
└── README.md               # 项目说明
```

## 代码规范

项目严格遵循PEP8代码规范，所有函数和类都有中文注释说明。

## 常见问题

### 1. 如何修改监控间隔？
编辑`config.json`文件，修改`interval`字段，单位为秒。

### 2. 如何启用邮件通知？
编辑`config.json`文件，在`smtp`部分配置正确的SMTP服务器信息，并将`enabled`设为`true`。

### 3. 报告保存在哪里？
默认保存在`./reports`目录下，每个报告是一个独立的子目录，包含HTML报告和图表图片。

### 4. 支持哪些操作系统？
支持Windows、Linux、macOS等主流操作系统。

## 许可证

本项目仅供学习和内部使用。

## 版本历史

### v1.0.0
- 初始版本发布
- 实现CPU、内存、磁盘、网络监控功能
- 实现告警和邮件通知功能
- 实现报告生成功能
- 完成单元测试
