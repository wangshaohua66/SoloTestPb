# 自动化报表生成工具

一个功能强大的自动化报表生成工具，支持从多种数据源读取数据、灵活的数据处理、自定义模板和多种输出格式。

## 功能特性

- **多数据源支持**：支持从CSV、Excel、JSON文件以及MySQL、SQLite数据库读取数据
- **数据处理**：支持数据筛选、排序、聚合、去重、缺失值处理等操作
- **模板引擎**：基于Jinja2的模板引擎，支持自定义报表格式
- **多格式输出**：支持生成Excel、HTML、PDF格式报表
- **定时任务**：支持定时自动生成并发送报表
- **邮件发送**：支持通过邮件发送生成的报表
- **高性能**：处理10万行数据生成报表耗时不超过30秒

## 技术栈

- **编程语言**：Python 3.12
- **数据处理**：pandas, openpyxl
- **模板引擎**：Jinja2
- **PDF生成**：WeasyPrint
- **数据库**：SQLAlchemy, pymysql
- **定时任务**：schedule
- **测试框架**：pytest + Allure

## 安装

```bash
# 克隆项目
git clone <repository-url>
cd ReportGen

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 使用Python API

```python
from reportgen.core import ReportGenerator

# 创建报表生成器
generator = ReportGenerator()

# 方式一：从DataFrame直接生成
import pandas as pd
df = pd.DataFrame({
    "name": ["张三", "李四", "王五"],
    "salary": [5000, 6000, 5500],
})

# 生成Excel报表
generator.generate_report_from_dataframe(
    df,
    output_format="excel",
    output_path="output/report.xlsx",
    title="员工薪资报表"
)

# 生成HTML报表
generator.generate_report_from_dataframe(
    df,
    output_format="html",
    output_path="output/report.html",
    title="员工薪资报表"
)
```

### 2. 使用配置文件

创建配置文件 `report_config.json`：

```json
{
    "source": {
        "type": "csv",
        "params": {
            "file_path": "data/employees.csv"
        }
    },
    "processing": {
        "operations": [
            {
                "type": "filter",
                "params": {
                    "conditions": {
                        "salary": {"min": 5000}
                    }
                }
            },
            {
                "type": "sort",
                "params": {
                    "sort_by": "salary",
                    "ascending": false
                }
            }
        ]
    },
    "output": {
        "format": "excel",
        "path": "output/employee_report.xlsx",
        "title": "高薪资员工报表"
    }
}
```

然后使用命令行运行：

```bash
python -m reportgen.main generate -c report_config.json
```

### 3. 使用Jinja2模板

创建模板文件 `templates/report.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ report_title }}</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #4472C4; color: white; }
        .total { font-weight: bold; color: #2E7D32; }
    </style>
</head>
<body>
    <h1>{{ report_title }}</h1>
    <p>生成时间: {{ report_date }}</p>
    
    <h3>数据摘要</h3>
    <p>总人数: {{ total_count }}</p>
    <p class="total">平均薪资: {{ avg_salary | format_currency }}</p>
    
    <h3>详细数据</h3>
    <table>
        <thead>
            <tr>
                {% for col in columns %}
                <th>{{ col }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in data %}
            <tr>
                {% for col in columns %}
                <td>{{ row[col] }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
```

然后使用模板生成报表：

```python
from reportgen.core import ReportGenerator

generator = ReportGenerator(template_dir="templates")

config = {
    "source": {
        "type": "csv",
        "params": {"file_path": "data/employees.csv"}
    },
    "output": {
        "format": "html",
        "path": "output/report.html",
        "title": "员工报表"
    },
    "template": {
        "use_template": true,
        "template_path": "report.html",
        "context": {
            "report_title": "2024年员工薪资报表",
            "report_date": "2024-01-01",
            "total_count": 100,
            "avg_salary": 8500.50
        }
    }
}

result = generator.generate_report(config)
```

### 4. 定时任务

```python
from reportgen.scheduler import ReportScheduler
from reportgen.core import ReportGenerator

scheduler = ReportScheduler()
generator = ReportGenerator()

def generate_daily_report():
    """
    生成每日报表的任务。
    """
    config = {
        "source": {
            "type": "csv",
            "params": {"file_path": "data/daily_data.csv"}
        },
        "output": {
            "format": "excel",
            "path": "output/daily_report.xlsx"
        }
    }
    result = generator.generate_report(config)
    print(f"报表生成完成: {result['output_path']}")

# 添加每日定时任务（每天早上9点执行）
scheduler.add_daily_job("09:00", generate_daily_report)

# 添加每小时任务
scheduler.add_hourly_job(1, generate_daily_report)

# 启动调度器
scheduler.start()
```

### 5. 发送邮件

```python
from reportgen.scheduler import ReportScheduler

scheduler = ReportScheduler()

email_config = {
    "smtp_host": "smtp.example.com",
    "smtp_port": 465,
    "sender": "report@example.com",
    "password": "your_password",
    "recipients": ["user1@example.com", "user2@example.com"],
    "use_ssl": True
}

# 发送带附件的报表邮件
scheduler.send_report_email(
    email_config=email_config,
    report_path="output/report.xlsx",
    report_name="月度销售报表"
)
```

## 数据处理操作

### 筛选数据
```json
{
    "type": "filter",
    "params": {
        "conditions": {
            "age": {"min": 25, "max": 35},
            "department": {"in": ["技术部", "市场部"]},
            "name": {"contains": "张"}
        }
    }
}
```

### 排序数据
```json
{
    "type": "sort",
    "params": {
        "sort_by": ["salary", "age"],
        "ascending": [false, true]
    }
}
```

### 聚合数据
```json
{
    "type": "aggregate",
    "params": {
        "group_by": "department",
        "aggregations": {
            "salary": "mean",
            "age": "count"
        }
    }
}
```

### 选择列
```json
{
    "type": "select_columns",
    "params": {
        "columns": ["name", "salary", "department"]
    }
}
```

### 重命名列
```json
{
    "type": "rename_columns",
    "params": {
        "column_mapping": {
            "name": "姓名",
            "salary": "薪资"
        }
    }
}
```

### 去重
```json
{
    "type": "drop_duplicates",
    "params": {
        "subset": ["name", "id"],
        "keep": "first"
    }
}
```

### 处理缺失值
```json
{
    "type": "handle_missing",
    "params": {
        "strategy": "fill",
        "fill_value": 0
    }
}
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=reportgen --cov-report=html

# 运行测试并生成Allure报告
pytest --alluredir=allure_results
allure serve allure_results
```

## 项目结构

```
ReportGen/
├── reportgen/                    # 主包
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # 命令行入口
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   └── generator.py         # 报表生成器
│   ├── data/                    # 数据模块
│   │   ├── __init__.py
│   │   ├── reader.py            # 数据读取
│   │   └── processor.py         # 数据处理
│   ├── output/                  # 输出模块
│   │   ├── __init__.py
│   │   ├── excel_output.py      # Excel输出
│   │   ├── html_output.py       # HTML输出
│   │   └── pdf_output.py        # PDF输出
│   ├── templates/               # 模板模块
│   │   ├── __init__.py
│   │   └── engine.py            # 模板引擎
│   └── scheduler/               # 调度器模块
│       ├── __init__.py
│       └── scheduler.py         # 定时任务和邮件
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── conftest.py              # pytest配置
│   ├── test_data_reader.py      # 数据读取测试
│   ├── test_data_processor.py   # 数据处理测试
│   ├── test_template_engine.py  # 模板引擎测试
│   ├── test_output.py           # 输出模块测试
│   └── test_report_generator.py # 报表生成器测试
├── requirements.txt             # 依赖列表
├── pytest.ini                   # pytest配置
└── README.md                    # 项目文档
```

## 数据源配置示例

### CSV文件
```json
{
    "type": "csv",
    "params": {
        "file_path": "data/data.csv",
        "encoding": "utf-8",
        "sep": ","
    }
}
```

### Excel文件
```json
{
    "type": "excel",
    "params": {
        "file_path": "data/data.xlsx",
        "sheet_name": "Sheet1"
    }
}
```

### JSON文件
```json
{
    "type": "json",
    "params": {
        "file_path": "data/data.json",
        "encoding": "utf-8"
    }
}
```

### MySQL数据库
```json
{
    "type": "mysql",
    "params": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "password",
        "database": "mydb",
        "query": "SELECT * FROM employees"
    }
}
```

### SQLite数据库
```json
{
    "type": "sqlite",
    "params": {
        "db_path": "data/mydb.db",
        "query": "SELECT * FROM employees"
    }
}
```

## 许可证

MIT License
