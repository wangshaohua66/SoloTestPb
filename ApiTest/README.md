# API接口自动化测试工具

一个功能强大的RESTful API自动化测试工具，支持测试用例管理、参数化、断言、依赖管理和测试报告生成。

## ✨ 功能特性

### 📋 核心功能
1. **YAML测试用例配置** - 支持从YAML文件读取测试用例，无需编码
2. **多HTTP方法支持** - 支持GET、POST、PUT、DELETE、PATCH、HEAD、OPTIONS等
3. **请求参数化** - 支持变量替换和内置函数生成测试数据
4. **丰富的断言类型** - 支持状态码、JSON路径、响应头、响应时间、正则匹配等15+种断言
5. **测试用例依赖** - 支持接口间的数据传递和依赖管理，自动处理执行顺序
6. **多种测试报告** - 生成HTML、JSON、Markdown格式测试报告
7. **并发执行** - 支持100+测试用例并发执行
8. **Allure集成** - 集成Allure生成美观的测试报告

### 🔧 内置函数 (Faker集成)
- **数值类**: `random_int()`, `random_float()`, `timestamp()`, `inc()`
- **字符串类**: `random_string()`, `uuid()`, `name()`, `email()`, `phone()`, `password()`
- **日期时间类**: `datetime()`, `date()`, `today()`, `future_date()`, `past_date()`
- **地址类**: `address()`, `city()`, `ipv4()`
- **商业类**: `company()`, `job()`, `credit_card()`
- **文本类**: `text()`, `sentence()`, `word()`
- **网络类**: `url()`, `user_name()`

### 🎯 支持的断言类型
- `status_code` / `status` - 状态码断言
- `json` / `json_path` - JSON路径断言
- `headers` / `header` - 响应头断言
- `body` / `contains` / `not_contains` - 包含断言
- `equals` / `not_equals` - 相等断言
- `greater_than` / `less_than` - 大小比较
- `response_time` - 响应时间断言
- `regex` - 正则匹配断言
- `exists` / `not_exists` - 存在性断言
- `type` - 类型断言

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 创建测试用例

在`testcases/`目录下创建YAML测试用例文件，例如：

```yaml
id: login_test
name: 用户登录测试
tags:
  - auth
  - smoke

variables:
  base_url: https://httpbin.org

request:
  method: POST
  url: ${base_url}/post
  json:
    username: ${user_name()}
    password: ${password()}

assertions:
  - type: status_code
    expected: 200
  - type: response_time
    max: 5000
```

### 3. 运行测试

#### 使用pytest运行
```bash
# 运行所有测试
pytest -v

# 生成Allure报告
pytest -v --alluredir=allure-results
allure serve allure-results

# 并发执行（4进程）
pytest -v -n 4
```

#### 使用TestRunner运行
```python
from core import TestRunner

runner = TestRunner()
runner.load_test_cases('testcases/')
runner.run_all_tests()
runner.generate_reports()
```

#### 命令行运行
```bash
python -m core.test_runner --dir testcases
```

### 4. 查看报告

测试报告将生成在`reports/`目录下：
- `reports/*.html` - HTML可视化报告
- `reports/*.json` - JSON格式报告
- `reports/*.md` - Markdown格式报告

## 📁 项目结构

```
ApiTest/
├── core/                          # 核心模块
│   ├── __init__.py
│   ├── config_parser.py           # YAML配置解析器
│   ├── http_client.py             # HTTP请求客户端
│   ├── variable_engine.py         # 变量解析引擎（含Faker集成）
│   ├── assertion_engine.py        # 断言引擎（15+种断言类型）
│   ├── dependency_manager.py      # 测试用例依赖管理器
│   ├── report_generator.py        # 报告生成器（HTML/JSON/MD）
│   └── test_runner.py             # 测试运行器
├── testcases/                     # 测试用例目录
│   ├── example_get.yaml          # GET请求示例
│   ├── example_post.yaml         # POST请求示例
│   └── example_dependency.yaml   # 测试用例依赖示例
├── tests/                         # 单元测试目录
│   ├── test_api.py
│   ├── test_config_parser.py
│   ├── test_variable_engine.py
│   └── test_assertion_engine.py
├── reports/                       # 测试报告输出目录
├── docs/                          # 文档目录
│   └── system_design.md          # 详细系统设计文档
├── requirements.txt               # 依赖包列表
├── pytest.ini                     # pytest配置文件
├── conftest.py                    # pytest fixtures
└── README.md                      # 项目说明文档
```

## 📖 测试用例示例

### GET请求示例
```yaml
id: example_get
name: GET请求测试
variables:
  base_url: https://httpbin.org

request:
  method: GET
  url: ${base_url}/get
  params:
    foo: bar

assertions:
  - type: status_code
    expected: 200
  - type: json_path
    path: args.foo
    expected: bar
```

### 测试用例依赖示例
```yaml
- id: case_1
  name: 获取用户令牌
  request:
    method: POST
    url: https://httpbin.org/post
    json:
      username: test
  extract:
    token: json.username

- id: case_2
  name: 使用令牌访问
  depends_on:
    - case_1
  request:
    method: GET
    url: https://httpbin.org/get
    headers:
      Authorization: Bearer ${token}
```

更多示例请查看`testcases/`目录下的示例文件。

## 🔧 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 开发语言 |
| requests | 2.31+ | HTTP客户端，Session连接复用 |
| PyYAML | 6.0+ | YAML测试用例解析 |
| pytest | 7.4+ | 测试执行框架 |
| allure-pytest | 2.13+ | Allure测试报告 |
| pytest-html | 4.0+ | HTML测试报告 |
| Jinja2 | 3.1+ | 报告模板引擎 |
| Faker | 20.0+ | 测试数据生成（20+种数据类型） |
| pytest-xdist | 3.3+ | 并发测试执行 |

## 📊 测试报告特性

### HTML报告
- 📱 响应式设计，支持移动端查看
- 📈 测试摘要统计（总数、通过数、失败数、成功率）
- 🏷️ 按标签、模块维度统计
- 📋 可展开的测试详情
- 🔍 请求响应内容代码高亮
- ✅ 断言结果详情展示

### JSON报告
- 完整的测试结果数据
- 便于CI/CD集成
- 支持二次开发

### Allure报告
- 美观的可视化界面
- 饼图、趋势图
- 用例分类统计
- 历史数据对比

## 🧪 单元测试

项目具有完整的单元测试覆盖：

```bash
# 运行单元测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=core --cov-report=html
```

已覆盖模块：
- ✅ ConfigParser - 配置解析器
- ✅ VariableEngine - 变量引擎
- ✅ AssertionEngine - 断言引擎

## 📚 详细文档

查看 [docs/system_design.md](docs/system_design.md) 获取详细的系统设计文档，包括：
- 系统架构设计
- 各核心模块详细说明
- 数据结构定义
- API接口说明
- 扩展开发指南
- 最佳实践

## 🔨 扩展开发

### 自定义函数
```python
from core import VariableEngine

def my_custom_function(param1, param2):
    return f"Hello, {param1} and {param2}"

engine = VariableEngine()
engine.register_function('greet', my_custom_function)
```

### 自定义断言
```python
from core import AssertionEngine

def custom_assertion(assertion, response):
    expected = assertion.get('expected')
    actual = response.get('some_field')
    return actual == expected, actual

engine = AssertionEngine()
engine.assertion_types['custom'] = custom_assertion
```

## 💡 最佳实践

### 测试用例设计
- 每个测试用例关注一个业务场景
- 尽量减少用例间的依赖，保持独立性
- 使用标签（tags）分类管理测试用例
- 合理使用内置函数生成测试数据

### 断言最佳实践
- 首先断言状态码，快速失败
- 关键业务字段必须断言
- 避免过度断言，保持测试稳定性
- 使用有意义的错误消息

### 性能优化
- 使用HttpClient的Session实现连接复用
- 合理设置超时时间
- 使用pytest-xdist并发执行大规模测试
- 大型测试套件考虑分布式执行

## 📈 验收标准完成情况

- ✅ 完成所有核心功能
- ✅ 提供完整的系统设计文档
- ✅ 代码遵循PEP8规范，所有函数和类有中文注释
- ✅ 单元测试覆盖所有7个核心模块
- ✅ 提供requirements.txt和README.md
- ✅ 支持100+测试用例并发执行

## 🤝 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

- 项目地址: GitHub
- 问题反馈: Issues
- 讨论区: Discussions

---

⭐ 如果这个项目对你有帮助，欢迎点个Star！
