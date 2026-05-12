import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union


class DataCleaner:
    """数据清洗类，提供去重、空值处理等功能"""

    def __init__(self):
        """初始化DataCleaner"""
        self.cleaning_stats = {}

    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
        """
        去除重复行

        Args:
            df: 输入DataFrame
            subset: 用于判断重复的列名列表，为None时使用所有列
            keep: 保留策略，'first'保留第一个，'last'保留最后一个，False删除所有重复

        Returns:
            pd.DataFrame: 去重后的DataFrame
        """
        # 记录原始行数用于统计去重数量
        original_count = len(df)
        # 使用pandas内置的drop_duplicates方法去重
        # subset参数指定判断重复的列，keep参数指定保留策略
        df_cleaned = df.drop_duplicates(subset=subset, keep=keep)
        # 计算被删除的重复行数
        removed_count = original_count - len(df_cleaned)

        # 更新清洗统计信息
        self.cleaning_stats['duplicates_removed'] = removed_count
        self.cleaning_stats['original_rows'] = original_count
        self.cleaning_stats['rows_after_dedup'] = len(df_cleaned)

        # 返回去重后的DataFrame
        return df_cleaned

    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'drop', fill_value: Any = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        处理缺失值

        Args:
            df: 输入DataFrame
            strategy: 处理策略
                - 'drop': 删除包含缺失值的行
                - 'drop_all': 删除全部为缺失值的行
                - 'fill': 用指定值填充
                - 'ffill': 用前一个值填充
                - 'bfill': 用后一个值填充
                - 'mean': 用均值填充（仅数值列）
                - 'median': 用中位数填充（仅数值列）
                - 'mode': 用众数填充
            fill_value: 当strategy为'fill'时使用的填充值
            columns: 指定要处理的列，为None时处理所有列

        Returns:
            pd.DataFrame: 处理后的DataFrame

        Raises:
            ValueError: 不支持的策略
        """
        # 统计原始缺失值总数：先按列统计isnull数量，再求和得到总数
        original_missing = df.isnull().sum().sum()

        # 确定目标列，用于后续针对特定列的处理
        if columns is not None:
            target_df = df[columns]
        else:
            target_df = df

        # 根据不同策略执行缺失值处理
        if strategy == 'drop':
            # 删除包含任何缺失值的行
            df_cleaned = df.dropna(subset=columns)
        elif strategy == 'drop_all':
            # 仅删除整行都是缺失值的行
            df_cleaned = df.dropna(how='all', subset=columns)
        elif strategy == 'fill':
            # 用指定值填充，默认填充空字符串
            if fill_value is None:
                fill_value = ''
            # 如果指定了列，则逐列填充，否则整体填充
            if columns:
                df_cleaned = df.copy()
                for col in columns:
                    df_cleaned[col] = df_cleaned[col].fillna(fill_value)
            else:
                df_cleaned = df.fillna(fill_value)
        elif strategy == 'ffill':
            # 向前填充（用前一个非空值填充）
            if columns:
                df_cleaned = df.copy()
                for col in columns:
                    df_cleaned[col] = df_cleaned[col].ffill()
            else:
                df_cleaned = df.ffill()
        elif strategy == 'bfill':
            # 向后填充（用后一个非空值填充）
            if columns:
                df_cleaned = df.copy()
                for col in columns:
                    df_cleaned[col] = df_cleaned[col].bfill()
            else:
                df_cleaned = df.bfill()
        elif strategy == 'mean':
            # 用均值填充，仅处理数值类型的列
            numeric_cols = target_df.select_dtypes(include=[np.number]).columns.tolist()
            df_cleaned = df.copy()
            for col in numeric_cols:
                # 检查该列是否需要处理
                if columns is None or col in columns:
                    df_cleaned[col] = df[col].fillna(df[col].mean())
        elif strategy == 'median':
            # 用中位数填充，仅处理数值类型的列
            numeric_cols = target_df.select_dtypes(include=[np.number]).columns.tolist()
            df_cleaned = df.copy()
            for col in numeric_cols:
                if columns is None or col in columns:
                    df_cleaned[col] = df[col].fillna(df[col].median())
        elif strategy == 'mode':
            # 用众数填充，适合所有数据类型（包括分类数据）
            df_cleaned = df.copy()
            for col in target_df.columns:
                if columns is None or col in columns:
                    # 注意：可能存在多个众数，取第一个；如果无众数则用fill_value
                    mode_value = df[col].mode().iloc[0] if not df[col].mode().empty else fill_value
                    df_cleaned[col] = df[col].fillna(mode_value)
        else:
            # 不支持的策略抛出异常
            raise ValueError(f"不支持的缺失值处理策略: {strategy}")

        # 统计处理后剩余的缺失值数量
        remaining_missing = df_cleaned.isnull().sum().sum()
        # 更新清洗统计信息
        self.cleaning_stats['original_missing'] = original_missing
        self.cleaning_stats['remaining_missing'] = remaining_missing
        self.cleaning_stats['handled_missing'] = original_missing - remaining_missing

        # 返回处理后的DataFrame
        return df_cleaned

    def drop_empty_rows(self, df: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
        """
        删除空行或大部分为空的行

        Args:
            df: 输入DataFrame
            threshold: 非空值比例阈值，0.0表示删除全空行，0.5表示删除超过一半为空的行

        Returns:
            pd.DataFrame: 处理后的DataFrame
        """
        original_count = len(df)
        if threshold == 0.0:
            df_cleaned = df.dropna(how='all')
        else:
            min_non_null = int(len(df.columns) * (1 - threshold))
            df_cleaned = df.dropna(thresh=min_non_null)

        removed_count = original_count - len(df_cleaned)
        self.cleaning_stats['empty_rows_removed'] = removed_count

        return df_cleaned

    def drop_empty_columns(self, df: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
        """
        删除空列或大部分为空的列

        Args:
            df: 输入DataFrame
            threshold: 非空值比例阈值，0.0表示删除全空列

        Returns:
            pd.DataFrame: 处理后的DataFrame
        """
        original_cols = len(df.columns)
        if threshold == 0.0:
            df_cleaned = df.dropna(axis=1, how='all')
        else:
            min_non_null = int(len(df) * (1 - threshold))
            df_cleaned = df.dropna(axis=1, thresh=min_non_null)

        removed_cols = original_cols - len(df_cleaned.columns)
        self.cleaning_stats['empty_cols_removed'] = removed_cols

        return df_cleaned

    def clean_data(self, df: pd.DataFrame, remove_duplicates: bool = True, duplicate_subset: Optional[List[str]] = None, missing_strategy: str = 'drop', missing_fill_value: Any = None, drop_empty_rows: bool = True, drop_empty_cols: bool = False) -> pd.DataFrame:
        """
        综合数据清洗函数

        Args:
            df: 输入DataFrame
            remove_duplicates: 是否去重
            duplicate_subset: 去重时使用的列
            missing_strategy: 缺失值处理策略
            missing_fill_value: 缺失值填充值
            drop_empty_rows: 是否删除空行
            drop_empty_cols: 是否删除空列

        Returns:
            pd.DataFrame: 清洗后的DataFrame
        """
        self.cleaning_stats = {}
        result = df.copy()

        if drop_empty_rows:
            result = self.drop_empty_rows(result)

        if drop_empty_cols:
            result = self.drop_empty_columns(result)

        if remove_duplicates:
            result = self.remove_duplicates(result, subset=duplicate_subset)

        result = self.handle_missing_values(result, strategy=missing_strategy, fill_value=missing_fill_value)

        return result

    def get_cleaning_stats(self) -> Dict[str, Any]:
        """
        获取清洗统计信息

        Returns:
            Dict[str, Any]: 统计信息字典
        """
        return self.cleaning_stats.copy()

    def reset_stats(self) -> None:
        """重置统计信息"""
        self.cleaning_stats = {}
