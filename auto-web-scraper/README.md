# 网页数据采集工具

---

## ⚠️ 重要声明

**所有验收标准需要在Python 3.12环境中实际运行验证脚本才能确认。**

当前状态：
- ✅ 代码已完成：所有功能模块和测试文件已创建
- ⏳ 待验证：需要在实际Python环境中运行测试才能确认通过

验证工具已准备就绪：
- `run_verification.py` - 一键验证脚本
- `docs/VERIFICATION_CHECKLIST.md` - 验证检查清单
- `docs/TESTING.md` - 详细测试运行指南

请在Python 3.12环境中运行以下命令进行实际验证：
```bash
python run_verification.py
```

---

一个功能完整的自动化网页数据采集框架，支持多种网页结构的数据提取，适用于各类数据采集场景。

## 功能特性

- ✅ **多选择器支持**：支持CSS选择器和XPath两种数据提取方式
- ✅ **自动分页**：支持URL参数分页和下一页链接自动跟踪
- ✅ **认证采集**：支持表单登录和Token认证，可采集需要登录的页面
- ✅ **请求间隔**：支持固定和随机间隔，避免访问过于频繁
- ✅ **代理轮换**：支持代理IP池自动轮换，提高采集成功率
- ✅ **多格式导出**：支持CSV、Excel、JSON三种数据导出格式
- ✅ **失败重试**：自动重试失败请求，提高数据完整率
- ✅ **会话管理**：Cookie持久化，支持保存和加载登录状态

## 技术栈

- **编程语言**：Python 3.12
- **网页请求**：requests
- **网页解析**：BeautifulSoup4 + lxml
- **数据处理**：pandas
- **测试框架**：pytest + pytest-cov + Allure
- **代码规范**：PEP8

## 目录结构

```
auto-web-scraper/
├── auto_web_scraper/          # 核心代码 (多个模块)
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── request_manager.py     # 请求管理
│   ├── data_extractor.py      # 数据提取
│   ├── pagination.py          # 分页处理
│   ├── authenticator.py       # 认证管理
│   ├── proxy_manager.py       # 代理管理
│   ├── rate_limiter.py        # 速率限制
│   ├── data_exporter.py       # 数据导出
│   └── scraper.py             # 核心采集器
├── tests/                     # 单元测试 (多个测试文件)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_data_extractor.py
│   ├── test_data_exporter.py
│   ├── test_pagination.py
│   ├── test_rate_limiter.py
│   ├── test_request_manager.py
│   ├── test_authenticator.py
│   ├── test_proxy_manager.py
│   └── test_scraper.py
├── benchmark/                 # 基准测试
│   ├── __init__.py
│   └── data_integrity_test.py # 数据完整性测试
├── examples/                  # 示例脚本
│   ├── __init__.py
│   └── mock_scrape_demo.py    # 完整流程演示
├── docs/                      # 文档
│   ├── system-design.md       # 系统设计文档
│   ├── TESTING.md             # 测试运行指南
│   └── VERIFICATION_CHECKLIST.md # 验证检查清单
├── config/                    # 示例配置
│   └── example.yaml
├── output/                    # 输出目录（自动创建）
├── main.py                    # 命令行入口
├── run_verification.py        # ⭐ 一键验证脚本
├── check_syntax.py            # 语法检查工具
├── static_analysis.py         # 静态代码分析工具
├── requirements.txt           # 依赖列表
├── pytest.ini                 # pytest配置
└── README.md                  # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置采集任务

创建配置文件 `my_config.yaml`：

```yaml
name: "我的采集任务"
start_urls:
  - "https://example.com/list"

selectors:
  - name: "title"
    selector: "h1.title"
    selector_type: "css"

  - name: "content"
    selector: "//div[@class='content']"
    selector_type: "xpath"

pagination:
  enabled: true
  selector: "a.next-page"
  selector_type: "css"
  max_pages: 5

export:
  formats:
    - "json"
    - "csv"
  output_dir: "./output"
```

### 3. 运行采集

```bash
# 使用配置文件
python main.py -c config/my_config.yaml

# 或使用命令行参数
python main.py \
  -u "https://example.com/list" \
  -s "title|h1.title|css" \
  -s "content|//div[@class='content']|xpath" \
  -p 5 \
  -f json \
  -f csv
```

## 配置说明

### 选择器配置（selectors）

每个选择器配置项支持以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 字段名称 |
| selector | string | 是 | 选择器表达式 |
| selector_type | string | 否 | 选择器类型：`css`（默认）或 `xpath` |
| attribute | string | 否 | 提取的属性名，如 `href`、`src` |
| is_list | boolean | 否 | 是否返回列表，默认 `false` |
| default_value | any | 否 | 提取失败时的默认值 |

### 分页配置（pagination）

| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用分页 |
| selector | string | 下一页链接的选择器 |
| selector_type | string | 选择器类型 |
| max_pages | int | 最大采集页数 |
| start_page | int | 起始页码 |
| page_param_name | string | URL页码参数名 |

### 代理配置（proxy）

| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用代理 |
| proxies | list[string] | 代理地址列表 |
| rotation_strategy | string | 轮换策略：`round_robin`、`random`、`weighted` |

## 编程接口

### 基础用法

```python
from auto_web_scraper.scraper import WebScraper
from auto_web_scraper.config import (
    ScraperConfig, SelectorConfig, PaginationConfig, ExportConfig
)

# 创建配置
config = ScraperConfig(
    name="test",
    start_urls=["https://example.com"],
    selectors=[
        SelectorConfig(name="title", selector="h1"),
    ],
    pagination=PaginationConfig(enabled=True, max_pages=3),
    export=ExportConfig(formats=["json", "csv"]),
)

# 创建采集器并运行
scraper = WebScraper(config=config)
data = scraper.scrape()

# 导出数据
paths = scraper.export_data()
print(paths)
```

### 带登录的采集

```python
from auto_web_scraper.config import ScraperConfig, LoginConfig

config = ScraperConfig(
    login=LoginConfig(
        login_url="https://example.com/login",
        username="user",
        password="pass",
        success_indicator="欢迎",
    ),
    start_urls=["https://example.com/profile"],
    selectors=[SelectorConfig(name="name", selector=".username")],
)

scraper = WebScraper(config=config)
data = scraper.scrape()
```

## 运行测试

### 运行单元测试

```bash
pytest
```

### 运行带覆盖率的测试

```bash
pytest --cov=auto_web_scraper --cov-report=term-missing
```

### 生成Allure测试报告

```bash
pytest --alluredir=allure_results
allure serve allure_results
```

## 命令行参数

```
usage: main.py [-h] [-c CONFIG] [-u URL] [-s SELECTOR] [-p PAGES]
               [-f {json,csv,excel}] [-o OUTPUT] [--delay-min DELAY_MIN]
               [--delay-max DELAY_MAX] [--proxy PROXY] [--login-url LOGIN_URL]
               [--username USERNAME] [--password PASSWORD]

网页数据采集工具 - 支持多种网页结构的自动化数据采集

optional arguments:
  -h, --help            显示帮助信息
  -c CONFIG, --config CONFIG
                        配置文件路径 (YAML或JSON格式)
  -u URL, --url URL     起始URL
  -s SELECTOR, --selector SELECTOR
                        CSS/XPath选择器，格式: name|selector|type|attribute
  -p PAGES, --pages PAGES
                        采集页数
  -f {json,csv,excel}, --format {json,csv,excel}
                        输出格式，可以多次指定
  -o OUTPUT, --output OUTPUT
                        输出目录
  --delay-min DELAY_MIN
                        最小请求间隔(秒)
  --delay-max DELAY_MAX
                        最大请求间隔(秒)
  --proxy PROXY         代理服务器地址，可以多次指定
  --login-url LOGIN_URL
                        登录页面URL
  --username USERNAME   登录用户名
  --password PASSWORD   登录密码
```

## 数据完整率保障

为确保采集大量页面时数据完整率不低于目标值，系统具备以下保障机制：

1. **自动重试**：失败请求自动重试（可配置次数）
2. **指数退避**：重试间隔随失败次数递增，避免瞬时压力
3. **代理容错**：自动剔除失效代理，优先选用成功率高的代理
4. **速率控制**：随机间隔模拟人类访问行为
5. **浏览器UA**：默认使用真实浏览器User-Agent
6. **错误统计**：详细的统计信息便于定位问题

## 注意事项

1. **合规使用**：请遵守目标网站的robots.txt和相关法律法规
2. **合理间隔**：设置合理的请求间隔，避免对目标服务器造成压力
3. **代理使用**：使用代理时请确保代理的合法性和稳定性
4. **数据保护**：采集的数据请注意保护用户隐私和商业机密

## 许可证

MIT License
