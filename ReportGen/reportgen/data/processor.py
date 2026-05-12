"""
数据处理模块。

提供数据聚合、排序、筛选等处理功能。
"""

from typing import Any, Dict, List, Optional, Union

import pandas as pd


class DataProcessor:
    """
    数据处理器类。

    提供对pandas DataFrame进行聚合、排序、筛选等处理的功能。
    """

    def __init__(self):
        """
        初始化数据处理器。
        """
        pass

    def filter_data(
        self,
        df: pd.DataFrame,
        conditions: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        根据条件筛选数据。

        Args:
            df: 待筛选的DataFrame。
            conditions: 筛选条件字典，key为列名，value为筛选值或条件。

        Returns:
            筛选后的DataFrame。

        Raises:
            ValueError: 筛选条件无效时抛出。
        """
        if df.empty:
            return df

        try:
            filtered_df = df.copy()

            for column, condition in conditions.items():
                if column not in filtered_df.columns:
                    raise ValueError(f"列不存在: {column}")

                if isinstance(condition, dict):
                    if "min" in condition:
                        filtered_df = filtered_df[filtered_df[column] >= condition["min"]]
                    if "max" in condition:
                        filtered_df = filtered_df[filtered_df[column] <= condition["max"]]
                    if "in" in condition:
                        filtered_df = filtered_df[filtered_df[column].isin(condition["in"])]
                    if "notin" in condition:
                        filtered_df = filtered_df[~filtered_df[column].isin(condition["notin"])]
                    if "contains" in condition:
                        filtered_df = filtered_df[
                            filtered_df[column].astype(str).str.contains(
                                condition["contains"],
                                case=False,
                            )
                        ]
                    if "startswith" in condition:
                        filtered_df = filtered_df[
                            filtered_df[column].astype(str).str.startswith(
                                condition["startswith"],
                            )
                        ]
                    if "endswith" in condition:
                        filtered_df = filtered_df[
                            filtered_df[column].astype(str).str.endswith(
                                condition["endswith"],
                            )
                        ]
                else:
                    filtered_df = filtered_df[filtered_df[column] == condition]

            return filtered_df
        except Exception as e:
            raise ValueError(f"数据筛选失败: {str(e)}")

    def sort_data(
        self,
        df: pd.DataFrame,
        sort_by: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
    ) -> pd.DataFrame:
        """
        对数据进行排序。

        Args:
            df: 待排序的DataFrame。
            sort_by: 排序列名或列名列表。
            ascending: 是否升序，默认为True。

        Returns:
            排序后的DataFrame。

        Raises:
            ValueError: 排序列不存在时抛出。
        """
        if df.empty:
            return df

        try:
            return df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
        except Exception as e:
            raise ValueError(f"数据排序失败: {str(e)}")

    def aggregate_data(
        self,
        df: pd.DataFrame,
        group_by: Union[str, List[str]],
        aggregations: Dict[str, str],
    ) -> pd.DataFrame:
        """
        对数据进行聚合。

        Args:
            df: 待聚合的DataFrame。
            group_by: 分组列名或列名列表。
            aggregations: 聚合函数字典，key为列名，value为聚合函数名。
                支持的聚合函数: count, sum, mean, min, max, std, var, median。

        Returns:
            聚合后的DataFrame。

        Raises:
            ValueError: 分组列或聚合列不存在时抛出。
        """
        if df.empty:
            return df

        try:
            return df.groupby(group_by).agg(aggregations).reset_index()
        except Exception as e:
            raise ValueError(f"数据聚合失败: {str(e)}")

    def select_columns(
        self,
        df: pd.DataFrame,
        columns: List[str],
    ) -> pd.DataFrame:
        """
        选择指定列。

        Args:
            df: 原始DataFrame。
            columns: 需要保留的列名列表。

        Returns:
            只包含指定列的DataFrame。

        Raises:
            ValueError: 指定列不存在时抛出。
        """
        if df.empty:
            return df

        try:
            return df[columns].copy()
        except Exception as e:
            raise ValueError(f"选择列失败: {str(e)}")

    def rename_columns(
        self,
        df: pd.DataFrame,
        column_mapping: Dict[str, str],
    ) -> pd.DataFrame:
        """
        重命名列。

        Args:
            df: 原始DataFrame。
            column_mapping: 列名映射字典，key为旧列名，value为新列名。

        Returns:
            列名已更新的DataFrame。
        """
        return df.rename(columns=column_mapping)

    def drop_duplicates(
        self,
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = "first",
    ) -> pd.DataFrame:
        """
        删除重复行。

        Args:
            df: 原始DataFrame。
            subset: 用于判断重复的列名列表，默认为所有列。
            keep: 保留方式，'first'保留第一个，'last'保留最后一个，False删除所有重复。

        Returns:
            去重后的DataFrame。
        """
        return df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)

    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = "drop",
        fill_value: Any = None,
    ) -> pd.DataFrame:
        """
        处理缺失值。

        Args:
            df: 原始DataFrame。
            strategy: 处理策略，'drop'删除缺失值行，'fill'使用指定值填充。
            fill_value: 当strategy为'fill'时使用的填充值。

        Returns:
            处理缺失值后的DataFrame。

        Raises:
            ValueError: 无效的处理策略时抛出。
        """
        if strategy == "drop":
            return df.dropna().reset_index(drop=True)
        elif strategy == "fill":
            return df.fillna(fill_value)
        else:
            raise ValueError(f"不支持的缺失值处理策略: {strategy}")

    def process_data(
        self,
        df: pd.DataFrame,
        operations: List[Dict[str, Any]],
    ) -> pd.DataFrame:
        """
        按顺序执行一系列数据处理操作。

        Args:
            df: 原始DataFrame。
            operations: 操作列表，每个操作是一个字典，包含'type'和'params'。

        Returns:
            处理后的DataFrame。

        Raises:
            ValueError: 操作类型不支持时抛出。
        """
        result = df.copy()

        for operation in operations:
            op_type = operation.get("type")
            params = operation.get("params", {})

            if op_type == "filter":
                result = self.filter_data(result, params.get("conditions", {}))
            elif op_type == "sort":
                result = self.sort_data(
                    result,
                    params.get("sort_by"),
                    params.get("ascending", True),
                )
            elif op_type == "aggregate":
                result = self.aggregate_data(
                    result,
                    params.get("group_by"),
                    params.get("aggregations", {}),
                )
            elif op_type == "select_columns":
                result = self.select_columns(result, params.get("columns", []))
            elif op_type == "rename_columns":
                result = self.rename_columns(result, params.get("column_mapping", {}))
            elif op_type == "drop_duplicates":
                result = self.drop_duplicates(
                    result,
                    params.get("subset"),
                    params.get("keep", "first"),
                )
            elif op_type == "handle_missing":
                result = self.handle_missing_values(
                    result,
                    params.get("strategy", "drop"),
                    params.get("fill_value"),
                )
            else:
                raise ValueError(f"不支持的数据处理操作: {op_type}")

        return result
