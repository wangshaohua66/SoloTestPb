"""
报告生成模块
生成识别结果报告，支持导出文本格式
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    报告生成器类
    用于生成书法字体识别结果的文本报告
    """

    def __init__(self):
        """
        初始化报告生成器
        """
        pass

    def generate_text_report(self, recognition_result, input_text):
        """
        生成文本格式的识别报告
        
        参数:
            recognition_result: 识别结果字典
            input_text: 用户输入的原始文本
            
        返回:
            报告文本字符串
        """
        logger.info("开始生成识别报告")

        primary = recognition_result.get("primary_result", {})
        all_results = recognition_result.get("all_results", [])
        similar_fonts = recognition_result.get("similar_fonts", [])
        font_info = primary.get("font_info", {})

        report_lines = []

        report_lines.append("=" * 60)
        report_lines.append("              书法字体识别结果报告")
        report_lines.append("=" * 60)
        report_lines.append("")
        report_lines.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        report_lines.append("-" * 60)
        report_lines.append("【一、输入描述】")
        report_lines.append("-" * 60)
        report_lines.append(input_text)
        report_lines.append("")

        report_lines.append("-" * 60)
        report_lines.append("【二、识别结果】")
        report_lines.append("-" * 60)

        font_name = primary.get("font_name", "未知")
        confidence = primary.get("confidence", 0)

        report_lines.append(f"识别字体: {font_name}")
        report_lines.append(f"识别置信度: {confidence}%")
        report_lines.append("")

        if font_info:
            report_lines.append(f"英文名称: {font_info.get('english_name', '')}")
            report_lines.append(f"字体简介: {font_info.get('description', '')}")
            report_lines.append(f"历史沿革: {font_info.get('history', '')}")
            report_lines.append("")

        report_lines.append("-" * 60)
        report_lines.append("【三、识别分析】")
        report_lines.append("-" * 60)
        report_lines.append(primary.get("analysis", ""))
        report_lines.append("")

        matched_keywords = primary.get("matched_keywords", [])
        if matched_keywords:
            report_lines.append("匹配的特征关键词:")
            for kw in matched_keywords:
                report_lines.append(f"  - [{kw.get('type', '')}] {kw.get('keyword', '')}")
            report_lines.append("")

        if font_info:
            report_lines.append("-" * 60)
            report_lines.append("【四、字体特征说明】")
            report_lines.append("-" * 60)

            stroke_features = font_info.get("stroke_features", {})
            if stroke_features:
                report_lines.append("■ 笔画特征:")
                for key, value in stroke_features.items():
                    report_lines.append(f"  {key}: {value}")
                report_lines.append("")

            structure_features = font_info.get("structure_features", {})
            if structure_features:
                report_lines.append("■ 结构特征:")
                for key, value in structure_features.items():
                    report_lines.append(f"  {key}: {value}")
                report_lines.append("")

            style_features = font_info.get("style_features", [])
            if style_features:
                report_lines.append("■ 风格特征:")
                for feature in style_features:
                    report_lines.append(f"  - {feature}")
                report_lines.append("")

            key_chars = font_info.get("key_characteristics", [])
            if key_chars:
                report_lines.append("■ 关键识别特征:")
                for char in key_chars:
                    report_lines.append(f"  - {char}")
                report_lines.append("")

            rep_works = font_info.get("representative_works", [])
            if rep_works:
                report_lines.append("■ 代表作品:")
                for work in rep_works:
                    report_lines.append(f"  - {work}")
                report_lines.append("")

        if all_results:
            report_lines.append("-" * 60)
            report_lines.append("【五、所有字体匹配度】")
            report_lines.append("-" * 60)

            sorted_results = sorted(all_results, key=lambda x: x.get("confidence", 0), reverse=True)
            for result in sorted_results:
                conf = result.get("confidence", 0)
                if isinstance(conf, float) and conf <= 1:
                    conf = conf * 100
                report_lines.append(f"  {result.get('font_name', '')}: {round(conf, 2)}%")
            report_lines.append("")

        if similar_fonts:
            report_lines.append("-" * 60)
            report_lines.append("【六、相似字体比对】")
            report_lines.append("-" * 60)

            for similar in similar_fonts:
                report_lines.append(f"■ 字体: {similar.get('font_name', '')}")
                conf = similar.get("confidence", 0)
                report_lines.append(f"  匹配度: {conf}%")
                report_lines.append(f"  区别要点: {similar.get('differences', '')}")
                report_lines.append("")

        report_lines.append("-" * 60)
        report_lines.append("【七、使用建议】")
        report_lines.append("-" * 60)
        report_lines.append("1. 本识别结果基于您提供的特征描述进行匹配。")
        report_lines.append("2. 如对结果有疑问，建议提供更详细的特征描述。")
        report_lines.append("3. 可以参考相似字体的区别要点进行比对确认。")
        report_lines.append("4. 对于重要的鉴定工作，建议结合专业书法知识综合判断。")
        report_lines.append("")

        report_lines.append("=" * 60)
        report_lines.append("              书法字体识别器")
        report_lines.append("=" * 60)

        report = "\n".join(report_lines)
        logger.info("报告生成完成")
        return report

    def generate_simple_report(self, recognition_result):
        """
        生成简化版报告
        
        参数:
            recognition_result: 识别结果字典
            
        返回:
            简化版报告字符串
        """
        primary = recognition_result.get("primary_result", {})
        font_name = primary.get("font_name", "未知")
        confidence = primary.get("confidence", 0)

        report = f"""
书法字体识别结果
------------------------
识别字体: {font_name}
置信度: {confidence}%
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report.strip()
