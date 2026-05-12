import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


class MergeReporter:
    """
    合并报告生成类，用于生成合并过程的详细报告

    功能特点:
    1. 支持两种报告格式：人性化的纯文本格式和机器可读的JSON格式
    2. 记录完整的合并统计信息，包括文件处理情况、数据清洗结果等
    3. 提供报告历史记录功能，可查询所有已生成报告
    4. 支持将报告保存到指定目录，自动创建带时间戳的文件名
    5. 提供控制台摘要打印功能，适合快速查看合并结果
    """

    def __init__(self):
        """
        初始化MergeReporter实例

        创建一个列表用于存储所有已生成报告的历史记录，
        便于后续查询、导出或分析多次合并操作的结果
        """
        # 报告历史记录列表，每个元素是一个报告数据字典
        self.reports = []

    def generate_report(self, merge_stats: Dict[str, Any], output_dir: Optional[str] = None, format: str = 'txt') -> str:
        """
        生成合并报告

        根据传入的合并统计信息生成对应格式的报告内容，
        可选将报告保存到指定目录，并将报告添加到历史记录中。

        Args:
            merge_stats: 合并统计信息字典，由ExcelMerger类生成
                        包含策略类型、文件处理情况、行数变化、清洗结果等
            output_dir: 报告输出目录路径，为None则不保存到文件
            format: 报告格式，可选值：
                   - 'txt': 纯文本格式，适合人类阅读（默认）
                   - 'json': JSON格式，适合程序解析

        Returns:
            str: 生成的报告内容字符串
        """
        # 获取当前时间戳，用于标记报告生成时间
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构造标准报告数据结构
        report_data = {
            'timestamp': timestamp,      # 报告生成时间
            'merge_stats': merge_stats   # 合并统计信息
        }

        # 根据格式选择生成方式
        if format == 'json':
            # JSON格式：使用json.dumps序列化
            # ensure_ascii=False确保中文正确显示，indent=2格式化输出
            report_content = json.dumps(report_data, ensure_ascii=False, indent=2)
        else:
            # 文本格式：调用内部方法生成格式化的文本报告
            report_content = self._generate_text_report(report_data)

        # 将报告数据添加到历史记录中
        self.reports.append(report_data)

        # 如果指定了输出目录，则将报告保存到文件
        if output_dir:
            self._save_report(report_content, output_dir, format, timestamp)

        # 返回生成的报告内容字符串
        return report_content

    def _generate_text_report(self, report_data: Dict[str, Any]) -> str:
        """
        生成文本格式的报告（内部方法）

        格式化输出合并统计信息，包括：
        - 报告标题和生成时间
        - 合并策略和基本统计
        - 数据清洗结果（去重、缺失值处理）
        - 关联合并或列合并的特殊信息
        - 每个文件的详细处理情况
        - 合并后的列名列表

        Args:
            report_data: 报告数据字典，包含timestamp和merge_stats

        Returns:
            str: 格式化的文本报告内容，使用换行符分隔各行
        """
        # 从报告数据中提取合并统计信息
        stats = report_data['merge_stats']
        # 初始化行列表，用于逐行构建报告内容
        lines = []

        # 第一部分：报告头部，包含标题和生成时间
        lines.append("=" * 60)
        lines.append("Excel 数据合并报告")
        lines.append(f"生成时间: {report_data['timestamp']}")
        lines.append("=" * 60)
        lines.append("")  # 空行分隔

        # 第二部分：基本合并信息
        lines.append(f"合并策略: {stats.get('strategy', 'N/A')}")
        lines.append(f"处理文件数: {stats.get('files_processed', 0)}")
        lines.append(f"失败文件数: {stats.get('files_failed', 0)}")
        lines.append("")  # 空行分隔

        # 第三部分：行数变化信息（仅按行合并且有原始行数记录时显示）
        if 'original_rows' in stats:
            lines.append(f"原始总行数: {stats['original_rows']}")
        lines.append(f"合并后行数: {stats.get('merged_rows', 0)}")
        lines.append(f"合并后列数: {len(stats.get('merged_columns', []))}")
        lines.append("")  # 空行分隔

        # 第四部分：数据清洗统计（仅执行了清洗操作时显示）
        if 'duplicates_removed' in stats:
            lines.append(f"去除重复行数: {stats['duplicates_removed']}")
        if 'handled_missing' in stats:
            lines.append(f"处理缺失值数量: {stats['handled_missing']}")
        if 'remaining_missing' in stats:
            lines.append(f"剩余缺失值数量: {stats['remaining_missing']}")
        lines.append("")  # 空行分隔

        # 第五部分：关联合并的特殊信息（仅关联合并时显示）
        if 'join_key' in stats:
            lines.append(f"关联键: {stats['join_key']}")
            lines.append(f"关联类型: {stats['join_type']}")
            lines.append("")  # 空行分隔

        # 第六部分：按列合并的特殊信息（仅按列合并时显示）
        if 'merge_method' in stats:
            lines.append(f"列合并方式: {stats['merge_method']}")
            lines.append("")  # 空行分隔

        # 第七部分：文件详情列表
        lines.append("-" * 60)
        lines.append("文件详情:")
        lines.append("-" * 60)
        # 遍历每个文件的处理详情
        for detail in stats.get('file_details', []):
            # 根据处理状态显示不同符号：✓成功，✗失败
            status = "✓" if detail['status'] == 'success' else "✗"
            lines.append(f"{status} {detail['file']}")
            if detail['status'] == 'success':
                # 成功文件显示行数和列数信息
                lines.append(f"    行数: {detail['rows']}, 列数: {len(detail['columns'])}")
            else:
                # 失败文件显示错误信息
                lines.append(f"    错误: {detail.get('error', 'Unknown')}")
        lines.append("")  # 空行分隔

        # 第八部分：合并后的列名列表（如果有列名信息）
        if stats.get('merged_columns'):
            lines.append("-" * 60)
            lines.append("合并后列名:")
            lines.append("-" * 60)
            # 逐行列示所有列名
            for col in stats['merged_columns']:
                lines.append(f"  - {col}")
            lines.append("")  # 空行分隔

        # 第九部分：报告尾部
        lines.append("=" * 60)
        lines.append("报告结束")
        lines.append("=" * 60)

        # 将所有行用换行符连接，形成最终报告文本
        return '\n'.join(lines)

    def _save_report(self, content: str, output_dir: str, format: str, timestamp: str) -> None:
        """
        保存报告内容到文件（内部方法）

        自动创建输出目录（如果不存在），生成带时间戳的唯一文件名，
        使用UTF-8编码写入文件以确保中文正确显示。

        Args:
            content: 要保存的报告内容字符串
            output_dir: 输出目录路径
            format: 文件扩展名（不带点），如'txt'或'json'
            timestamp: 报告生成的时间戳字符串（保留但不直接使用）
        """
        # 创建输出目录，exist_ok=True表示目录已存在时不报错
        os.makedirs(output_dir, exist_ok=True)

        # 生成唯一的文件名，使用当前时间戳避免重名
        # 格式：merge_report_YYYYMMDD_HHMMSS.ext
        filename_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"merge_report_{filename_timestamp}.{format}"
        # 拼接完整文件路径
        filepath = os.path.join(output_dir, filename)

        # 使用with语句确保文件正确关闭，指定UTF-8编码
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # 打印提示信息，告知用户报告已保存
        print(f"报告已保存到: {filepath}")

    def get_all_reports(self) -> list:
        """
        获取所有历史报告记录

        返回报告列表的副本，避免外部代码修改内部状态。
        每个报告元素包含timestamp（生成时间）和merge_stats（合并统计）。

        Returns:
            list: 报告历史列表的副本
        """
        # 返回副本而不是原列表，保证数据安全
        return self.reports.copy()

    def clear_reports(self) -> None:
        """
        清空报告历史记录

        重置reports列表为空，释放内存空间。
        适用于长时间运行的应用程序定期清理历史数据。
        """
        # 重置为空白列表
        self.reports = []

    def print_summary(self, merge_stats: Dict[str, Any]) -> None:
        """
        打印合并摘要信息到控制台

        输出比完整报告更简洁的摘要信息，适合在命令行快速查看合并结果。
        包含：策略类型、文件处理结果、行数/列数、清洗统计等关键信息。

        Args:
            merge_stats: 合并统计信息字典
        """
        # 打印分隔线和标题
        print("\n" + "=" * 50)
        print("合并完成摘要")
        print("=" * 50)

        # 打印基本信息
        print(f"策略: {merge_stats.get('strategy', 'N/A')}")
        print(f"文件: {merge_stats.get('files_processed', 0)} 成功, {merge_stats.get('files_failed', 0)} 失败")
        print(f"行数: {merge_stats.get('merged_rows', 0)}")
        print(f"列数: {len(merge_stats.get('merged_columns', []))}")

        # 打印去重信息（如果有）
        if 'duplicates_removed' in merge_stats:
            print(f"去重: {merge_stats['duplicates_removed']} 行")
        # 打印缺失值处理信息（如果有）
        if 'handled_missing' in merge_stats:
            print(f"处理缺失值: {merge_stats['handled_missing']} 个")

        # 打印结束分隔线
        print("=" * 50 + "\n")
