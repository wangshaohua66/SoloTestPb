import pytest
import allure
import os
from click.testing import CliRunner
from src.cli import cli


@allure.feature('命令行接口')
class TestCLI:
    
    @pytest.fixture
    def runner(self):
        """创建CLI测试运行器"""
        return CliRunner()
    
    @allure.story('合并PDF命令')
    def test_merge_command(self, runner, sample_pdfs, temp_dir):
        """测试合并PDF命令正常场景"""
        output_path = str(temp_dir / "merged.pdf")
        
        result = runner.invoke(
            cli, 
            ['merge', '--inputs', sample_pdfs[0], '--inputs', sample_pdfs[1], '--inputs', sample_pdfs[2], '--output', output_path]
        )
        
        assert result.exit_code == 0
        assert '合并完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('合并PDF命令 - 缺少参数')
    def test_merge_command_missing_args(self, runner):
        """测试合并PDF命令缺少参数的情况"""
        result = runner.invoke(cli, ['merge'])
        assert result.exit_code != 0
    
    @allure.story('拆分PDF命令')
    def test_split_command(self, runner, sample_pdf, temp_dir):
        """测试拆分PDF命令正常场景"""
        output_path = str(temp_dir / "splitted.pdf")
        
        result = runner.invoke(
            cli, 
            ['split', '--input', sample_pdf, '--output', output_path, '--start', '1', '--end', '2']
        )
        
        assert result.exit_code == 0
        assert '拆分完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('拆分PDF命令 - 缺少参数')
    def test_split_command_missing_args(self, runner):
        """测试拆分PDF命令缺少参数的情况"""
        result = runner.invoke(cli, ['split'])
        assert result.exit_code != 0
    
    @allure.story('提取文本命令')
    def test_extract_text_command(self, runner, sample_pdf, temp_dir):
        """测试提取文本命令正常场景"""
        output_path = str(temp_dir / "output.txt")
        
        result = runner.invoke(
            cli, 
            ['extract-text', '--input', sample_pdf, '--output', output_path]
        )
        
        assert result.exit_code == 0
        assert '文本提取完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('提取文本命令 - 无输出文件')
    def test_extract_text_command_no_output(self, runner, sample_pdf):
        """测试提取文本命令不指定输出文件的情况"""
        result = runner.invoke(
            cli, 
            ['extract-text', '--input', sample_pdf]
        )
        
        assert result.exit_code == 0
    
    @allure.story('提取图片命令')
    def test_extract_images_command(self, runner, sample_pdf, temp_dir):
        """测试提取图片命令正常场景"""
        output_dir = str(temp_dir / "images")
        
        result = runner.invoke(
            cli, 
            ['extract-images', '--input', sample_pdf, '--output-dir', output_dir]
        )
        
        assert result.exit_code == 0
        assert '图片提取完成' in result.output
        assert os.path.exists(output_dir)
    
    @allure.story('提取图片命令 - 缺少参数')
    def test_extract_images_command_missing_args(self, runner):
        """测试提取图片命令缺少参数的情况"""
        result = runner.invoke(cli, ['extract-images'])
        assert result.exit_code != 0
    
    @allure.story('添加页码命令')
    def test_add_page_numbers_command(self, runner, sample_pdf, temp_dir):
        """测试添加页码命令正常场景"""
        output_path = str(temp_dir / "with_numbers.pdf")
        
        result = runner.invoke(
            cli, 
            ['add-page-numbers', '--input', sample_pdf, '--output', output_path]
        )
        
        assert result.exit_code == 0
        assert '页码添加完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('添加页码命令 - 自定义位置')
    def test_add_page_numbers_command_with_position(self, runner, sample_pdf, temp_dir):
        """测试添加页码命令使用自定义位置"""
        output_path = str(temp_dir / "with_numbers.pdf")
        
        result = runner.invoke(
            cli, 
            ['add-page-numbers', '--input', sample_pdf, '--output', output_path, '--position', 'bottom_center']
        )
        
        assert result.exit_code == 0
    
    @allure.story('添加页眉页脚命令')
    def test_add_header_footer_command(self, runner, sample_pdf, temp_dir):
        """测试添加页眉页脚命令正常场景"""
        output_path = str(temp_dir / "with_header.pdf")
        
        result = runner.invoke(
            cli, 
            ['add-header-footer', '--input', sample_pdf, '--output', output_path, '--header', '测试页眉', '--footer', '测试页脚']
        )
        
        assert result.exit_code == 0
        assert '页眉页脚添加完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('加密PDF命令')
    def test_encrypt_command(self, runner, sample_pdf, temp_dir):
        """测试加密PDF命令正常场景"""
        output_path = str(temp_dir / "encrypted.pdf")
        
        result = runner.invoke(
            cli, 
            ['encrypt', '--input', sample_pdf, '--output', output_path, '--password', 'test123']
        )
        
        assert result.exit_code == 0
        assert '加密完成' in result.output
        assert os.path.exists(output_path)
    
    @allure.story('加密PDF命令 - 缺少密码')
    def test_encrypt_command_missing_password(self, runner, sample_pdf, temp_dir):
        """测试加密PDF命令缺少密码的情况"""
        output_path = str(temp_dir / "encrypted.pdf")
        
        result = runner.invoke(
            cli, 
            ['encrypt', '--input', sample_pdf, '--output', output_path]
        )
        
        assert result.exit_code != 0
    
    @allure.story('解密PDF命令')
    def test_decrypt_command(self, runner, sample_pdf, temp_dir):
        """测试解密PDF命令正常场景"""
        encrypted_path = str(temp_dir / "encrypted.pdf")
        decrypted_path = str(temp_dir / "decrypted.pdf")
        
        # 先加密
        from src.pdf_security import PDFSecurity
        security = PDFSecurity()
        security.encrypt_pdf(sample_pdf, encrypted_path, password="test123")
        
        result = runner.invoke(
            cli, 
            ['decrypt', '--input', encrypted_path, '--output', decrypted_path, '--password', 'test123']
        )
        
        assert result.exit_code == 0
        assert '解密完成' in result.output
        assert os.path.exists(decrypted_path)
    
    @allure.story('解密PDF命令 - 缺少密码')
    def test_decrypt_command_missing_password(self, runner, sample_pdf, temp_dir):
        """测试解密PDF命令缺少密码的情况"""
        output_path = str(temp_dir / "decrypted.pdf")
        
        result = runner.invoke(
            cli, 
            ['decrypt', '--input', sample_pdf, '--output', output_path]
        )
        
        assert result.exit_code != 0
    
    @allure.story('文件不存在 - 错误处理')
    def test_file_not_found_error(self, runner, temp_dir):
        """测试输入文件不存在时的错误处理"""
        nonexistent_file = str(temp_dir / "nonexistent.pdf")
        output_path = str(temp_dir / "output.pdf")
        
        result = runner.invoke(
            cli, 
            ['merge', '--inputs', nonexistent_file, '--output', output_path]
        )
        
        assert result.exit_code != 0
