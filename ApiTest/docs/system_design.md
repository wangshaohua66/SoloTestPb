# API接口自动化测试工具 - 系统设计文档

## 1. 系统概述

API接口自动化测试工具是一个功能强大的RESTful API测试框架，支持测试用例管理、参数化、断言、依赖管理和测试报告生成。

### 1.1 设计目标
- 易用性：通过YAML配置文件定义测试用例，无需编码
- 灵活性：支持多种HTTP方法、参数化、断言类型
- 可扩展性：支持自定义函数和断言
- 并发执行：支持大规模测试用例并发执行
- 完整报告：生成HTML、JSON格式的测试报告

## 2. 架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                        测试运行层                             │
│            ┌───────────────────────────────────┐            │
│            │            TestRunner             │            │
│            └───────────────────────────────────┘            │
└──────────────────────────────────────┬──────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────┐
│                核心模块层            │                      │
│    ┌──────────┐   ┌──────────┐   ┌┴─────────┐   ┌─────────┐│
│    │ Config   │   │ HTTP     │   │ Variable │   │ Assertion││
│    │ Parser   │   │ Client   │   │ Engine   │   │ Engine  ││
│    └──────────┘   └──────────┘   └──────────┘   └─────────┘│
│    ┌──────────────┐   ┌───────────────────┐                 │
│    │ Dependency   │   │ Report            │                 │
│    │ Manager      │   │ Generator         │                 │
│    └──────────────┘   └───────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────┐
│                测试配置层            │                      │
│          YAML测试用例配置文件        │                      │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构
```
ApiTest/
├── core/                          # 核心模块
│   ├── __init__.py
│   ├── config_parser.py           # YAML配置解析器
│   ├── http_client.py             # HTTP请求客户端
│   ├── variable_engine.py         # 变量解析引擎
│   ├── assertion_engine.py        # 断言引擎
│   ├── dependency_manager.py      # 依赖管理器
│   ├── report_generator.py        # 报告生成器
│   └── test_runner.py             # 测试运行器
├── testcases/                     # 测试用例目录
│   ├── example_get.yaml
│   ├── example_post.yaml
│   └── example_dependency.yaml
├── tests/                         # 单元测试目录
│   ├── test_api.py
│   ├── test_config_parser.py
│   ├── test_variable_engine.py
│   └── test_assertion_engine.py
├── reports/                       # 测试报告输出目录
├── docs/                          # 文档目录
│   └── system_design.md
├── requirements.txt               # 依赖包列表
├── pytest.ini                     # pytest配置
├── conftest.py                    # pytest fixtures
└── README.md                      # 项目说明
```

## 3. 核心模块设计

### 3.1 ConfigParser (配置解析器)

#### 功能说明
- 解析YAML格式的测试用例配置文件
- 支持单个文件或整个目录解析
- 标准化测试用例格式
- 支持按ID、标签筛选测试用例

#### 主要方法
```python
parse_file(file_path: str) -> List[Dict]
parse_directory(dir_path: str) -> List[Dict]
get_test_case_by_id(case_id: str) -> Dict
get_test_cases_by_tag(tag: str) -> List[Dict]
get_all_test_cases() -> List[Dict]
```

#### 数据结构
```python
{
    'id': str,                    # 测试用例ID
    'name': str,                  # 测试用例名称
    'description': str,           # 描述
    'tags': List[str],            # 标签列表
    'module': str,                # 模块名
    'enabled': bool,              # 是否启用
    'request': Dict,              # 请求配置
    'assertions': List[Dict],     # 断言列表
    'variables': Dict,            # 变量定义
    'depends_on': List[str],      # 依赖的用例ID
    'extract': Dict,              # 提取变量配置
    'timeout': int                # 请求超时时间
}
```

### 3.2 HttpClient (HTTP请求客户端)

#### 功能说明
- 支持GET、POST、PUT、DELETE、PATCH等HTTP方法
- 基于requests.Session实现连接复用
- 支持基础URL设置
- 记录请求响应时间

#### 主要方法
```python
request(method: str, url: str, **kwargs) -> Dict
get(url: str, **kwargs) -> Dict
post(url: str, **kwargs) -> Dict
put(url: str, **kwargs) -> Dict
delete(url: str, **kwargs) -> Dict
```

#### 响应数据结构
```python
{
    'success': bool,              # 请求是否成功
    'request': Dict,              # 请求信息
    'response': {
        'status_code': int,       # 状态码
        'headers': Dict,          # 响应头
        'body': Any,              # 响应体
        'text': str,              # 原始响应文本
        'response_time_ms': int,  # 响应时间(ms)
        'cookies': Dict           # Cookies
    },
    'error': Dict                 # 错误信息
}
```

### 3.3 VariableEngine (变量解析引擎)

#### 功能说明
- 支持${variable_name}语法的变量替换
- 内置函数生成测试数据（Faker集成）
- 支持自定义函数注册
- 递归解析嵌套数据结构

#### 内置函数列表
```
random_int(min, max)        # 生成随机整数
random_string(length)       # 生成随机字符串
random_float(min, max, precision)  # 生成随机浮点数
random_choice(*args)        # 列表中随机选择
uuid()                      # 生成UUID
timestamp(unit)             # 生成时间戳
datetime(format)            # 生成日期时间
date(format)                # 生成日期
today(format)               # 生成今天日期
future_date(days, format)   # 生成未来日期
past_date(days, format)     # 生成过去日期
name()                      # 生成随机姓名
phone()                     # 生成随机手机号
email()                     # 生成随机邮箱
address()                   # 生成随机地址
city()                      # 生成城市名
company()                   # 生成公司名
job()                       # 生成职位
text()                      # 生成随机文本
sentence()                  # 生成句子
word()                      # 生成单词
url()                       # 生成URL
ipv4()                      # 生成IP地址
user_name()                 # 生成用户名
password()                  # 生成密码
credit_card()               # 生成信用卡号
inc(start, step)            # 生成递增数字
```

### 3.4 AssertionEngine (断言引擎)

#### 功能说明
- 支持多种断言类型
- 支持JSONPath路径表达式
- 支持类型断言
- 返回详细的断言结果

#### 支持的断言类型
```python
{
    'status_code': '状态码断言',
    'status': '状态码断言(别名)',
    'body': '响应体包含断言',
    'json': 'JSON值断言',
    'json_path': 'JSON路径断言',
    'headers': '响应头断言',
    'header': '响应头断言(别名)',
    'response_time': '响应时间断言',
    'contains': '包含断言',
    'not_contains': '不包含断言',
    'equals': '相等断言',
    'not_equals': '不相等断言',
    'greater_than': '大于断言',
    'less_than': '小于断言',
    'regex': '正则匹配断言',
    'exists': '存在断言',
    'not_exists': '不存在断言',
    'type': '类型断言'
}
```

### 3.5 DependencyManager (依赖管理器)

#### 功能说明
- 管理测试用例之间的依赖关系
- 从响应中提取数据存入上下文
- 解析依赖占位符
- 检测循环依赖
- 按依赖关系排序执行顺序

#### 主要方法
```python
add_to_context(key: str, value: Any)
get_from_context(key: str, default: Any = None) -> Any
extract_data(response: Dict, extract_config: Dict) -> Dict
resolve_dependencies(test_case: Dict) -> Dict
check_dependencies_met(test_case: Dict) -> Tuple[bool, List[str]]
get_execution_order(test_cases: List[Dict]) -> List[Dict]
```

### 3.6 ReportGenerator (报告生成器)

#### 功能说明
- 生成美观的HTML测试报告
- 支持JSON格式报告导出
- 支持Markdown格式报告导出
- 按模块、标签统计结果
- 展示请求响应详情

#### HTML报告特性
- 响应式设计
- 测试摘要统计
- 模块/标签维度统计
- 可展开的测试详情
- 代码高亮展示请求响应
- 断言结果展示

### 3.7 TestRunner (测试运行器)

#### 功能说明
- 整合所有核心模块
- 加载并执行测试用例
- 支持pytest集成
- 支持并发执行
- 生成测试报告

#### 执行流程
```
1. 加载测试用例 (YAML -> Dict)
2. 分析依赖关系，确定执行顺序
3. 循环执行每个测试用例:
   a. 检查依赖是否满足
   b. 解析变量和函数
   c. 发送HTTP请求
   d. 执行断言
   e. 提取响应数据
   f. 记录测试结果
4. 生成测试报告
```

## 4. 测试用例格式说明

### 4.1 完整示例
```yaml
id: test_case_001
name: 用户登录测试
description: 测试用户登录接口
tags:
  - auth
  - smoke
module: user
enabled: true
timeout: 30

variables:
  base_url: https://api.example.com
  username: ${user_name()}
  password: ${password()}

depends_on:
  - test_case_000

request:
  method: POST
  url: ${base_url}/api/auth/login
  headers:
    Content-Type: application/json
    User-Agent: ApiTest/1.0
  json:
    username: ${username}
    password: ${password}

assertions:
  - type: status_code
    expected: 200
    message: 登录成功状态码应为200

  - type: json_path
    path: data.token
    message: 应返回访问令牌

  - type: response_time
    max: 1000
    message: 响应时间应小于1秒

extract:
  access_token: data.token
  user_id: data.user.id
```

### 4.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 测试用例唯一标识 |
| name | string | 是 | 测试用例名称 |
| description | string | 否 | 测试用例描述 |
| tags | list[string] | 否 | 标签列表，用于筛选 |
| module | string | 否 | 模块名，用于报告统计 |
| enabled | bool | 否 | 是否启用，默认true |
| timeout | int | 否 | 请求超时时间(秒)，默认30 |
| variables | dict | 否 | 变量定义 |
| depends_on | list[string] | 否 | 依赖的测试用例ID列表 |
| request | dict | 是 | 请求配置 |
| request.method | string | 是 | HTTP方法: GET/POST/PUT/DELETE等 |
| request.url | string | 是 | 请求URL |
| request.headers | dict | 否 | 请求头 |
| request.params | dict | 否 | URL查询参数 |
| request.json | dict | 否 | JSON请求体 |
| request.data | dict/string | 否 | 表单数据或文本 |
| request.files | dict | 否 | 文件上传 |
| assertions | list[dict] | 否 | 断言列表 |
| extract | dict | 否 | 提取响应数据配置 |

## 5. 技术选型

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 开发语言 |
| requests | 2.31+ | HTTP客户端 |
| PyYAML | 6.0+ | YAML解析 |
| pytest | 7.4+ | 测试框架 |
| allure-pytest | 2.13+ | Allure报告 |
| pytest-html | 4.0+ | HTML报告 |
| Jinja2 | 3.1+ | 模板引擎 |
| Faker | 20.0+ | 测试数据生成 |
| pytest-xdist | 3.3+ | 并发执行 |

## 6. 部署与运行

### 6.1 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 6.2 安装依赖
```bash
pip install -r requirements.txt
```

### 6.3 运行测试

#### 使用pytest运行
```bash
# 运行所有测试
pytest -v

# 运行带特定标签的测试
pytest -v -m smoke

# 生成Allure报告
pytest -v --alluredir=allure-results
allure serve allure-results

# 并发执行
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

## 7. 扩展开发

### 7.1 自定义函数
```python
from core import VariableEngine

def my_function(param1, param2):
    return f"result: {param1}, {param2}"

engine = VariableEngine()
engine.register_function('my_func', my_function)
```

### 7.2 自定义断言
```python
from core import AssertionEngine

def custom_assertion(assertion, response):
    expected = assertion.get('expected')
    actual = response.get('some_field')
    return actual == expected, actual

engine = AssertionEngine()
engine.assertion_types['custom'] = custom_assertion
```

## 8. 最佳实践

### 8.1 测试用例设计
- 每个测试用例关注一个场景
- 测试用例之间应独立，尽量减少依赖
- 使用标签分类管理测试用例
- 合理使用变量和函数生成测试数据

### 8.2 断言最佳实践
- 首先断言状态码
- 关键业务字段必须断言
- 不要过度断言，避免测试脆弱
- 使用有意义的错误消息

### 8.3 性能考虑
- 使用连接复用(HttpClient的Session)
- 合理设置超时时间
- 使用并发执行大规模测试
- 测试报告异步生成

## 9. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-01-01 | 初始版本，实现核心功能 |

## 10. 联系方式

- 项目地址: GitHub
- 问题反馈: Issues
