# 网站健康检测工具 - 系统设计文档

## 1. 项目概述

网站健康检测工具是一个自动化监控系统，用于定期检测多个网站的可用性、响应时间和SSL证书状态，并在异常时发送告警通知。

### 1.1 功能特性

- **HTTP/HTTPS协议检测**: 记录响应时间和状态码
- **多站点配置**: 支持配置多个检测站点，按优先级排序
- **检测频率配置**: 可设置检测间隔
- **SSL证书检测**: SSL证书有效期检测和过期提醒
- **告警通知**: 异常时支持邮件和Webhook两种告警方式
- **统计报告**: 生成网站可用性统计报告，包含响应时间趋势图

### 1.2 技术栈

- **编程语言**: Python 3
- **HTTP库**: requests
- **任务调度**: APScheduler
- **图表生成**: matplotlib
- **测试框架**: pytest + Allure
- **配置文件**: YAML

---

## 2. 系统架构

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         调度器 (Scheduler)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    任务调度 (APScheduler)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  HTTP检测器   │        │ SSL检测器     │        │  报告生成器   │
│ (HTTPChecker)│        │ (SSLChecker)  │        │  (Reporter)   │
└───────┬───────┘        └───────┬───────┘        └───────┬───────┘
        │                        │                        │
        │                        └────────────────────────┘
        │                                     │
        ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         通知管理器 (Notifier)                      │
│  ┌──────────────┐          ┌──────────────────┐                 │
│  │  邮件通知    │          │   Webhook通知     │                 │
│  │ (Email)      │          │                  │                 │
│  └──────────────┘          └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 主要职责 | 核心类 |
|------|----------|--------|
| 配置管理 | 加载和管理系统配置，设置日志系统 | Config |
| HTTP检测 | 执行HTTP/HTTPS请求，检测网站可用性 | HTTPChecker |
| SSL检测 | 检测SSL证书有效期 | SSLChecker |
| 告警通知 | 发送邮件和Webhook告警 | NotificationManager |
| 报告生成 | 生成统计报告和趋势图表 | Reporter |
| 调度器 | 定时执行检测任务 | HealthCheckScheduler |

---

## 3. 核心模块设计

### 3.1 配置管理模块 (config.py)

#### 3.1.1 类设计

```python
class Config:
    """配置管理类"""
    def __init__(self, config_path: str = "config.yaml")
    def get_sites(self) -> List[Dict[str, Any]]
    def get_notifications(self) -> Dict[str, Any]
    def get_ssl_config(self) -> Dict[str, Any]
    def get_report_config(self) -> Dict[str, Any]
    def get_logging_config(self) -> Dict[str, Any]
```

#### 3.1.2 配置文件结构

```yaml
sites:
  - name: 百度
    url: https://www.baidu.com
    priority: 1
    check_interval: 60
    timeout: 10

notifications:
  email:
    enabled: true
    smtp_server: smtp.example.com
    smtp_port: 587
    use_tls: true
    username: your_email@example.com
    password: your_password
    recipients:
      - admin@example.com
  webhook:
    enabled: true
    url: https://webhook.example.com/alert
    method: POST
    headers:
      Content-Type: application/json

ssl:
  check_enabled: true
  alert_days_before_expiry: 30

report:
  generate_interval: 86400
  output_dir: ./reports
  history_days: 7

logging:
  level: INFO
  file: ./logs/sitecheck.log
  max_size: 10485760
  backup_count: 5
```

---

### 3.2 HTTP检测模块 (http_checker.py)

#### 3.2.1 数据类

```python
@dataclass
class CheckResult:
    site_name: str          # 站点名称
    url: str                # 站点URL
    success: bool           # 是否检测成功
    status_code: Optional[int]  # HTTP状态码
    response_time: float    # 响应时间（毫秒）
    error_message: Optional[str]  # 错误信息
    timestamp: datetime     # 检测时间戳
```

#### 3.2.2 类设计

```python
class HTTPChecker:
    """HTTP检测器"""
    def __init__(self, timeout: int = 10)
    def check(self, site: Dict[str, Any]) -> CheckResult
    def close(self) -> None
    def __enter__(self)
    def __exit__(self, exc_type, exc_val, exc_tb)
```

#### 3.2.3 检测流程

1. 接收站点配置
2. 发起HTTP/HTTPS请求
3. 记录响应时间（毫秒精度）
4. 分析HTTP状态码
5. 处理异常情况（超时、连接错误等）
6. 返回检测结果

---

### 3.3 SSL证书检测模块 (ssl_checker.py)

#### 3.3.1 数据类

```python
@dataclass
class SSLCheckResult:
    site_name: str                    # 站点名称
    url: str                          # 站点URL
    success: bool                     # 是否检测成功
    valid: bool                       # 证书是否有效
    expiry_date: Optional[datetime]   # 过期时间
    days_until_expiry: Optional[int]  # 剩余天数
    issuer: Optional[str]             # 签发者
    subject: Optional[str]            # 主题
    error_message: Optional[str]      # 错误信息
    timestamp: datetime               # 检测时间戳
```

#### 3.3.2 类设计

```python
class SSLChecker:
    """SSL证书检测器"""
    def __init__(self, timeout: int = 10, alert_days: int = 30)
    def _parse_url(self, url: str) -> Tuple[str, int]
    def _get_cert(self, hostname: str, port: int) -> Dict[str, Any]
    def check(self, site: Dict[str, Any]) -> SSLCheckResult
    def needs_alert(self, result: SSLCheckResult) -> bool
```

#### 3.3.3 告警判断逻辑

- 证书已过期 → 需要告警
- 证书剩余天数 ≤ 告警阈值 → 需要告警
- 检测失败 → 需要告警

---

### 3.4 告警通知模块 (notifier.py)

#### 3.4.1 类层次结构

```
Notifier (基类)
├── EmailNotifier (邮件通知)
└── WebhookNotifier (Webhook通知)

NotificationManager (通知管理器)
```

#### 3.4.2 类设计

```python
class Notifier:
    """通知基类"""
    def send_alert(self, result: Any, alert_type: str) -> bool

class EmailNotifier(Notifier):
    """邮件通知器"""
    def __init__(self, config: Dict[str, Any])
    def send_alert(self, result: Any, alert_type: str) -> bool
    def _generate_email_content(self, result: Any, alert_type: str) -> tuple

class WebhookNotifier(Notifier):
    """Webhook通知器"""
    def __init__(self, config: Dict[str, Any])
    def send_alert(self, result: Any, alert_type: str) -> bool
    def _generate_payload(self, result: Any, alert_type: str) -> Dict[str, Any]

class NotificationManager:
    """通知管理器"""
    def __init__(self, config: Dict[str, Any])
    def _setup_notifiers(self) -> None
    def send_http_alert(self, result: CheckResult) -> None
    def send_ssl_alert(self, result: SSLCheckResult) -> None
```

---

### 3.5 报告生成模块 (reporter.py)

#### 3.5.1 类设计

```python
class Reporter:
    """报告生成器"""
    def __init__(self, output_dir: str = './reports', history_days: int = 7)
    def add_result(self, result: CheckResult) -> None
    def generate_report(self) -> str
    def _calculate_summary(self) -> Dict[str, Any]
    def _generate_response_time_chart(self, timestamp: str) -> str
    def _generate_html_content(self, summary: Dict[str, Any], chart_path: str) -> str
    def _save_raw_data(self, timestamp: str) -> None
```

#### 3.5.2 报告内容

1. **站点统计摘要**:
   - 检测次数
   - 成功次数
   - 可用性百分比
   - 平均响应时间
   - 最大/最小响应时间
   - 最新状态
   - 最后检测时间

2. **响应时间趋势图**:
   - 多站点对比折线图
   - 时间轴按检测时间排序

3. **原始数据**:
   - JSON格式保存所有检测记录
   - 便于后续分析

---

### 3.6 调度器模块 (scheduler.py)

#### 3.6.1 类设计

```python
class HealthCheckScheduler:
    """健康检测调度器"""
    def __init__(self, config: Config)
    def _check_site(self, site: Dict[str, Any]) -> None
    def _generate_report_job(self) -> None
    def start(self) -> None
    def stop(self) -> None
    def run_once(self) -> None
    def wait(self) -> None
```

#### 3.6.2 调度流程

1. 加载配置文件
2. 初始化各功能模块
3. 为每个站点创建定时检测任务
4. 创建定时报告生成任务
5. 执行一次初始检测
6. 启动调度器等待任务执行

---

## 4. 数据流程

### 4.1 检测数据流程

```
配置文件 → 调度器 → HTTPChecker → CheckResult
                                    ↓
                                  Reporter → 报告
                                    ↓
                          检测失败? → NotificationManager → 邮件/Webhook
```

### 4.2 SSL检测流程

```
HTTPS站点 → SSLChecker → SSLCheckResult → needs_alert? → NotificationManager
```

---

## 5. 关键技术点

### 5.1 响应时间测量

- 使用 `time.perf_counter()` 高精度计时器
- 记录毫秒级精度
- 包含DNS解析、TCP连接、SSL握手、服务器响应等全部时间

### 5.2 任务调度

- 使用 APScheduler 的 BackgroundScheduler
- 每个站点独立的检测间隔
- 时区设置为 Asia/Shanghai

### 5.3 日志管理

- 使用 RotatingFileHandler 进行日志轮转
- 同时输出到文件和控制台
- 支持配置日志级别

---

## 6. 测试策略

### 6.1 单元测试覆盖

| 模块 | 测试文件 | 覆盖内容 |
|------|----------|----------|
| 配置管理 | test_config.py | 配置加载、站点获取、各配置项获取 |
| HTTP检测 | test_http_checker.py | 成功/失败场景、异常处理、响应时间 |
| SSL检测 | test_ssl_checker.py | 证书解析、过期判断、告警判断 |
| 告警通知 | test_notifier.py | 邮件通知、Webhook通知、管理器 |
| 报告生成 | test_reporter.py | 数据添加、摘要计算、报告生成 |

### 6.2 测试框架

- **pytest**: 测试运行器
- **pytest-cov**: 覆盖率统计
- **Allure**: 测试报告生成
- **unittest.mock**: 模拟外部依赖

---

## 7. 部署与运行

### 7.1 环境要求

- Python 3.8+
- 网络连接（用于检测网站）
- 邮件服务器（如需邮件告警）

### 7.2 安装依赖

```bash
pip install -r requirements.txt
```

### 7.3 运行方式

#### 单次检测模式

```bash
python main.py --once
```

#### 定时调度模式

```bash
python main.py
```

#### 指定配置文件

```bash
python main.py --config /path/to/config.yaml
```

---

## 8. 目录结构

```
SiteCheck/
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置管理模块
│   ├── http_checker.py    # HTTP检测模块
│   ├── ssl_checker.py     # SSL证书检测模块
│   ├── notifier.py        # 告警通知模块
│   ├── reporter.py        # 报告生成模块
│   └── scheduler.py       # 调度器模块
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_http_checker.py
│   ├── test_ssl_checker.py
│   ├── test_notifier.py
│   └── test_reporter.py
├── reports/               # 报告输出目录
├── logs/                  # 日志目录
├── main.py                # 主入口程序
├── config.yaml            # 配置文件
├── config.yaml.example    # 配置文件示例
├── requirements.txt       # 依赖列表
├── pytest.ini             # pytest配置
├── README.md              # 项目说明
└── SYSTEM_DESIGN.md       # 系统设计文档
```

---

## 9. 扩展建议

### 9.1 功能扩展

- 支持更多告警渠道（钉钉、企业微信、Slack等）
- 添加数据库持久化存储
- 支持自定义检查项（如页面内容校验）
- 添加告警抑制和聚合机制
- 支持多环境配置

### 9.2 性能优化

- 异步并发检测
- 检测结果缓存
- 增量报告生成

### 9.3 运维优化

- Docker容器化部署
- Prometheus指标输出
- 健康检查端点
- 配置热加载
