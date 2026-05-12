import pytest
import pandas as pd
import numpy as np
from excel_merger.cleaner import DataCleaner


class TestDataCleaner:
    """测试DataCleaner类"""

    @pytest.fixture
    def cleaner(self):
        """创建DataCleaner实例"""
        return DataCleaner()

    @pytest.fixture
    def sample_df_with_duplicates(self):
        """创建包含重复行的DataFrame"""
        return pd.DataFrame({
            'id': [1, 2, 2, 3, 3, 3],
            'name': ['Alice', 'Bob', 'Bob', 'Charlie', 'Charlie', 'Charlie'],
            'age': [25, 30, 30, 35, 35, 35]
        })

    @pytest.fixture
    def sample_df_with_missing(self):
        """创建包含缺失值的DataFrame"""
        return pd.DataFrame({
            'id': [1, 2, np.nan, 4, 5],
            'name': ['Alice', np.nan, 'Charlie', 'David', 'Eve'],
            'age': [25, np.nan, 35, np.nan, 45],
            'score': [85.5, 90.0, np.nan, 75.0, 80.0]
        })

    def test_remove_duplicates(self, cleaner, sample_df_with_duplicates):
        """测试去除重复行"""
        original_count = len(sample_df_with_duplicates)
        df_cleaned = cleaner.remove_duplicates(sample_df_with_duplicates)
        assert len(df_cleaned) == 3
        stats = cleaner.get_cleaning_stats()
        assert stats['duplicates_removed'] == original_count - 3

    def test_remove_duplicates_with_subset(self, cleaner, sample_df_with_duplicates):
        """测试按指定列去重"""
        df_cleaned = cleaner.remove_duplicates(sample_df_with_duplicates, subset=['id'])
        assert len(df_cleaned) == 3

    def test_handle_missing_fill(self, cleaner, sample_df_with_missing):
        """测试用指定值填充缺失值"""
        df_cleaned = cleaner.handle_missing_values(sample_df_with_missing, strategy='fill', fill_value='UNKNOWN')
        assert df_cleaned.isnull().sum().sum() == 0

    def test_handle_missing_drop(self, cleaner, sample_df_with_missing):
        """测试删除包含缺失值的行"""
        df_cleaned = cleaner.handle_missing_values(sample_df_with_missing, strategy='drop')
        assert len(df_cleaned) == 2

    def test_handle_missing_mean(self, cleaner, sample_df_with_missing):
        """测试用均值填充数值列"""
        df_cleaned = cleaner.handle_missing_values(sample_df_with_missing, strategy='mean')
        assert not pd.isnull(df_cleaned['age'][1])
        assert not pd.isnull(df_cleaned['score'][2])

    def test_handle_missing_median(self, cleaner, sample_df_with_missing):
        """测试用中位数填充数值列"""
        df_cleaned = cleaner.handle_missing_values(sample_df_with_missing, strategy='median')
        assert not pd.isnull(df_cleaned['age'][1])

    def test_handle_missing_mode(self, cleaner, sample_df_with_missing):
        """测试用众数填充"""
        df_cleaned = cleaner.handle_missing_values(sample_df_with_missing, strategy='mode')
        assert not pd.isnull(df_cleaned['name'][1])

    def test_unsupported_missing_strategy(self, cleaner, sample_df_with_missing):
        """测试不支持的缺失值处理策略"""
        with pytest.raises(ValueError):
            cleaner.handle_missing_values(sample_df_with_missing, strategy='unsupported')

    def test_drop_empty_rows(self, cleaner):
        """测试删除空行"""
        df = pd.DataFrame({
            'a': [1, np.nan, 3],
            'b': [2, np.nan, 4]
        })
        df_cleaned = cleaner.drop_empty_rows(df)
        assert len(df_cleaned) == 2

    def test_drop_empty_columns(self, cleaner):
        """测试删除空列"""
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [np.nan, np.nan, np.nan],
            'c': [4, 5, 6]
        })
        df_cleaned = cleaner.drop_empty_columns(df)
        assert 'b' not in df_cleaned.columns
        assert len(df_cleaned.columns) == 2

    def test_clean_data_combined(self, cleaner, sample_df_with_duplicates, sample_df_with_missing):
        """测试综合数据清洗"""
        df = pd.concat([sample_df_with_duplicates, sample_df_with_missing], ignore_index=True)
        df_cleaned = cleaner.clean_data(
            df,
            remove_duplicates=True,
            missing_strategy='fill',
            missing_fill_value=0
        )
        assert isinstance(df_cleaned, pd.DataFrame)
        stats = cleaner.get_cleaning_stats()
        assert 'duplicates_removed' in stats

    def test_get_cleaning_stats(self, cleaner, sample_df_with_duplicates):
        """测试获取清洗统计"""
        cleaner.remove_duplicates(sample_df_with_duplicates)
        stats = cleaner.get_cleaning_stats()
        assert isinstance(stats, dict)
        assert 'duplicates_removed' in stats

    def test_reset_stats(self, cleaner, sample_df_with_duplicates):
        """测试重置统计信息"""
        cleaner.remove_duplicates(sample_df_with_duplicates)
        stats1 = cleaner.get_cleaning_stats()
        assert stats1['duplicates_removed'] > 0

        cleaner.reset_stats()
        stats2 = cleaner.get_cleaning_stats()
        assert stats2 == {}
