"""
pytest配置和fixture。
"""

import os
import tempfile
from typing import List

import pandas as pd
import pytest


@pytest.fixture
def sample_dataframe():
    """
    提供示例DataFrame用于测试。
    """
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["张三", "李四", "王五", "赵六", "钱七"],
            "age": [25, 30, 28, 35, 22],
            "salary": [5000, 6000, 5500, 7000, 4500],
            "department": ["技术部", "市场部", "技术部", "销售部", "市场部"],
        }
    )


@pytest.fixture
def large_dataframe():
    """
    提供大型DataFrame用于性能测试（10万行）。
    """
    import random
    import string

    def random_name():
        return "".join(random.choices(string.ascii_letters, k=8))

    def random_department():
        return random.choice(["技术部", "市场部", "销售部", "财务部", "人事部"])

    n = 100000
    return pd.DataFrame(
        {
            "id": range(1, n + 1),
            "name": [random_name() for _ in range(n)],
            "age": [random.randint(20, 60) for _ in range(n)],
            "salary": [random.randint(3000, 20000) for _ in range(n)],
            "department": [random_department() for _ in range(n)],
        }
    )


@pytest.fixture
def temp_dir():
    """
    提供临时目录用于测试文件输出。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_csv_file(temp_dir, sample_dataframe):
    """
    创建示例CSV文件。
    """
    file_path = os.path.join(temp_dir, "sample.csv")
    sample_dataframe.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sample_excel_file(temp_dir, sample_dataframe):
    """
    创建示例Excel文件。
    """
    file_path = os.path.join(temp_dir, "sample.xlsx")
    sample_dataframe.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def sample_json_file(temp_dir, sample_dataframe):
    """
    创建示例JSON文件。
    """
    file_path = os.path.join(temp_dir, "sample.json")
    sample_dataframe.to_json(file_path, orient="records", force_ascii=False)
    return file_path


@pytest.fixture
def sample_sqlite_file(temp_dir, sample_dataframe):
    """
    创建示例SQLite数据库文件。
    """
    from sqlalchemy import create_engine

    db_path = os.path.join(temp_dir, "sample.db")
    engine = create_engine(f"sqlite:///{db_path}")
    sample_dataframe.to_sql("employees", engine, index=False)
    engine.dispose()
    return db_path
