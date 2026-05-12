import os
import pandas as pd
from typing import List, Dict, Any, Optional


class ExcelReader:
    """
    Excel文件读取类，支持读取xlsx、xls、csv格式文件

    功能特点:
    1. 支持三种主流数据文件格式的读取
    2. 自动根据文件扩展名选择合适的读取引擎
    3. 提供批量文件读取功能
    4. 自动记录文件元信息（行数、列名等）
    5. 支持从目录自动扫描支持的文件
    6. 支持获取Excel文件工作表名称列表
    """

    # 支持的文件扩展名常量，用于格式校验和目录扫描
    SUPPORTED_EXTENSIONS = ('.xlsx', '.xls', '.csv')

    def __init__(self):
        """
        初始化ExcelReader实例

        创建一个字典用于缓存最近读取的文件元信息，
        避免重复读取文件来获取基本信息，提高性能
        """
        # 缓存已读取文件的元信息，键为文件路径，值为信息字典
        self.last_file_info = {}

    def read_file(self, file_path: str, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        读取单个Excel或CSV文件

        根据文件扩展名自动选择合适的读取引擎：
        - .csv: 使用pandas.read_csv()
        - .xls: 使用xlrd引擎读取旧版Excel文件
        - .xlsx: 使用openpyxl引擎读取新版Excel文件

        Args:
            file_path: 要读取的文件的完整路径
            sheet_name: 工作表名称或索引（仅对Excel文件有效）
                       为None时默认读取第一个工作表（索引0）
            **kwargs: 额外的关键字参数，将传递给pandas的读取函数
                     例如：header, sep, encoding等

        Returns:
            pd.DataFrame: 读取到的数据表

        Raises:
            FileNotFoundError: 当指定的文件路径不存在时抛出
            ValueError: 当文件格式不被支持时抛出
            Exception: 读取过程中发生其他错误时抛出（如文件损坏）
        """
        # 第一步：检查文件是否存在，不存在则抛出异常
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 第二步：获取文件扩展名并转换为小写，用于格式判断
        ext = os.path.splitext(file_path)[1].lower()

        # 第三步：检查文件格式是否被支持，不支持则抛出异常
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}。支持的格式: {', '.join(self.SUPPORTED_EXTENSIONS)}")

        try:
            # 第四步：根据扩展名选择对应的读取方式
            if ext == '.csv':
                # CSV格式：直接使用pandas.read_csv读取
                df = pd.read_csv(file_path, **kwargs)
            elif ext == '.xls':
                # XLS格式（Excel 97-2003）：使用xlrd引擎
                # 未指定sheet_name时默认读取第一个工作表（索引0）
                if sheet_name is None:
                    sheet_name = 0
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd', **kwargs)
            else:  # .xlsx格式（Excel 2007及以后）
                # 使用openpyxl引擎读取，兼容性更好
                if sheet_name is None:
                    sheet_name = 0
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', **kwargs)

            # 第五步：记录文件元信息到缓存，供后续get_file_info使用
            # 包含：数据行数、列名列表、数据形状（行数x列数）
            self.last_file_info[file_path] = {
                'rows': len(df),
                'columns': list(df.columns),
                'shape': df.shape
            }

            # 第六步：返回读取到的DataFrame数据
            return df
        except Exception as e:
            # 捕获所有读取异常，包装成更友好的错误信息后抛出
            raise Exception(f"读取文件 {file_path} 时出错: {str(e)}")

    def read_multiple_files(self, file_paths: List[str], sheet_name: Optional[str] = None, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        批量读取多个文件

        遍历文件路径列表，逐个调用read_file方法读取文件。
        单个文件读取失败不会中断整个批量读取流程，失败的文件对应值为None。

        Args:
            file_paths: 文件路径字符串列表
            sheet_name: 工作表名称或索引（仅对Excel文件有效）
            **kwargs: 额外的关键字参数，将传递给每个文件的读取函数

        Returns:
            Dict[str, pd.DataFrame]: 结果字典，键为文件路径，值为对应的DataFrame
                   读取失败的文件对应值为None
        """
        # 初始化结果字典
        results = {}

        # 遍历每个文件路径进行读取
        for file_path in file_paths:
            try:
                # 尝试读取单个文件
                df = self.read_file(file_path, sheet_name, **kwargs)
                # 读取成功，存入结果字典
                results[file_path] = df
            except Exception as e:
                # 读取失败，设置为None并打印警告信息
                # 不抛出异常，确保批量读取不被中断
                results[file_path] = None
                print(f"警告: 读取文件 {file_path} 失败: {str(e)}")

        # 返回最终结果字典
        return results

    def get_files_from_directory(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """
        从目录中递归扫描并获取所有支持的Excel/CSV文件路径

        使用os.walk递归遍历目录及其子目录，根据扩展名筛选支持的文件。
        返回的文件路径列表按字母顺序排序，确保结果一致性。

        Args:
            directory: 要扫描的目录路径
            extensions: 指定要搜索的扩展名列表，如 ['.xlsx', '.csv']
                       为None时使用默认的SUPPORTED_EXTENSIONS

        Returns:
            List[str]: 符合条件的文件完整路径列表，已按字母排序
        """
        # 如果未指定扩展名列表，使用默认支持的所有格式
        if extensions is None:
            extensions = self.SUPPORTED_EXTENSIONS

        # 初始化文件路径列表
        file_paths = []

        # 使用os.walk递归遍历目录树
        # root: 当前遍历的目录路径
        # _: 子目录列表（用_表示暂不使用）
        # files: 当前目录下的文件名列表
        for root, _, files in os.walk(directory):
            # 遍历当前目录下的所有文件
            for file in files:
                # 获取文件扩展名并转换为小写
                ext = os.path.splitext(file)[1].lower()
                # 检查扩展名是否在目标列表中
                if ext in extensions:
                    # 拼接完整路径并添加到结果列表
                    file_paths.append(os.path.join(root, file))

        # 按字母顺序排序后返回，确保多次调用结果一致
        return sorted(file_paths)

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件的元信息（行数、列名、形状）

        首先检查缓存中是否有该文件的信息，有则直接返回；
        没有则先读取文件再返回信息。利用缓存机制提高重复调用性能。

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息字典，包含：
                   - rows: 数据行数（int）
                   - columns: 列名列表（List[str]）
                   - shape: 数据形状（行数, 列数）
                   如果获取失败则返回空字典
        """
        # 先检查缓存，如果已有信息则直接返回
        if file_path in self.last_file_info:
            return self.last_file_info[file_path]

        # 缓存中没有，先读取文件（读取时会自动缓存信息）
        self.read_file(file_path)
        # 从缓存中获取并返回（即使读取失败也返回空字典）
        return self.last_file_info.get(file_path, {})

    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        获取Excel文件的所有工作表名称列表

        注意：仅适用于.xlsx和.xls格式的Excel文件，CSV文件没有工作表概念。
        使用with语句确保ExcelFile对象在使用后自动关闭，避免资源泄漏。

        Args:
            file_path: Excel文件路径

        Returns:
            List[str]: 工作表名称字符串列表

        Raises:
            ValueError: 当文件不是Excel格式（.xlsx或.xls）时抛出
            Exception: 获取工作表名称过程中发生其他错误时抛出
        """
        # 获取文件扩展名并转换为小写
        ext = os.path.splitext(file_path)[1].lower()

        # 检查是否为Excel格式，非Excel格式抛出异常
        if ext not in ('.xlsx', '.xls'):
            raise ValueError(f"只能获取Excel文件的工作表名称: {ext}")

        try:
            # 根据扩展名选择对应的引擎
            # 使用with语句创建ExcelFile上下文管理器，确保资源自动释放
            if ext == '.xls':
                # XLS格式使用xlrd引擎
                with pd.ExcelFile(file_path, engine='xlrd') as xl_file:
                    return xl_file.sheet_names
            else:
                # XLSX格式使用openpyxl引擎
                with pd.ExcelFile(file_path, engine='openpyxl') as xl_file:
                    return xl_file.sheet_names
        except Exception as e:
            # 捕获异常并包装成友好的错误信息后抛出
            raise Exception(f"获取工作表名称失败: {str(e)}")
