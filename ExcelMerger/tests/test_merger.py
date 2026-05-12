import pytest
import pandas as pd
import os
import tempfile
from excel_merger.merger import ExcelMerger


class TestExcelMerger:
    """测试ExcelMerger类"""

    @pytest.fixture
    def merger(self):
        """创建ExcelMerger实例"""
        return ExcelMerger()

    @pytest.fixture
    def temp_csv_files(self):
        """创建多个临时CSV文件用于按行合并测试"""
        temp_files = []

        for i in range(3):
            df = pd.DataFrame({
                'id': [i * 3 + 1, i * 3 + 2, i * 3 + 3],
                'name': [f'Person{i*3+1}', f'Person{i*3+2}', f'Person{i*3+3}'],
                'age': [20 + i * 5, 25 + i * 5, 30 + i * 5]
            })
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
                df.to_csv(f.name, index=False)
                temp_files.append(f.name)

        yield temp_files

        for f in temp_files:
            try:
                os.unlink(f)
            except:
                pass

    @pytest.fixture
    def temp_csv_files_for_join(self):
        """创建多个临时CSV文件用于关联合并测试"""
        temp_files = []

        df1 = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            df1.to_csv(f.name, index=False)
            temp_files.append(f.name)

        df2 = pd.DataFrame({
            'id': [1, 2, 3],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Paris']
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            df2.to_csv(f.name, index=False)
            temp_files.append(f.name)

        df3 = pd.DataFrame({
            'id': [1, 2, 3],
            'score': [85, 90, 95],
            'grade': ['A', 'A', 'A']
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            df3.to_csv(f.name, index=False)
            temp_files.append(f.name)

        yield temp_files

        for f in temp_files:
            try:
                os.unlink(f)
            except:
                pass

    def test_merge_by_row(self, merger, temp_csv_files):
        """测试按行合并"""
        result, stats = merger.merge_by_row(temp_csv_files)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 9
        assert stats['strategy'] == 'row_merge'
        assert stats['files_processed'] == 3
        assert stats['merged_rows'] == 9

    def test_merge_by_row_without_duplicates(self, merger, temp_csv_files):
        """测试按行合并不去重"""
        result, stats = merger.merge_by_row(temp_csv_files, remove_duplicates=False)
        assert len(result) == 9

    def test_merge_by_column(self, merger, temp_csv_files):
        """测试按列合并"""
        result, stats = merger.merge_by_column(temp_csv_files)
        assert isinstance(result, pd.DataFrame)
        assert stats['strategy'] == 'column_merge'
        assert stats['files_processed'] == 3
        assert len(result.columns) > 3

    def test_merge_by_join_inner(self, merger, temp_csv_files_for_join):
        """测试内关联合并"""
        result, stats = merger.merge_by_join(temp_csv_files_for_join, join_key='id', how='inner')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'name' in result.columns
        assert 'age' in result.columns
        assert 'score' in result.columns
        assert stats['strategy'] == 'join_merge'
        assert stats['join_key'] == 'id'

    def test_merge_by_join_left(self, merger, temp_csv_files_for_join):
        """测试左关联合并"""
        result, stats = merger.merge_by_join(temp_csv_files_for_join, join_key='id', how='left')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_merge_by_join_outer(self, merger, temp_csv_files_for_join):
        """测试外关联合并"""
        result, stats = merger.merge_by_join(temp_csv_files_for_join, join_key='id', how='outer')
        assert isinstance(result, pd.DataFrame)

    def test_merge_unified_interface_row(self, merger, temp_csv_files):
        """测试统一合并接口 - 按行"""
        result, stats = merger.merge(temp_csv_files, strategy='row')
        assert isinstance(result, pd.DataFrame)
        assert stats['strategy'] == 'row_merge'

    def test_merge_unified_interface_column(self, merger, temp_csv_files):
        """测试统一合并接口 - 按列"""
        result, stats = merger.merge(temp_csv_files, strategy='column')
        assert isinstance(result, pd.DataFrame)
        assert stats['strategy'] == 'column_merge'

    def test_merge_unified_interface_join(self, merger, temp_csv_files_for_join):
        """测试统一合并接口 - 关联"""
        result, stats = merger.merge(temp_csv_files_for_join, strategy='join', join_key='id')
        assert isinstance(result, pd.DataFrame)
        assert stats['strategy'] == 'join_merge'

    def test_merge_unsupported_strategy(self, merger, temp_csv_files):
        """测试不支持的合并策略"""
        with pytest.raises(ValueError):
            merger.merge(temp_csv_files, strategy='unsupported')

    def test_merge_no_files(self, merger):
        """测试没有文件的情况"""
        with pytest.raises(ValueError):
            merger.merge_by_row([])

    def test_save_result_csv(self, merger, temp_csv_files):
        """测试保存结果为CSV"""
        result, _ = merger.merge_by_row(temp_csv_files)
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            merger.save_result(result, output_path)
            assert os.path.exists(output_path)
            df_read = pd.read_csv(output_path)
            assert len(df_read) == len(result)
        finally:
            os.unlink(output_path)

    def test_save_result_excel(self, merger, temp_csv_files):
        """测试保存结果为Excel"""
        result, _ = merger.merge_by_row(temp_csv_files)
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            output_path = f.name
        try:
            merger.save_result(result, output_path)
            assert os.path.exists(output_path)
            df_read = pd.read_excel(output_path, engine='openpyxl')
            assert len(df_read) == len(result)
        finally:
            os.unlink(output_path)

    def test_save_result_unsupported_format(self, merger, temp_csv_files):
        """测试保存不支持的格式"""
        result, _ = merger.merge_by_row(temp_csv_files)
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = f.name
        try:
            with pytest.raises(ValueError):
                merger.save_result(result, output_path)
        finally:
            os.unlink(output_path)

    def test_get_merge_stats(self, merger, temp_csv_files):
        """测试获取合并统计"""
        merger.merge_by_row(temp_csv_files)
        stats = merger.get_merge_stats()
        assert isinstance(stats, dict)
        assert 'strategy' in stats
        assert 'merged_rows' in stats
