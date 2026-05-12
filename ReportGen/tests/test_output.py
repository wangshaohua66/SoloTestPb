"""
报表输出模块单元测试。
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

from reportgen.output import ExcelOutput, HtmlOutput, PdfOutput


class TestExcelOutput:
    """
    ExcelOutput类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        output = ExcelOutput()
        assert output.default_sheet_name == "Sheet1"

    def test_export(self, sample_dataframe, temp_dir):
        """
        测试导出Excel。
        """
        output = ExcelOutput()
        output_path = os.path.join(temp_dir, "test.xlsx")

        result = output.export(sample_dataframe, output_path)

        assert result == output_path
        assert os.path.exists(output_path)

    def test_export_multiple_sheets(self, sample_dataframe, temp_dir):
        """
        测试导出多工作表Excel。
        """
        output = ExcelOutput()
        output_path = os.path.join(temp_dir, "test_multi.xlsx")

        data_dict = {
            "Sheet1": sample_dataframe,
            "Sheet2": sample_dataframe,
        }

        result = output.export_multiple_sheets(data_dict, output_path)

        assert result == output_path
        assert os.path.exists(output_path)

    def test_export_with_formatting(self, sample_dataframe, temp_dir):
        """
        测试导出带格式的Excel。
        """
        output = ExcelOutput()
        output_path = os.path.join(temp_dir, "test_formatted.xlsx")

        format_config = {
            "header_color": "4472C4",
            "header_font_bold": True,
        }

        result = output.export_with_formatting(
            sample_dataframe, output_path, format_config=format_config
        )

        assert result == output_path
        assert os.path.exists(output_path)


class TestHtmlOutput:
    """
    HtmlOutput类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        output = HtmlOutput()
        assert output.template_engine is not None

    def test_export(self, sample_dataframe, temp_dir):
        """
        测试导出HTML。
        """
        output = HtmlOutput()
        output_path = os.path.join(temp_dir, "test.html")

        result = output.export(sample_dataframe, output_path, title="测试报表")

        assert result == output_path
        assert os.path.exists(output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<html" in content.lower()
        assert "测试报表" in content

    def test_export_with_template_string(self, sample_dataframe, temp_dir):
        """
        测试使用模板字符串导出HTML。
        """
        output = HtmlOutput()
        output_path = os.path.join(temp_dir, "test_template.html")

        template_string = """
        <!DOCTYPE html>
        <html>
        <head><title>{{ title }}</title></head>
        <body>
            <h1>{{ title }}</h1>
        </body>
        </html>
        """

        result = output.export_with_template_string(
            sample_dataframe,
            output_path,
            template_string,
            context={"title": "自定义模板"},
        )

        assert result == output_path
        assert os.path.exists(output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "自定义模板" in content

    def test_export_with_template_file(self, sample_dataframe, temp_dir):
        """
        测试使用模板文件导出HTML。
        """
        template_path = os.path.join(temp_dir, "mytemplate.html")
        with open(template_path, "w", encoding="utf-8") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>{{ title }}</title></head>
            <body>
                <h1>{{ title }}</h1>
            </body>
            </html>
            """)

        output = HtmlOutput(template_dir=temp_dir)
        output_path = os.path.join(temp_dir, "test_from_file.html")

        result = output.export_with_template(
            sample_dataframe,
            output_path,
            "mytemplate.html",
            context={"title": "文件模板测试"},
        )

        assert result == output_path
        assert os.path.exists(output_path)


class TestPdfOutput:
    """
    PdfOutput类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        output = PdfOutput()
        assert output is not None

    def test_dataframe_to_html(self, sample_dataframe):
        """
        测试将DataFrame转换为HTML。
        """
        output = PdfOutput()
        result = output._dataframe_to_html(sample_dataframe, "测试标题")
        
        assert "<html" in result.lower()
        assert "<title>测试标题</title>" in result
        assert "<h1>测试标题</h1>" in result
        assert "<table>" in result
        assert "<th>name</th>" in result

    def test_dataframe_to_html_empty_dataframe(self):
        """
        测试将空DataFrame转换为HTML。
        """
        import pandas as pd
        output = PdfOutput()
        empty_df = pd.DataFrame()
        
        result = output._dataframe_to_html(empty_df, "空报表")
        
        assert "<html" in result.lower()
        assert "<h1>空报表</h1>" in result

    def test_export_from_html_string_import_error(self, temp_dir):
        """
        测试当缺少WeasyPrint时抛出ImportError。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', False):
            with pytest.raises(ImportError, match="需要安装WeasyPrint库"):
                output.export_from_html_string("<html></html>", output_path)

    def test_export_from_dataframe_import_error(self, sample_dataframe, temp_dir):
        """
        测试DataFrame导出时缺少WeasyPrint。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', False):
            with pytest.raises(ValueError, match="DataFrame转PDF失败"):
                output.export_from_dataframe(sample_dataframe, output_path)

    def test_export_from_dataframe_with_mock(self, sample_dataframe, temp_dir):
        """
        使用mock测试DataFrame导出PDF。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_dataframe(sample_dataframe, output_path, title="测试")

                assert result == output_path
                mock_html.assert_called_once()
                mock_html_instance.write_pdf.assert_called_once_with(output_path)

    def test_export_from_html_string_with_mock(self, temp_dir):
        """
        使用mock测试HTML字符串导出PDF。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_html_string(
                    "<html><body>Test</body></html>",
                    output_path
                )

                assert result == output_path
                mock_html.assert_called_once()
                mock_html_instance.write_pdf.assert_called_once_with(output_path)

    def test_export_from_html_string_value_error(self, temp_dir):
        """
        测试转换失败时抛出ValueError。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.side_effect = Exception("Test error")
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                with pytest.raises(ValueError, match="HTML字符串转PDF失败"):
                    output.export_from_html_string("<html></html>", output_path)

    def test_export_from_dataframe_value_error(self, sample_dataframe, temp_dir):
        """
        测试DataFrame转换失败时抛出ValueError。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.side_effect = Exception("Test error")
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                with pytest.raises(ValueError, match="DataFrame转PDF失败"):
                    output.export_from_dataframe(sample_dataframe, output_path)

    def test_export_from_html_import_error(self, temp_dir):
        """
        测试HTML文件导出时缺少WeasyPrint。
        """
        output = PdfOutput()

        html_path = os.path.join(temp_dir, "test.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html></html>")

        output_path = os.path.join(temp_dir, "test.pdf")

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', False):
            with pytest.raises(ImportError, match="需要安装WeasyPrint库"):
                output.export_from_html(html_path, output_path)

    def test_export_from_html_with_mock(self, temp_dir):
        """
        使用mock测试HTML文件导出PDF。
        """
        output = PdfOutput()

        html_path = os.path.join(temp_dir, "test.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html><body>Test</body></html>")

        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_html(html_path, output_path)

                assert result == output_path
                mock_html.assert_called_once_with(filename=html_path)

    def test_export_from_dataframe_default_title(self, sample_dataframe, temp_dir):
        """
        测试DataFrame导出PDF时使用默认标题。
        """
        output = PdfOutput()
        output_path = os.path.join(temp_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_dataframe(sample_dataframe, output_path)

                assert result == output_path
                mock_html.assert_called_once()

    def test_export_from_html_string_creates_directory(self, temp_dir):
        """
        测试导出PDF时自动创建输出目录。
        """
        output = PdfOutput()
        nested_dir = os.path.join(temp_dir, "subdir1", "subdir2")
        output_path = os.path.join(nested_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_html_string("<html></html>", output_path)

                assert os.path.exists(nested_dir)
                assert result == output_path

    def test_export_from_html_creates_directory(self, temp_dir):
        """
        测试从HTML文件导出时自动创建输出目录。
        """
        output = PdfOutput()

        html_path = os.path.join(temp_dir, "test.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html></html>")

        nested_dir = os.path.join(temp_dir, "nested", "dir")
        output_path = os.path.join(nested_dir, "test.pdf")

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = None
        mock_html = MagicMock()
        mock_html.return_value = mock_html_instance

        with patch('reportgen.output.pdf_output.HAS_WEASYPRINT', True):
            with patch('reportgen.output.pdf_output.HTML', mock_html):
                result = output.export_from_html(html_path, output_path)

                assert os.path.exists(nested_dir)
                assert result == output_path
