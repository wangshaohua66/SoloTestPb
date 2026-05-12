"""
单元测试 - 测试CLI命令行界面
"""

import os
import pytest
import allure
import shutil
import tempfile
import sys
from io import StringIO
from unittest.mock import patch
from batch_rename.cli import main


@allure.feature("命令行界面")
class TestCLI:
    """
    测试CLI命令行界面
    """

    @pytest.fixture
    def temp_directory(self):
        """
        创建临时测试目录
        """
        temp_dir = tempfile.mkdtemp()
        
        test_files = [
            "a.txt",
            "b.txt",
            "c.txt",
            "photo.jpg",
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("test content")
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)

    @allure.story("帮助信息")
    @allure.title("测试显示帮助信息")
    def test_help(self):
        with patch.object(sys, 'argv', ['batch_rename', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @allure.story("缺少模式参数")
    @allure.title("测试缺少必需的模式参数")
    def test_missing_mode(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("目录不存在")
    @allure.title("测试指定的目录不存在")
    def test_nonexistent_directory(self):
        with patch.object(sys, 'argv', ['batch_rename', '/nonexistent/path', '--mode', 'sequence', '--name', 'file']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("序列模式缺少name")
    @allure.title("测试序列模式缺少name参数")
    def test_sequence_missing_name(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'sequence']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("替换模式缺少find")
    @allure.title("测试替换模式缺少find参数")
    def test_replace_missing_find(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'replace', '--replace', 'new']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("替换模式缺少replace")
    @allure.title("测试替换模式缺少replace参数")
    def test_replace_missing_replace(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'replace', '--find', 'old']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("前缀模式缺少prefix")
    @allure.title("测试前缀模式缺少prefix参数")
    def test_prefix_missing_prefix(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'prefix']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("后缀模式缺少suffix")
    @allure.title("测试后缀模式缺少suffix参数")
    def test_suffix_missing_suffix(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'suffix']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("正则模式缺少pattern")
    @allure.title("测试正则模式缺少pattern参数")
    def test_regex_missing_pattern(self, temp_directory):
        with patch.object(sys, 'argv', ['batch_rename', temp_directory, '--mode', 'regex', '--replace', 'new']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @allure.story("预览模式")
    @allure.title("测试预览模式不修改文件")
    def test_preview_mode(self, temp_directory):
        test_args = [
            'batch_rename',
            temp_directory,
            '--mode', 'sequence',
            '--name', 'test',
            '--preview'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                main()
        
        # 检查文件没有被修改
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "c.txt"))

    @allure.story("扩展名过滤")
    @allure.title("测试按扩展名过滤")
    def test_extension_filter(self, temp_directory):
        test_args = [
            'batch_rename',
            temp_directory,
            '--mode', 'prefix',
            '--prefix', '2024_',
            '--ext', '.jpg',
            '--preview'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                main()
        
        # 检查所有文件仍然存在
        assert os.path.exists(os.path.join(temp_directory, "photo.jpg"))
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))

    @allure.story("无历史撤销")
    @allure.title("测试没有历史记录时的撤销操作")
    def test_undo_no_history(self, temp_directory):
        test_args = ['batch_rename', temp_directory, '--undo']
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    @allure.story("强制执行模式")
    @allure.title("测试--force参数跳过交互式确认")
    def test_force_mode(self, temp_directory):
        test_args = [
            'batch_rename',
            temp_directory,
            '--mode', 'prefix',
            '--prefix', 'test_',
            '--force'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                main()
        
        # 检查文件被重命名（不需要用户确认）
        assert os.path.exists(os.path.join(temp_directory, "test_a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "test_b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "test_c.txt"))
        assert os.path.exists(os.path.join(temp_directory, "test_photo.jpg"))
        
        # 检查原文件不存在
        assert not os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "c.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "photo.jpg"))

    @allure.story("交互式确认取消")
    @allure.title("测试交互式确认时选择取消")
    def test_interactive_cancel(self, temp_directory):
        test_args = [
            'batch_rename',
            temp_directory,
            '--mode', 'prefix',
            '--prefix', 'test_'
        ]
        
        with patch.object(sys, 'argv', test_args):
            with patch('builtins.print'):
                with patch('builtins.input', return_value='n'):
                    main()
        
        # 检查文件没有被重命名
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "c.txt"))
        assert os.path.exists(os.path.join(temp_directory, "photo.jpg"))
