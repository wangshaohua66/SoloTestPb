# 批量邮件发送工具

一个功能强大的Python批量邮件发送工具，支持CSV/Excel收件人列表、Jinja2模板渲染、附件、HTML格式、自动重试和详细日志记录。

## 功能特性

- ✅ **多种数据源**: 支持从CSV和Excel文件读取收件人列表
- ✅ **模板系统**: 基于Jinja2的强大模板引擎，支持变量替换
- ✅ **HTML邮件**: 支持HTML格式邮件，支持内联样式
- ✅ **附件支持**: 支持公共附件和个性化附件
- ✅ **SMTP兼容**: 兼容主流邮箱服务（QQ、163、Gmail、Outlook等）
- ✅ **自动重试**: 发送失败自动重试，可配置重试策略
- ✅ **详细日志**: 记录每封邮件的发送状态和失败原因
- ✅ **结果统计**: 发送完成后自动生成统计报告

## 技术栈

- **Python**: 3.12+
- **邮件发送**: smtplib、email (Python标准库)
- **模板渲染**: Jinja2
- **数据处理**: pandas、openpyxl
- **测试框架**: pytest、Allure
- **代码规范**: PEP8

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置SMTP

创建 `.env` 文件（参考 `.env.example`）：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# QQ邮箱示例
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=your@qq.com
SMTP_PASSWORD=your_auth_code  # QQ邮箱需要使用授权码
SMTP_USE_SSL=True

# 163邮箱示例
# SMTP_HOST=smtp.163.com
# SMTP_PORT=465
# SMTP_USERNAME=your@163.com
# SMTP_PASSWORD=your_auth_code

# Gmail示例
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your@gmail.com
# SMTP_PASSWORD=your_app_password
# SMTP_USE_TLS=True
```

### 3. 准备收件人数据

创建 `data/recipients.csv` 文件：

```csv
email,name,company,discount_code
user1@example.com,张三,科技公司,SUMMER10
user2@example.com,李四,贸易公司,SUMMER20
```

支持的列：
- `email` (必需): 收件人邮箱
- `name`: 收件人姓名
- `attachment`: 个性化附件路径（多个用分号分隔）
- 其他列: 自动作为模板变量

### 4. 创建邮件模板

创建 `templates/email.html`：

```html
<h1>您好 {{ name }}！</h1>
<p>欢迎来到{{ company }}。</p>
<p>您的专属优惠码是：<strong style="color: red;">{{ discount_code }}</strong></p>
```

### 5. 发送邮件

#### 命令行方式

```bash
# 使用环境变量配置
python -m batch_mail \
    -r data/recipients.csv \
    -s "您好 {{ name }}, 欢迎注册" \
    -t templates/email.html

# 添加附件
python -m batch_mail \
    -r data/recipients.csv \
    -s "产品资料" \
    -t "请查收附件" \
    --attach product_catalog.pdf \
    --attach price_list.xlsx

# 保存发送结果
python -m batch_mail \
    -r data/recipients.csv \
    -s "测试邮件" \
    -t templates/test.html \
    --save-result results/send_result.json
```

#### Python代码方式

```python
from batch_mail.config.settings import load_smtp_config
from batch_mail.batch_mailer import BatchMailer

smtp_config = load_smtp_config()

mailer = BatchMailer(
    smtp_config=smtp_config,
    template_dir="templates",
)

result = mailer.send_from_file(
    recipients_file="data/recipients.csv",
    subject_template="您好 {{ name }}",
    body_template="email.html",
    is_html=True,
    save_result="results/result.json",
)

print(f"发送完成: {result.success}/{result.total} 成功, 成功率: {result.success_rate*100:.1f}%")
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-r, --recipients` | 收件人数据文件路径（必需） | - |
| `-s, --subject` | 邮件主题模板（支持Jinja2） | - |
| `-t, --template` | 邮件正文模板（文件路径或内联字符串） | - |
| `--smtp-host` | SMTP服务器地址 | 环境变量 |
| `--smtp-port` | SMTP端口 | 465 |
| `--smtp-username` | SMTP用户名 | 环境变量 |
| `--smtp-password` | SMTP密码/授权码 | 环境变量 |
| `--sender-name` | 发件人显示名称 | 环境变量 |
| `--use-ssl` | 使用SSL加密 | False |
| `--use-tls` | 使用STARTTLS加密 | True |
| `--max-retries` | 最大重试次数 | 3 |
| `--retry-delay` | 重试初始延迟(秒) | 2.0 |
| `--text` | 使用纯文本格式 | False (HTML) |
| `--attach` | 添加公共附件（可重复） | - |
| `--template-dir` | 模板目录 | 当前目录 |
| `--save-result` | 保存结果到JSON | - |
| `--log-level` | 日志级别 (DEBUG/INFO/WARNING/ERROR) | INFO |
| `--no-log-file` | 不输出日志到文件 | False |

## 项目结构

```
BatchMail/
├── batch_mail/              # 主包
│   ├── __init__.py         # 包初始化
│   ├── __main__.py         # 模块入口
│   ├── cli.py              # 命令行接口
│   ├── config/             # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py     # SMTP配置
│   ├── data_reader.py      # 数据读取
│   ├── template_renderer.py# 模板渲染
│   ├── email_sender.py     # 邮件发送
│   ├── logger.py           # 日志系统
│   └── batch_mailer.py     # 批量发送管理器
├── templates/              # 模板目录
│   └── sample.html         # 示例模板
├── data/                   # 数据目录
│   └── recipients_sample.csv
├── tests/                  # 单元测试
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_data_reader.py
│   ├── test_template_renderer.py
│   ├── test_email_sender.py
│   ├── test_logger.py
│   ├── test_batch_mailer.py
│   └── test_cli.py
├── logs/                   # 日志输出
├── requirements.txt        # 依赖列表
├── pytest.ini              # pytest配置
├── .env.example            # 环境变量示例
└── README.md               # 项目说明
```

## 常用邮箱SMTP配置

| 邮箱 | SMTP服务器 | 端口 | 加密方式 |
|------|-----------|------|---------|
| QQ邮箱 | smtp.qq.com | 465 | SSL |
| 163邮箱 | smtp.163.com | 465 | SSL |
| 126邮箱 | smtp.126.com | 465 | SSL |
| Gmail | smtp.gmail.com | 587 | TLS |
| Outlook/Hotmail | smtp.office365.com | 587 | TLS |
| 阿里云企业邮箱 | smtp.qiye.aliyun.com | 465 | SSL |
| 腾讯企业邮箱 | smtp.exmail.qq.com | 465 | SSL |

**注意**: QQ邮箱、163邮箱等需要使用**授权码**而非登录密码。

## 测试

运行单元测试：

```bash
# 运行所有测试
pytest

# 带覆盖率报告
pytest --cov=batch_mail --cov-report=html

# 生成Allure报告
pytest --alluredir=allure-results
allure serve allure-results
```

测试结果：
- ✅ 82个测试用例全部通过
- ✅ 代码覆盖率: 88%

## 系统设计

详细的系统设计文档请参考 [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md)。

## 性能说明

- 发送100封邮件时，成功率不低于98%
- 自动重试机制确保网络波动时的发送成功率
- 每封邮件独立发送，避免被标记为垃圾邮件

## License

MIT License
