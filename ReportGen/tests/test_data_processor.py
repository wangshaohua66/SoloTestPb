"""
数据处理模块单元测试。
"""

import pytest
import pandas as pd

from reportgen.data import DataProcessor


class TestDataProcessor:
    """
    DataProcessor类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        processor = DataProcessor()
        assert processor is not None

    def test_filter_data(self, sample_dataframe):
        """
        测试数据筛选。
        """
        processor = DataProcessor()

        conditions = {"department": "技术部"}
        result = processor.filter_data(sample_dataframe, conditions)

        assert len(result) == 2
        assert all(result["department"] == "技术部")

    def test_filter_data_with_range(self, sample_dataframe):
        """
        测试使用范围条件筛选数据。
        """
        processor = DataProcessor()

        conditions = {"age": {"min": 25, "max": 30}}
        result = processor.filter_data(sample_dataframe, conditions)

        assert len(result) == 3
        assert all(result["age"].between(25, 30))

    def test_filter_data_with_in_list(self, sample_dataframe):
        """
        测试使用in条件筛选数据。
        """
        processor = DataProcessor()

        conditions = {"department": {"in": ["技术部", "市场部"]}}
        result = processor.filter_data(sample_dataframe, conditions)

        assert len(result) == 4

    def test_filter_data_invalid_column(self, sample_dataframe):
        """
        测试筛选不存在的列时抛出异常。
        """
        processor = DataProcessor()

        conditions = {"non_existent_column": "value"}

        with pytest.raises(ValueError, match="列不存在"):
            processor.filter_data(sample_dataframe, conditions)

    def test_filter_data_empty_dataframe(self):
        """
        测试筛选空DataFrame。
        """
        processor = DataProcessor()
        empty_df = pd.DataFrame()
        result = processor.filter_data(empty_df, {"col": "value"})

        assert result.empty

    def test_sort_data(self, sample_dataframe):
        """
        测试数据排序。
        """
        processor = DataProcessor()

        result = processor.sort_data(sample_dataframe, "age")

        assert result.iloc[0]["age"] == 22
        assert result.iloc[-1]["age"] == 35

    def test_sort_data_descending(self, sample_dataframe):
        """
        测试降序排序。
        """
        processor = DataProcessor()

        result = processor.sort_data(sample_dataframe, "salary", ascending=False)

        assert result.iloc[0]["salary"] == 7000
        assert result.iloc[-1]["salary"] == 4500

    def test_sort_data_empty_dataframe(self):
        """
        测试排序空DataFrame。
        """
        processor = DataProcessor()
        empty_df = pd.DataFrame()
        result = processor.sort_data(empty_df, "col")

        assert result.empty

    def test_aggregate_data(self, sample_dataframe):
        """
        测试数据聚合。
        """
        processor = DataProcessor()

        result = processor.aggregate_data(
            sample_dataframe,
            group_by="department",
            aggregations={"salary": "mean", "age": "count"},
        )

        assert len(result) == 3
        assert "department" in result.columns
        assert "salary" in result.columns
        assert "age" in result.columns

    def test_aggregate_data_empty_dataframe(self):
        """
        测试聚合空DataFrame。
        """
        processor = DataProcessor()
        empty_df = pd.DataFrame()
        result = processor.aggregate_data(empty_df, "col", {})

        assert result.empty

    def test_select_columns(self, sample_dataframe):
        """
        测试选择列。
        """
        processor = DataProcessor()

        result = processor.select_columns(sample_dataframe, ["name", "salary"])

        assert list(result.columns) == ["name", "salary"]

    def test_rename_columns(self, sample_dataframe):
        """
        测试重命名列。
        """
        processor = DataProcessor()

        result = processor.rename_columns(
            sample_dataframe,
            {"name": "姓名", "salary": "薪资"},
        )

        assert "姓名" in result.columns
        assert "薪资" in result.columns

    def test_drop_duplicates(self, sample_dataframe):
        """
        测试去重。
        """
        processor = DataProcessor()

        df_with_duplicates = pd.concat([sample_dataframe, sample_dataframe.iloc[0:1]])
        result = processor.drop_duplicates(df_with_duplicates)

        assert len(result) == 5

    def test_handle_missing_values_drop(self):
        """
        测试删除缺失值。
        """
        processor = DataProcessor()

        df_with_missing = pd.DataFrame(
            {
                "col1": [1, 2, None, 4],
                "col2": ["a", "b", "c", "d"],
            }
        )

        result = processor.handle_missing_values(df_with_missing, strategy="drop")

        assert len(result) == 3

    def test_handle_missing_values_fill(self):
        """
        测试填充缺失值。
        """
        processor = DataProcessor()

        df_with_missing = pd.DataFrame(
            {
                "col1": [1, 2, None, 4],
                "col2": ["a", "b", "c", "d"],
            }
        )

        result = processor.handle_missing_values(
            df_with_missing,
            strategy="fill",
            fill_value=0,
        )

        assert len(result) == 4
        assert result["col1"].isnull().sum() == 0

    def test_handle_missing_values_invalid_strategy(self, sample_dataframe):
        """
        测试无效的缺失值处理策略。
        """
        processor = DataProcessor()

        with pytest.raises(ValueError, match="不支持的缺失值处理策略"):
            processor.handle_missing_values(sample_dataframe, strategy="invalid")

    def test_process_data_multiple_operations(self, sample_dataframe):
        """
        测试执行多个处理操作。
        """
        processor = DataProcessor()

        operations = [
            {
                "type": "filter",
                "params": {"conditions": {"age": {"min": 25}}},
            },
            {
                "type": "sort",
                "params": {"sort_by": "salary", "ascending": False},
            },
        ]

        result = processor.process_data(sample_dataframe, operations)

        assert len(result) == 4
        assert result.iloc[0]["salary"] == 7000

    def test_process_data_aggregate_operation(self, sample_dataframe):
        """
        测试聚合操作。
        """
        processor = DataProcessor()

        operations = [
            {
                "type": "aggregate",
                "params": {
                    "group_by": "department",
                    "aggregations": {"salary": "sum"},
                },
            }
        ]

        result = processor.process_data(sample_dataframe, operations)

        assert len(result) == 3

    def test_process_data_invalid_operation(self, sample_dataframe):
        """
        测试无效的操作类型。
        """
        processor = DataProcessor()

        operations = [{"type": "invalid_operation"}]

        with pytest.raises(ValueError, match="不支持的数据处理操作"):
            processor.process_data(sample_dataframe, operations)
