# 批量邮件发送工具 - 系统设计文档

## 1. 概述

### 1.1 项目背景

批量邮件发送工具是一个面向企业和个人的自动化邮件发送解决方案，适用于通知、营销、活动邀请等场景。系统支持从CSV/Excel读取收件人数据，使用Jinja2模板引擎渲染个性化邮件内容，并提供完整的发送日志和统计。

### 1.2 设计目标

- **高可扩展性**: 模块化设计，便于后续功能扩展
- **高可靠性**: 自动重试机制，确保发送成功率
- **易用性**: 提供命令行和Python API两种使用方式
- **可维护性**: 清晰的代码结构，完整的中文注释
- **可测试性**: 高测试覆盖率，确保代码质量

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层                                      │
│  ┌──────────────────┐  ┌────────────────────────────────────────┐  │
│  │   命令行CLI      │  │           Python API                   │  │
│  │  (batch_mail.cli)│  │  (BatchMailer, EmailSender, etc.)    │  │
│  └──────────────────┘  └────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        业务逻辑层                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    BatchMailer (批量管理器)                   │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐              │   │
│  │  │ 数据读取   │ │ 模板渲染   │ │ 邮件发送   │              │   │
│  │  └────────────┘ └────────────┘ └────────────┘              │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   基础设施层    │  │   基础设施层    │  │   基础设施层    │
│ DataReader     │  │TemplateRenderer│  │ EmailSender    │
│ (CSV/Excel)    │  │  (Jinja2)      │  │  (smtplib)     │
└────────────────┘  └────────────────┘  └────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│    外部依赖     │  │    外部依赖     │  │    外部依赖     │
│  pandas        │  │  Jinja2        │  │  smtplib       │
│  openpyxl      │  │                │  │  email         │
└────────────────┘  └────────────────┘  └────────────────┘
```

### 2.2 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| 配置管理 | `config/settings.py` | 管理SMTP和重试配置 |
| 数据读取 | `data_reader.py` | 读取CSV/Excel收件人数据 |
| 模板渲染 | `template_renderer.py` | 使用Jinja2渲染邮件模板 |
| 邮件发送 | `email_sender.py` | 构建和发送邮件，管理SMTP连接 |
| 日志系统 | `logger.py` | 记录发送日志和错误信息 |
| 批量管理 | `batch_mailer.py` | 协调各模块，执行批量发送 |
| 命令行接口 | `cli.py` | 提供命令行使用方式 |

## 3. 核心类设计

### 3.1 数据类（Data Classes）

#### 3.1.1 SMTPConfig

```python
@dataclass
class SMTPConfig:
    host: str                    # SMTP服务器地址
    port: int                    # 端口号
    username: str                # 用户名
    password: str                # 密码/授权码
    use_tls: bool = True         # 是否使用STARTTLS
    use_ssl: bool = False        # 是否使用SSL
    timeout: int = 30            # 连接超时(秒)
    sender_name: Optional[str]   # 发件人显示名称
```

#### 3.1.2 RetryConfig

```python
@dataclass
class RetryConfig:
    max_retries: int = 3              # 最大重试次数
    retry_delay: float = 2.0          # 初始重试延迟(秒)
    backoff_multiplier: float = 2.0   # 退避因子
```

#### 3.1.3 Recipient

```python
@dataclass
class Recipient:
    email: str                    # 邮箱地址
    name: Optional[str]           # 姓名
    variables: Dict[str, Any]     # 个性化变量
    attachments: List[str]        # 个性化附件
```

#### 3.1.4 EmailMessage

```python
@dataclass
class EmailMessage:
    subject: str                  # 邮件主题
    body: str                     # 邮件正文
    recipient: Recipient          # 收件人
    is_html: bool = True          # 是否HTML格式
    attachments: List[str]        # 公共附件
```

#### 3.1.5 SendLog

```python
@dataclass
class SendLog:
    email: str                    # 收件人邮箱
    success: bool                 # 是否成功
    attempt: int                  # 尝试次数
    error_message: Optional[str]  # 错误信息
    timestamp: datetime           # 时间戳
```

#### 3.1.6 BatchResult

```python
@dataclass
class BatchResult:
    total: int                    # 总邮件数
    success: int                  # 成功数
    failed: int                   # 失败数
    logs: List[SendLog]           # 详细日志
    start_time: datetime          # 开始时间
    end_time: Optional[datetime]  # 结束时间

    @property
    def success_rate(self) -> float  # 成功率
    @property
    def duration(self) -> float      # 发送耗时(秒)
```

### 3.2 核心类

#### 3.2.1 DataReader

**职责**: 从文件读取收件人数据

**主要方法**:
- `__init__(file_path: str)`: 初始化，验证文件格式
- `read() -> List[Recipient]`: 读取并转换数据
- `_read_csv() -> pd.DataFrame`: 读取CSV
- `_read_excel() -> pd.DataFrame`: 读取Excel
- `_convert_to_recipients(df) -> List[Recipient]`: 数据转换
- `_validate_columns(df)`: 验证必要列

**数据列映射**:
- `email` → 邮箱地址
- `name` → 收件人姓名
- `attachment` → 附件（分号分隔多个）
- 其他列 → 自动加入 variables

#### 3.2.2 TemplateRenderer

**职责**: 渲染邮件模板

**主要方法**:
- `render_from_file(template_file, context) -> str`: 从文件渲染
- `render_from_string(template_string, context) -> str`: 从字符串渲染
- `render_subject(subject_template, context) -> str`: 渲染主题
- `render_body(body_template, context, is_html) -> str`: 渲染正文
- `_is_file_path(template) -> bool`: 判断是否为文件路径

**模板支持**:
- Jinja2完整语法
- 自动HTML转义（可配置）
- 条件判断、循环、过滤器

#### 3.2.3 EmailSender

**职责**: 管理SMTP连接和发送邮件

**主要方法**:
- `connect()`: 建立SMTP连接
- `disconnect()`: 断开连接
- `build_message(email_msg) -> MIMEMultipart`: 构建邮件对象
- `send(email_msg) -> SendLog`: 发送邮件（带重试）
- `__enter__()`, `__exit__()`: 上下文管理器支持

**重试策略**:
- 认证失败不重试
- 网络错误使用指数退避重试
- 最大重试次数可配置

#### 3.2.4 BatchMailer

**职责**: 协调各模块，执行批量发送

**主要方法**:
- `send_from_file(...) -> BatchResult`: 从文件发送
- `send(...) -> BatchResult`: 从列表发送
- `_build_email_message(...) -> EmailMessage`: 构建单封邮件
- `_log_summary(result)`: 输出发送摘要

**工作流程**:
1. 读取/获取收件人列表
2. 遍历收件人
3. 为每个收件人渲染个性化邮件
4. 发送邮件并记录结果
5. 汇总统计并输出

## 4. 关键流程设计

### 4.1 批量发送流程

```
开始
  │
  ▼
┌─────────────────┐
│ 加载SMTP配置     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 读取收件人数据   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 建立SMTP连接     │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ 遍历   │
    │ 收件人  │
    └───┬────┘
        │
        ▼
┌─────────────────┐
│ 渲染模板         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 构建邮件         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     失败      ┌──────────────┐
│  发送邮件        │─────────────▶│  重试策略     │
└────────┬────────┘              └──────┬───────┘
         │                              │
         │ 成功/重试后成功               │ 重试耗尽
         ▼                              ▼
┌─────────────────┐              ┌─────────────────┐
│ 记录成功日志     │              │ 记录失败日志     │
└────────┬────────┘              └────────┬────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ 全部处理完成？    │
              └───────┬─────────┘
                      │ 是
                      ▼
              ┌─────────────────┐
              │ 生成统计报告     │
              └────────┬────────┘
                       │
                       ▼
                     结束
```

### 4.2 重试机制流程

```
发送失败
  │
  ▼
┌─────────────────────────┐
│ 是认证错误？             │
└──────┬──────────────────┘
       │ 是             │ 否
       ▼                ▼
┌────────────┐    ┌────────────────────┐
│ 直接返回失败 │    │ 已达最大重试次数？  │
└────────────┘    └──────┬─────────────┘
                         │ 否       │ 是
                         ▼          ▼
                  ┌──────────┐  ┌──────────┐
                  │ 等待延迟  │  │ 返回失败  │
                  └────┬─────┘  └──────────┘
                       │
                       ▼
                  ┌──────────┐
                  │ 再次发送  │
                  └────┬─────┘
                       │
               ┌───────┴───────┐
               │ 成功?         │
               └──┬─────────┬──┘
                  │ 是      │ 否
                  ▼         ▼
            ┌────────┐  重新检查
            │ 返回成功 │
            └────────┘
```

**退避算法**:
```
第1次重试延迟 = retry_delay * (backoff_multiplier ^ 0)
第2次重试延迟 = retry_delay * (backoff_multiplier ^ 1)
第3次重试延迟 = retry_delay * (backoff_multiplier ^ 2)
...
第n次重试延迟 = retry_delay * (backoff_multiplier ^ (n-1))
```

默认配置（2秒初始延迟，2倍退避）:
- 第1次失败后等待 2秒
- 第2次失败后等待 4秒
- 第3次失败后等待 8秒

## 5. 数据格式规范

### 5.1 收件人CSV格式

```csv
email,name,company,discount_code,attachment
user1@example.com,张三,科技公司,SUMMER10,doc1.pdf
user2@example.com,李四,贸易公司,SUMMER20,doc2.pdf;doc3.xlsx
user3@example.com,王五,,SUMMER30,
```

**列说明**:
- `email` (必需): 收件人邮箱
- `name` (可选): 收件人姓名
- `attachment` (可选): 附件路径，多个用`;`分隔
- 其他列 (可选): 自动作为模板变量

### 5.2 模板语法示例

```html
<!-- 基本变量 -->
<p>您好 {{ name }}！</p>

<!-- 条件判断 -->
{% if is_vip %}
    <p>尊敬的VIP用户</p>
{% else %}
    <p>尊敬的用户</p>
{% endif %}

<!-- 循环 -->
<ul>
{% for item in items %}
    <li>{{ item.name }}: {{ item.price }}</li>
{% endfor %}
</ul>

<!-- 默认值 -->
<p>公司: {{ company | default("未知") }}</p>
```

### 5.3 结果JSON格式

```json
{
  "total": 100,
  "success": 98,
  "failed": 2,
  "success_rate": "98.00%",
  "duration": "120.50秒",
  "start_time": "2024-01-01 10:00:00",
  "end_time": "2024-01-01 10:02:00",
  "logs": [
    {
      "email": "user1@example.com",
      "success": true,
      "attempt": 1,
      "error_message": null,
      "timestamp": "2024-01-01 10:00:05"
    },
    {
      "email": "user2@example.com",
      "success": false,
      "attempt": 3,
      "error_message": "SMTP错误: Connection timed out",
      "timestamp": "2024-01-01 10:00:10"
    }
  ]
}
```

## 6. 错误处理

### 6.1 错误分类

| 错误类型 | 处理策略 | 重试 |
|---------|---------|------|
| 文件不存在 | 抛出异常，提前终止 | 否 |
| 数据格式错误 | 抛出异常，提前终止 | 否 |
| 模板语法错误 | 记录错误，继续下一封 | 否 |
| SMTP认证失败 | 记录错误，终止发送 | 否 |
| SMTP连接超时 | 自动重试 | 是 |
| SMTP服务器错误 | 自动重试 | 是 |
| 附件不存在 | 记录错误，继续下一封 | 否 |

### 6.2 日志级别

| 级别 | 用途 |
|------|------|
| DEBUG | 详细调试信息 |
| INFO | 正常操作信息（发送成功等） |
| WARNING | 警告信息（重试等） |
| ERROR | 错误信息（发送失败等） |
| CRITICAL | 严重错误（系统不可用） |

## 7. 测试策略

### 7.1 测试覆盖范围

| 模块 | 测试类型 | 覆盖率目标 |
|------|---------|-----------|
| 配置管理 | 单元测试 | 90%+ |
| 数据读取 | 单元测试 | 90%+ |
| 模板渲染 | 单元测试 | 90%+ |
| 邮件发送 | 单元测试（Mock） | 85%+ |
| 日志系统 | 单元测试 | 90%+ |
| 批量管理 | 单元测试（Mock） | 85%+ |
| CLI | 单元测试 | 50%+ |

**整体目标**: 80%+

### 7.2 测试用例分类

- **配置模块**: 配置加载、验证、默认值
- **数据模块**: CSV/Excel读取、数据转换、边界情况
- **模板模块**: 字符串渲染、文件渲染、条件循环
- **发送模块**: 连接管理、邮件构建、重试机制
- **批量模块**: 成功/失败场景、异常处理、统计汇总

## 8. 性能指标

| 指标 | 目标值 |
|------|--------|
| 100封邮件发送成功率 | >= 98% |
| 单封邮件发送耗时 | < 3秒 |
| 内存占用（1000封） | < 100MB |
| 测试覆盖率 | >= 80% |

## 9. 扩展规划

- [ ] 支持异步发送（asyncio）
- [ ] 支持并发发送（线程池）
- [ ] 支持邮件模板预览
- [ ] 支持发送进度显示
- [ ] 支持邮件黑名单
- [ ] 支持发送限制（速率控制）
- [ ] 支持更多数据源（数据库、API）
