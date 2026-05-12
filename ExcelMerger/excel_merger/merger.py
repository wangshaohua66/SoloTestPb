import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .reader import ExcelReader
from .cleaner import DataCleaner


class ExcelMerger:
    """Excel合并类，提供三种合并策略：按行、按列、关联合并"""

    def __init__(self):
        """初始化ExcelMerger"""
        self.reader = ExcelReader()
        self.cleaner = DataCleaner()
        self.merge_stats = {}

    def merge_by_row(self, file_paths: List[str], sheet_name: Optional[str] = None, remove_duplicates: bool = True, duplicate_subset: Optional[List[str]] = None, handle_missing: bool = True, missing_strategy: str = 'fill', missing_fill_value: Any = '') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        按行合并（追加数据）

        Args:
            file_paths: 文件路径列表
            sheet_name: 工作表名称
            remove_duplicates: 是否去重
            duplicate_subset: 去重时使用的列
            handle_missing: 是否处理缺失值
            missing_strategy: 缺失值处理策略
            missing_fill_value: 缺失值填充值

        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: 合并后的DataFrame和统计信息
        """
        # 初始化合并统计信息
        self.merge_stats = {
            'strategy': 'row_merge',
            'files_processed': 0,
            'files_failed': 0,
            'original_rows': 0,
            'merged_rows': 0,
            'file_details': []
        }

        # 存储所有成功读取的DataFrame
        dfs = []
        # 循环遍历每个文件路径
        for file_path in file_paths:
            try:
                # 读取单个文件数据
                df = self.reader.read_file(file_path, sheet_name=sheet_name)
                # 获取当前文件行数
                original_rows = len(df)
                # 累加原始总行数
                self.merge_stats['original_rows'] += original_rows
                # 增加已处理文件计数
                self.merge_stats['files_processed'] += 1

                # 将DataFrame添加到列表中待合并
                dfs.append(df)
                # 记录该文件的详细处理信息
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'rows': original_rows,
                    'columns': list(df.columns),
                    'status': 'success'
                })
            except Exception as e:
                # 处理失败时增加失败计数并记录错误信息
                self.merge_stats['files_failed'] += 1
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })
                # 输出警告信息但不中断整个合并流程
                print(f"警告: 处理文件 {file_path} 失败: {str(e)}")

        # 检查是否有成功读取的文件，如没有则抛出异常
        if not dfs:
            raise ValueError("没有成功读取任何文件")

        # 使用pandas.concat沿垂直方向（axis=0）合并所有DataFrame
        # ignore_index=True重置索引，避免重复的索引值
        result = pd.concat(dfs, axis=0, ignore_index=True)

        # 根据配置处理缺失值
        if handle_missing:
            result = self.cleaner.handle_missing_values(
                result, strategy=missing_strategy, fill_value=missing_fill_value
            )

        # 根据配置去除重复行
        if remove_duplicates:
            result = self.cleaner.remove_duplicates(result, subset=duplicate_subset)

        # 更新统计信息，加入清洗统计数据
        self.merge_stats.update(self.cleaner.get_cleaning_stats())
        # 记录合并后的行数和列名
        self.merge_stats['merged_rows'] = len(result)
        self.merge_stats['merged_columns'] = list(result.columns)

        # 返回合并结果和统计信息的副本（防止外部修改内部状态）
        return result, self.merge_stats.copy()

    def merge_by_column(self, file_paths: List[str], sheet_name: Optional[str] = None, axis: int = 1, join: str = 'outer') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        按列合并（合并字段）

        Args:
            file_paths: 文件路径列表
            sheet_name: 工作表名称
            axis: 合并轴，1为按列合并
            join: 连接方式，'inner'或'outer'

        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: 合并后的DataFrame和统计信息
        """
        # 初始化合并统计信息
        self.merge_stats = {
            'strategy': 'column_merge',
            'files_processed': 0,
            'files_failed': 0,
            'file_details': []
        }

        # 存储所有成功读取的DataFrame
        dfs = []
        # 循环遍历每个文件路径，同时记录索引
        for idx, file_path in enumerate(file_paths):
            try:
                # 读取单个文件数据
                df = self.reader.read_file(file_path, sheet_name=sheet_name)
                # 为除第一个文件外的所有列添加后缀，避免列名冲突
                # 第一个文件保持原列名，后续文件添加 _1, _2 等后缀
                df = df.add_suffix(f'_{idx}') if idx > 0 else df
                # 将DataFrame添加到列表中待合并
                dfs.append(df)
                # 增加已处理文件计数
                self.merge_stats['files_processed'] += 1
                # 记录该文件的详细处理信息
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'status': 'success'
                })
            except Exception as e:
                # 处理失败时增加失败计数并记录错误信息
                self.merge_stats['files_failed'] += 1
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })
                # 输出警告信息但不中断整个合并流程
                print(f"警告: 处理文件 {file_path} 失败: {str(e)}")

        # 检查是否有成功读取的文件，如没有则抛出异常
        if not dfs:
            raise ValueError("没有成功读取任何文件")

        # 使用pandas.concat沿水平方向（axis=1）合并所有DataFrame
        # join参数控制连接方式：inner取交集，outer取并集
        result = pd.concat(dfs, axis=axis, join=join)

        # 记录合并后的行数、列名和连接方式
        self.merge_stats['merged_rows'] = len(result)
        self.merge_stats['merged_columns'] = list(result.columns)
        self.merge_stats['merge_method'] = join

        # 返回合并结果和统计信息的副本
        return result, self.merge_stats.copy()

    def merge_by_join(self, file_paths: List[str], join_key: str, how: str = 'inner', sheet_name: Optional[str] = None, suffixes: Tuple[str, str] = ('_x', '_y')) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        按指定键值进行关联合并（类似SQL JOIN）

        Args:
            file_paths: 文件路径列表
            join_key: 连接键列名
            how: 连接方式：'inner', 'left', 'right', 'outer'
            sheet_name: 工作表名称
            suffixes: 列名冲突时的后缀

        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: 合并后的DataFrame和统计信息
        """
        # 初始化合并统计信息，记录关联键和连接类型
        self.merge_stats = {
            'strategy': 'join_merge',
            'join_key': join_key,
            'join_type': how,
            'files_processed': 0,
            'files_failed': 0,
            'file_details': []
        }

        # 存储所有成功读取的DataFrame
        dfs = []
        # 循环遍历每个文件路径
        for file_path in file_paths:
            try:
                # 读取单个文件数据
                df = self.reader.read_file(file_path, sheet_name=sheet_name)
                # 验证连接键列是否存在，不存在则抛出异常
                if join_key not in df.columns:
                    raise ValueError(f"文件中不存在连接键列: {join_key}")
                # 将DataFrame添加到列表中待合并
                dfs.append(df)
                # 增加已处理文件计数
                self.merge_stats['files_processed'] += 1
                # 记录该文件的详细处理信息
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'rows': len(df),
                    'columns': list(df.columns),
                    'status': 'success'
                })
            except Exception as e:
                # 处理失败时增加失败计数并记录错误信息
                self.merge_stats['files_failed'] += 1
                self.merge_stats['file_details'].append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })
                # 输出警告信息但不中断整个合并流程
                print(f"警告: 处理文件 {file_path} 失败: {str(e)}")

        # 检查是否有成功读取的文件，如没有则抛出异常
        if not dfs:
            raise ValueError("没有成功读取任何文件")

        # 如果只有一个文件，直接返回该文件数据
        if len(dfs) == 1:
            result = dfs[0]
        else:
            # 多个文件时，使用迭代方式逐步关联合并
            # 以第一个文件为左表，后续文件依次进行join操作
            result = dfs[0]
            for i in range(1, len(dfs)):
                # 根据是否提供suffixes参数决定使用默认后缀还是自定义后缀
                current_suffixes = (f'_{i-1}', f'_{i}') if suffixes is None else suffixes
                # 使用pandas.merge执行关联操作，类似SQL的JOIN操作
                result = pd.merge(
                    result, dfs[i],
                    on=join_key,          # 关联键列名
                    how=how,              # 连接类型（inner/left/right/outer）
                    suffixes=current_suffixes  # 列名冲突时的后缀
                )

        # 记录合并后的行数和列名
        self.merge_stats['merged_rows'] = len(result)
        self.merge_stats['merged_columns'] = list(result.columns)

        # 返回合并结果和统计信息的副本
        return result, self.merge_stats.copy()

    def merge(self, file_paths: List[str], strategy: str = 'row', **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        统一的合并接口

        Args:
            file_paths: 文件路径列表
            strategy: 合并策略：'row', 'column', 'join'
            **kwargs: 传递给具体合并方法的参数

        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: 合并后的DataFrame和统计信息

        Raises:
            ValueError: 不支持的合并策略
        """
        if strategy == 'row':
            return self.merge_by_row(file_paths, **kwargs)
        elif strategy == 'column':
            return self.merge_by_column(file_paths, **kwargs)
        elif strategy == 'join':
            return self.merge_by_join(file_paths, **kwargs)
        else:
            raise ValueError(f"不支持的合并策略: {strategy}。支持的策略: row, column, join")

    def save_result(self, df: pd.DataFrame, output_path: str, sheet_name: str = 'Sheet1', index: bool = False, **kwargs) -> None:
        """
        保存合并结果到文件

        Args:
            df: 要保存的DataFrame
            output_path: 输出文件路径
            sheet_name: 工作表名称（仅对Excel文件有效）
            index: 是否保存索引
            **kwargs: 传递给pandas写入函数的额外参数
        """
        import os
        ext = os.path.splitext(output_path)[1].lower()

        if ext == '.csv':
            df.to_csv(output_path, index=index, **kwargs)
        elif ext in ('.xlsx', '.xls'):
            engine = 'openpyxl' if ext == '.xlsx' else 'xlwt'
            df.to_excel(output_path, sheet_name=sheet_name, index=index, engine=engine, **kwargs)
        else:
            raise ValueError(f"不支持的输出格式: {ext}")

    def get_merge_stats(self) -> Dict[str, Any]:
        """
        获取合并统计信息

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        return self.merge_stats.copy()
