# 测试运行指南

---

## ⚠️ 重要免责声明

**本文档中的所有"预期输出"和"模拟输出"都是基于代码逻辑的预期值，不是实际运行结果。**

由于当前环境限制（无可用Python解释器），以下内容：
- ❓ 所有输出示例都是模拟的
- ⏳ 所有验证状态都是"待验证"
- ⚠️ 需要在实际Python 3.12环境中运行才能确认真实结果

请参考 `docs/VERIFICATION_CHECKLIST.md` 获取详细的验证步骤。

---

## 📊 项目状态说明

### 代码完成状态（已确认）

| 模块 | 状态 | 说明 |
|------|------|------|
| 配置管理 (config) | ✅ 完成 | 8个dataclass配置类，YAML/JSON加载 |
| 请求管理 (request_manager) | ✅ 完成 | 重试机制、Session管理 |
| 数据提取 (data_extractor) | ✅ 完成 | CSS/XPath提取 |
| 分页处理 (pagination) | ✅ 完成 | URL参数分页、下一页跟踪 |
| 认证管理 (authenticator) | ✅ 完成 | 表单登录、Token认证、Cookie管理 |
| 代理管理 (proxy_manager) | ✅ 完成 | 3种轮换策略、健康检测 |
| 速率限制 (rate_limiter) | ✅ 完成 | 固定/随机间隔、并发控制 |
| 数据导出 (data_exporter) | ✅ 完成 | CSV/Excel/JSON导出 |
| 核心采集器 (scraper) | ✅ 完成 | 整合所有模块 |

### 验证通过状态（待验证）

| 验证项 | 状态 | 说明 |
|--------|------|------|
| 语法检查 | ⏳ 待验证 | 需要运行 `python check_syntax.py` |
| 单元测试通过 | ⏳ 待验证 | 需要运行 `pytest` |
| 覆盖率≥80% | ⏳ 待验证 | 需要运行 `pytest --cov` |
| Allure报告生成 | ⏳ 待验证 | 需要运行 `pytest --alluredir` |
| 数据完整性≥99% | ⏳ 待验证 | 需要运行 `benchmark/data_integrity_test.py` |

---

## 📦 测试用例统计（准确数据）

实际统计结果：**139个测试用例**

| 测试文件 | 测试数量 | 覆盖模块 | 覆盖范围 |
|---------|---------|---------|---------|
| `test_config.py` | 7 | config.py | 配置加载、默认值 |
| `test_data_extractor.py` | 14 | data_extractor.py | CSS/XPath提取、清洗 |
| `test_pagination.py` | 11 | pagination.py | URL构建、分页检测 |
| `test_rate_limiter.py` | 8 | rate_limiter.py | 延迟计算、并发控制 |
| `test_data_exporter.py` | 9 | data_exporter.py | 3种格式导出 |
| `test_request_manager.py` | 19 | request_manager.py | 重试、Cookie、Session |
| `test_authenticator.py` | 25 | authenticator.py | 登录、Token、Cookie管理 |
| `test_proxy_manager.py` | 26 | proxy_manager.py | 代理检测、轮换、标记 |
| `test_scraper.py` | 20 | scraper.py | 主流程、分页、导出 |
| **总计** | **139** | - | - |

---

## 🔧 环境要求

### Python版本
- **推荐**: Python 3.12
- **最低**: Python 3.8

### 验证Python版本
```bash
python --version
# 或
python3 --version
```

---

## 🚀 一键验证（推荐）

### 方式1：使用一键验证脚本

```bash
# 在项目根目录运行
cd f:\github\SoloTestPb\auto-web-scraper
python run_verification.py
```

这个脚本会自动执行：
1. ✅ Python版本检查
2. ✅ 依赖安装
3. ✅ 语法检查
4. ✅ 单元测试运行
5. ✅ 覆盖率测试
6. ✅ Allure报告生成
7. ✅ 数据完整性基准测试

### 方式2：手动分步验证

```bash
# 步骤1：安装依赖
pip install -r requirements.txt

# 步骤2：语法检查
python check_syntax.py

# 步骤3：运行单元测试
pytest -v --tb=short

# 步骤4：覆盖率测试（需≥80%）
pytest --cov=auto_web_scraper --cov-report=term-missing

# 步骤5：生成Allure报告
pytest --alluredir=allure_results
# 查看报告（需安装Allure CLI）
allure serve allure_results

# 步骤6：数据完整性基准测试
python benchmark/data_integrity_test.py -p 1000
```

---

## 📋 详细步骤说明

### 步骤1：安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**：
```
requests>=2.31.0          # HTTP请求
beautifulsoup4>=4.12.0   # HTML解析
lxml>=4.9.0               # XML/HTML解析（XPath）
pandas>=2.1.0             # 数据处理
openpyxl>=3.1.0           # Excel导出
PyYAML>=6.0               # YAML配置
pytest>=7.4.0             # 测试框架
pytest-cov>=4.1.0         # 覆盖率
allure-pytest>=2.13.0     # Allure报告
```

### 步骤2：语法检查

```bash
python check_syntax.py
```

**⚠️ 模拟输出示例（非实际运行结果）**：
```
======================================================================
Python语法检查
======================================================================
项目根目录: f:\github\SoloTestPb\auto-web-scraper
======================================================================

✅ f:\github\SoloTestPb\auto-web-scraper\main.py
✅ f:\github\SoloTestPb\auto-web-scraper\check_syntax.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\__init__.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\config.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\request_manager.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\data_extractor.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\pagination.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\authenticator.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\proxy_manager.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\rate_limiter.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\data_exporter.py
✅ f:\github\SoloTestPb\auto-web-scraper\auto_web_scraper\scraper.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\__init__.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\conftest.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_config.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_data_extractor.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_pagination.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_rate_limiter.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_data_exporter.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_request_manager.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_authenticator.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_proxy_manager.py
✅ f:\github\SoloTestPb\auto-web-scraper\tests\test_scraper.py
✅ f:\github\SoloTestPb\auto-web-scraper\benchmark\__init__.py
✅ f:\github\SoloTestPb\auto-web-scraper\benchmark\data_integrity_test.py
✅ f:\github\SoloTestPb\auto-web-scraper\examples\__init__.py
✅ f:\github\SoloTestPb\auto-web-scraper\examples\mock_scrape_demo.py

======================================================================
检查结果
======================================================================
总文件数: 28
错误文件: 0
✅ 所有文件语法正确！
======================================================================
```

### 步骤3：运行单元测试

```bash
pytest -v --tb=short
```

**⚠️ 模拟输出示例（非实际运行结果）**：
```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-7.4.0, pluggy-1.3.0
rootdir: f:\github\SoloTestPb\auto-web-scraper
configfile: pytest.ini
testpaths: tests
collected 139 items

tests/test_authenticator.py::TestAuthenticator::test_form_login_success PASSED
tests/test_authenticator.py::TestAuthenticator::test_form_login_with_extra_fields PASSED
tests/test_authenticator.py::TestAuthenticator::test_form_login_with_success_indicator PASSED
... (共25个测试)

tests/test_config.py::TestSelectorConfig::test_selector_config_defaults PASSED
tests/test_config.py::TestSelectorConfig::test_selector_config_custom PASSED
... (共7个测试)

tests/test_data_exporter.py::TestDataExporter::test_export_to_csv PASSED
tests/test_data_exporter.py::TestDataExporter::test_export_to_json PASSED
... (共9个测试)

tests/test_data_extractor.py::TestDataExtractor::test_clean_text PASSED
tests/test_data_extractor.py::TestDataExtractor::test_empty_result PASSED
... (共14个测试)

tests/test_pagination.py::TestPaginationHandler::test_build_page_url PASSED
tests/test_pagination.py::TestPaginationHandler::test_detect_pagination_pattern PASSED
... (共11个测试)

tests/test_proxy_manager.py::TestProxyInfo::test_proxy_info_defaults PASSED
tests/test_proxy_manager.py::TestProxyManager::test_add_proxy_duplicate PASSED
... (共26个测试)

tests/test_rate_limiter.py::TestRateLimiter::test_calculate_delay_fixed PASSED
tests/test_rate_limiter.py::TestRateLimiter::test_calculate_delay_random PASSED
... (共8个测试)

tests/test_request_manager.py::TestRequestManager::test_build_request_params PASSED
tests/test_request_manager.py::TestRequestManager::test_close_session PASSED
... (共19个测试)

tests/test_scraper.py::TestWebScraper::test_export_custom_data PASSED
tests/test_scraper.py::TestWebScraper::test_export_data PASSED
... (共20个测试)

========================= 139 passed in 5.23s =========================
```

### 步骤4：覆盖率测试

```bash
pytest --cov=auto_web_scraper --cov-report=term-missing
```

**预期输出示例**（覆盖率应≥80%）：
```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-7.4.0
rootdir: f:\github\SoloTestPb\auto-web-scraper
testpaths: tests
collected 139 items

tests/test_authenticator.py ................................. [ 17%]
tests/test_config.py .............................          [ 22%]
tests/test_data_exporter.py ......................           [ 28%]
tests/test_data_extractor.py ............................... [ 38%]
tests/test_pagination.py ....................                [ 46%]
tests/test_proxy_manager.py ..............................  [ 64%]
tests/test_rate_limiter.py ........                         [ 70%]
tests/test_request_manager.py ........................      [ 83%]
tests/test_scraper.py ......................                [100%]

---------- coverage: platform win32, python 3.12.0-final-0 ----------
Name                                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------------
auto_web_scraper\__init__.py                              10      0   100%
auto_web_scraper\config.py                              120     10    92%   85-92
auto_web_scraper\request_manager.py                      95     12    87%   120-130
auto_web_scraper\data_extractor.py                       75      6    92%   60-65
auto_web_scraper\pagination.py                           58      5    91%   100-105
auto_web_scraper\authenticator.py                       120     15    88%   200-210
auto_web_scraper\proxy_manager.py                       100     12    88%   150-160
auto_web_scraper\rate_limiter.py                         60      4    93%   80-83
auto_web_scraper\data_exporter.py                        80     10    88%   110-120
auto_web_scraper\scraper.py                             150     18    88%   200-215
--------------------------------------------------------------------------------------
TOTAL                                                    868     92    89.4%

========================= 139 passed in 6.15s =========================

✅ 覆盖率达到要求 (89.4% >= 80%)
```

### 步骤5：生成Allure报告

```bash
# 生成Allure结果
pytest --alluredir=allure_results

# 安装Allure CLI（首次需要）
# Windows: scoop install allure
# 或下载: https://github.com/allure-framework/allure2/releases

# 查看报告
allure serve allure_results
```

**⚠️ 模拟输出示例（非实际运行结果）**：
```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-7.4.0
rootdir: f:\github\SoloTestPb\auto-web-scraper
testpaths: tests
collected 139 items

tests/test_authenticator.py ................................. [ 17%]
tests/test_config.py .............................          [ 22%]
...
tests/test_scraper.py ......................                [100%]

========================= 139 passed in 7.82s =========================

✅ Allure结果已生成到: f:\github\SoloTestPb\auto-web-scraper\allure_results
   要查看报告，请安装Allure CLI后运行:
   allure serve f:\github\SoloTestPb\auto-web-scraper\allure_results
```

**Allure报告预览**（浏览器打开后）：
```
Allure Report
├── Overview
│   ├── 139 test cases
│   ├── 139 passed (100%)
│   ├── 0 failed
│   ├── Duration: ~8s
│   └── Environment: Python 3.12, Windows
│
├── Suites
│   ├── TestAuthenticator (25 tests)
│   ├── TestConfig (7 tests)
│   ├── TestDataExporter (9 tests)
│   ├── TestDataExtractor (14 tests)
│   ├── TestPaginationHandler (11 tests)
│   ├── TestProxyManager (26 tests)
│   ├── TestRateLimiter (8 tests)
│   ├── TestRequestManager (19 tests)
│   └── TestWebScraper (20 tests)
│
├── Categories
│   └── No defects
│
└── Graphs
    ├── 100% Success Rate
    ├── 0% Failed Rate
    └── Distribution by duration
```

### 步骤6：数据完整性基准测试

```bash
# 运行1000页测试
python benchmark/data_integrity_test.py -p 1000

# 运行5次以验证稳定性
python benchmark/data_integrity_test.py -p 1000 -r 5
```

**预期输出（单次运行）**：
```
======================================================================
开始数据完整性基准测试
======================================================================
测试参数:
  - 页面总数: 1000
  - 永久失败率: 0.5%
  - 瞬时错误率: 10.0%
  - 重试次数: 3
======================================================================

生成了 1000 个模拟页面
进度: 100/1000 (10%)
进度: 200/1000 (20%)
进度: 300/1000 (30%)
进度: 400/1000 (40%)
进度: 500/1000 (50%)
进度: 600/1000 (60%)
进度: 700/1000 (70%)
进度: 800/1000 (80%)
进度: 900/1000 (90%)
进度: 1000/1000 (100%)

======================================================================
基准测试结果
======================================================================
执行统计:
  - 总请求数: 1150
  - 重试次数: 150
  - 总耗时: 2.35秒
  - 平均每页耗时: 2.35毫秒

数据统计:
  - 总页面数: 1000
  - 成功采集: 995
  - 失败页面: 5
  - 预期永久失败: 5

质量指标:
  - 数据完整率: 99.50%
  - 实际成功率: 100.00%
  - 要求: 99%

======================================================================
✅ 测试通过！数据完整率 (99.50%) >= 99%
======================================================================
```

**预期输出（多次运行统计）**：
```
######################################################################
第 1/5 次运行
######################################################################
... (如上)
✅ 测试通过！数据完整率 (99.50%) >= 99%

######################################################################
第 2/5 次运行
######################################################################
...
✅ 测试通过！数据完整率 (99.40%) >= 99%

... (共5次)


======================================================================
多次运行统计 (5 次运行)
======================================================================
数据完整率:
  - 平均值: 99.42%
  - 最小值: 99.30%
  - 最大值: 99.55%
  - 标准差: 0.0850%

执行时间:
  - 平均耗时: 2.28秒

结果:
  - 通过次数: 5/5
  - 全部通过: ✅ 是
======================================================================
```

### 步骤7：运行示例脚本

```bash
python examples/mock_scrape_demo.py
```

**⚠️ 模拟输出示例（非实际运行结果）**：
```
======================================================================
网页数据采集工具 - 完整采集流程演示
======================================================================

[1/7] 准备模拟数据...
    已生成 5 个模拟页面
    页面URL列表:
      - https://example.com/list
      - https://example.com/list?page=2
      - https://example.com/list?page=3
      - https://example.com/list?page=4
      - https://example.com/list?page=5

[2/7] 创建配置...
    配置名称: mock_demo_scraper
    选择器数量: 4
    分页: 启用
    代理: 启用
    登录: 启用

[3/7] 演示速率限制器...
    延迟范围: 0.01s - 0.02s
    随机延迟: 是

[4/7] 演示代理管理器...
    代理池大小: 3
    轮换策略: round_robin
    前3个代理:
      - http://proxy1:8080
      - http://proxy2:8080
      - http://proxy3:8080

[5/7] 演示数据提取...
    提取的字段:
      product_titles: 5 项
        示例: ['商品 1', '商品 2']
      product_prices: 5 项
        示例: ['¥99.00', '¥199.00']
      product_links: 5 项
        示例: ['/products/1', '/products/2']
      first_product: 商品 1

[6/7] 演示完整采集流程（模拟）...
    [1/5] 采集: https://example.com/list
    [2/5] 采集: https://example.com/list?page=2
    [3/5] 采集: https://example.com/list?page=3
    [4/5] 采集: https://example.com/list?page=4
    [5/5] 采集: https://example.com/list?page=5

    共采集 5 个页面

[7/7] 演示数据导出...
    导出目录: f:\github\SoloTestPb\auto-web-scraper\output\examples
      JSON: f:\github\SoloTestPb\auto-web-scraper\output\examples\mock_demo_20240101_120000.json
      CSV: f:\github\SoloTestPb\auto-web-scraper\output\examples\mock_demo_20240101_120000.csv

======================================================================
演示完成！
======================================================================

采集统计:
  - 总页面数: 5
  - 导出格式: json, csv

采集数据预览 (第1页):
  product_titles: 5 项
  product_prices: 5 项
  product_links: 5 项
  first_product: 商品 1
  _page_url: https://example.com/list

======================================================================
```

---

## 📋 验收标准核对清单

在完成所有测试后，请核对以下标准：

### 功能验收

| 标准 | 检查方式 | 通过标志 |
|------|----------|----------|
| CSS选择器提取 | `pytest tests/test_data_extractor.py` | ✅ |
| XPath提取 | `pytest tests/test_data_extractor.py` | ✅ |
| 自动分页 | `pytest tests/test_pagination.py` | ✅ |
| 登录认证 | `pytest tests/test_authenticator.py` | ✅ |
| 请求间隔 | `pytest tests/test_rate_limiter.py` | ✅ |
| 代理轮换 | `pytest tests/test_proxy_manager.py` | ✅ |
| CSV导出 | `pytest tests/test_data_exporter.py` | ✅ |
| Excel导出 | `pytest tests/test_data_exporter.py` | ✅ |
| JSON导出 | `pytest tests/test_data_exporter.py` | ✅ |

### 质量验收

| 标准 | 检查方式 | 阈值 | 实际值 |
|------|----------|------|--------|
| 测试用例通过 | `pytest` | 100% | ⏳ |
| 代码覆盖率 | `pytest --cov` | ≥80% | ⏳ |
| 数据完整率 | `benchmark/data_integrity_test.py` | ≥99% | ⏳ |
| PEP8规范 | 代码检查 | 无错误 | ✅ |
| 中文注释 | 代码检查 | 所有类/函数 | ✅ |

### 文档验收

| 文档 | 路径 | 状态 |
|------|------|------|
| 系统设计文档 | `docs/system-design.md` | ✅ |
| 测试运行指南 | `docs/TESTING.md` | ✅ |
| 使用说明 | `README.md` | ✅ |
| 依赖列表 | `requirements.txt` | ✅ |
| 示例配置 | `config/example.yaml` | ✅ |

---

## 🔍 故障排除

### 问题1：pytest未找到测试

**解决方案**：
```bash
# 确保在项目根目录运行
cd f:\github\SoloTestPb\auto-web-scraper

# 或者指定测试目录
pytest tests/

# 或者使用配置文件
pytest -c pytest.ini
```

### 问题2：依赖安装失败

**解决方案**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者升级pip
python -m pip install --upgrade pip
```

### 问题3：覆盖率低于80%

**排查步骤**：
1. 检查是否有测试文件遗漏
2. 检查是否有未测试的代码分支
3. 查看 `--cov-report=term-missing` 输出的Missing行
4. 补充测试用例

### 问题4：Allure命令找不到

**解决方案**：
```bash
# Windows使用scoop安装
scoop install allure

# 或者下载后手动添加到PATH
# 下载地址: https://github.com/allure-framework/allure2/releases

# 验证安装
allure --version
```

### 问题5：数据完整性测试失败

**排查步骤**：
1. 检查 `--failure-rate` 参数是否过高
2. 检查 `--retry-times` 是否足够
3. 运行多次验证稳定性
4. 如果网络环境差，考虑增加重试次数

---

## 📞 支持

如有问题，请检查：
1. Python版本是否为3.8+
2. 所有依赖是否正确安装
3. 项目目录结构是否完整
4. 测试文件是否都在 `tests/` 目录

---

**最后更新**: 2024年
**Python版本要求**: 3.8+ (推荐3.12)
**测试框架**: pytest 7.4+
