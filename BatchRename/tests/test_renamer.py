"""
单元测试 - 测试BatchRenamer主类和HistoryManager
"""

import os
import pytest
import allure
import shutil
import tempfile
from batch_rename.core import (
    SequenceRenameStrategy,
    ReplaceRenameStrategy,
    PrefixRenameStrategy,
    BatchRenamer,
    HistoryManager,
)


@allure.feature("历史记录管理器")
class TestHistoryManager:
    """
    测试HistoryManager类
    """

    @allure.story("保存历史记录")
    @allure.title("测试保存重命名操作历史")
    def test_save_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = HistoryManager(temp_dir)
            operations = [
                {"old_path": "/path/to/old1.txt", "new_path": "/path/to/new1.txt"},
                {"old_path": "/path/to/old2.txt", "new_path": "/path/to/new2.txt"},
            ]
            
            manager.save_history(operations)
            assert manager.has_history()
            
            loaded = manager.load_history()
            assert loaded == operations

    @allure.story("加载历史记录")
    @allure.title("测试加载历史记录")
    def test_load_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = HistoryManager(temp_dir)
            
            assert manager.load_history() is None
            assert manager.has_history() is False

    @allure.story("清除历史记录")
    @allure.title("测试清除历史记录")
    def test_clear_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = HistoryManager(temp_dir)
            operations = [
                {"old_path": "/path/to/old.txt", "new_path": "/path/to/new.txt"},
            ]
            
            manager.save_history(operations)
            assert manager.has_history()
            
            manager.clear_history()
            assert not manager.has_history()
            assert manager.load_history() is None


@allure.feature("批量重命名器")
class TestBatchRenamer:
    """
    测试BatchRenamer主类
    """

    @pytest.fixture
    def temp_directory(self):
        """
        创建临时测试目录和测试文件
        """
        temp_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        test_files = [
            "a.txt",
            "b.txt",
            "c.txt",
            "photo.jpg",
            "image.png",
            "readme",
        ]
        
        for filename in test_files:
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, "w") as f:
                f.write(f"content of {filename}")
        
        yield temp_dir
        
        # 清理
        shutil.rmtree(temp_dir)

    @allure.story("获取文件列表")
    @allure.title("测试获取目录下所有文件")
    def test_get_files(self, temp_directory):
        strategy = SequenceRenameStrategy(name="file")
        renamer = BatchRenamer(temp_directory, strategy)
        
        files = renamer.get_files()
        assert len(files) == 6
        assert "a.txt" in files
        assert "b.txt" in files
        assert "c.txt" in files
        assert "photo.jpg" in files
        assert "image.png" in files
        assert "readme" in files

    @allure.story("文件扩展名过滤")
    @allure.title("测试按扩展名过滤文件")
    def test_get_files_with_extension_filter(self, temp_directory):
        strategy = SequenceRenameStrategy(name="file")
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        files = renamer.get_files()
        assert len(files) == 3
        assert "a.txt" in files
        assert "b.txt" in files
        assert "c.txt" in files
        assert "photo.jpg" not in files
        assert "image.png" not in files

    @allure.story("多扩展名过滤")
    @allure.title("测试过滤多个扩展名")
    def test_get_files_multiple_extensions(self, temp_directory):
        strategy = SequenceRenameStrategy(name="file")
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".jpg", ".png"])
        
        files = renamer.get_files()
        assert len(files) == 2
        assert "photo.jpg" in files
        assert "image.png" in files

    @allure.story("预览功能")
    @allure.title("测试预览重命名结果")
    def test_preview(self, temp_directory):
        strategy = SequenceRenameStrategy(name="doc", padding=2)
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        preview = renamer.preview()
        assert len(preview) == 3
        
        # 检查原文件仍然存在
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "c.txt"))

    @allure.story("执行重命名")
    @allure.title("测试执行实际重命名")
    def test_execute(self, temp_directory):
        strategy = SequenceRenameStrategy(name="doc", padding=2)
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        results = renamer.execute(preview=False)
        
        assert len(results) == 3
        
        # 检查原文件不存在，新文件存在
        assert not os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "c.txt"))
        
        assert os.path.exists(os.path.join(temp_directory, "doc_01.txt"))
        assert os.path.exists(os.path.join(temp_directory, "doc_02.txt"))
        assert os.path.exists(os.path.join(temp_directory, "doc_03.txt"))

    @allure.story("预览不执行")
    @allure.title("测试预览模式不修改文件")
    def test_execute_preview_mode(self, temp_directory):
        strategy = SequenceRenameStrategy(name="doc", padding=2)
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        results = renamer.execute(preview=True)
        
        assert len(results) == 3
        
        # 检查原文件仍然存在
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "c.txt"))
        
        # 检查新文件不存在
        assert not os.path.exists(os.path.join(temp_directory, "doc_01.txt"))

    @allure.story("替换重命名")
    @allure.title("测试执行查找替换重命名")
    def test_execute_replace(self, temp_directory):
        strategy = ReplaceRenameStrategy(find="photo", replace="picture")
        renamer = BatchRenamer(temp_directory, strategy)
        
        renamer.execute(preview=False)
        
        # 检查photo.jpg应该变成picture.jpg
        assert not os.path.exists(os.path.join(temp_directory, "photo.jpg"))
        assert os.path.exists(os.path.join(temp_directory, "picture.jpg"))

    @allure.story("撤销功能")
    @allure.title("测试撤销重命名操作")
    def test_undo(self, temp_directory):
        strategy = SequenceRenameStrategy(name="file", padding=2)
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        # 执行重命名
        renamer.execute(preview=False)
        
        assert os.path.exists(os.path.join(temp_directory, "file_01.txt"))
        assert os.path.exists(os.path.join(temp_directory, "file_02.txt"))
        assert os.path.exists(os.path.join(temp_directory, "file_03.txt"))
        
        # 执行撤销
        undo_results = renamer.undo()
        
        assert len(undo_results) == 3
        
        # 检查文件恢复
        assert os.path.exists(os.path.join(temp_directory, "a.txt"))
        assert os.path.exists(os.path.join(temp_directory, "b.txt"))
        assert os.path.exists(os.path.join(temp_directory, "c.txt"))
        
        assert not os.path.exists(os.path.join(temp_directory, "file_01.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "file_02.txt"))
        assert not os.path.exists(os.path.join(temp_directory, "file_03.txt"))

    @allure.story("无历史撤销")
    @allure.title("测试没有历史记录时的撤销")
    def test_undo_without_history(self, temp_directory):
        strategy = PrefixRenameStrategy(prefix="pre_")
        renamer = BatchRenamer(temp_directory, strategy)
        
        undo_results = renamer.undo()
        assert undo_results == []

    @allure.story("目录不存在")
    @allure.title("测试目录不存在的情况")
    def test_nonexistent_directory(self):
        strategy = SequenceRenameStrategy(name="file")
        renamer = BatchRenamer("/nonexistent/directory", strategy)
        
        with pytest.raises(FileNotFoundError):
            renamer.get_files()

    @allure.story("排序一致性")
    @allure.title("测试文件列表排序的一致性")
    def test_file_sorting(self, temp_directory):
        # 创建更多文件测试排序
        for i in range(10, 15):
            filepath = os.path.join(temp_directory, f"file_{i}.txt")
            with open(filepath, "w") as f:
                f.write("content")
        
        strategy = SequenceRenameStrategy(name="test")
        renamer = BatchRenamer(temp_directory, strategy)
        
        files = renamer.get_files()
        
        # 检查文件按字母顺序排列
        for i in range(len(files) - 1):
            assert files[i] <= files[i + 1]

    @allure.story("空目录")
    @allure.title("测试空目录的情况")
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            strategy = SequenceRenameStrategy(name="file")
            renamer = BatchRenamer(empty_dir, strategy)
            
            files = renamer.get_files()
            assert files == []
            
            preview = renamer.preview()
            assert preview == []
            
            results = renamer.execute(preview=False)
            assert results == []

    @allure.story("同名文件处理")
    @allure.title("测试不会产生冲突的重命名")
    def test_no_conflict_renaming(self, temp_directory):
        # 测试不会产生同名冲突的情况
        strategy = SequenceRenameStrategy(name="renamed", padding=2)
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        results = renamer.execute(preview=False)
        
        # 所有操作应该成功
        for _, _, success in results:
            assert success

    @allure.story("历史记录清除")
    @allure.title("测试撤销后清除历史")
    def test_history_cleared_after_undo(self, temp_directory):
        strategy = SequenceRenameStrategy(name="file")
        renamer = BatchRenamer(temp_directory, strategy, file_extensions=[".txt"])
        
        # 执行重命名
        renamer.execute(preview=False)
        assert renamer.history_manager.has_history()
        
        # 执行撤销
        renamer.undo()
        assert not renamer.history_manager.has_history()
