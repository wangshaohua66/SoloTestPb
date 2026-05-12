"""
日志记录模块单元测试
"""

import os
import pytest
from folder_organizer.logger import Logger


class TestLogger:
    """
    日志记录器测试类
    """

    def test_init(self, temp_dir):
        """
        测试初始化
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir)
        
        assert os.path.exists(log_dir)
        assert logger.log_dir == log_dir
        assert logger.log_level == "INFO"

    def test_log_levels(self, temp_dir):
        """
        测试不同日志级别
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir, log_level="DEBUG")
        
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
        
        log_file = os.path.join(log_dir, "organizer.log")
        assert os.path.exists(log_file)
        
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "debug message" in content
        assert "info message" in content
        assert "warning message" in content
        assert "error message" in content
        assert "critical message" in content

    def test_log_organize_result(self, temp_dir):
        """
        测试记录整理结果
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir)
        
        result = {
            "total_files": 10,
            "moved_files": 8,
            "failed_files": 2,
            "elapsed_time": 0.5,
            "category_stats": {
                "documents": 5,
                "images": 3
            }
        }
        
        logger.log_organize_result(result)
        
        log_file = os.path.join(log_dir, "organizer.log")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "文件整理完成" in content
        assert "总文件数: 10" in content
        assert "成功移动: 8" in content
        assert "移动失败: 2" in content
        assert "documents: 5" in content
        assert "images: 3" in content

    def test_log_file_moved(self, temp_dir):
        """
        测试记录文件移动
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir)
        
        logger.log_file_moved("/source/file.pdf", "/target/Documents/file.pdf", "documents")
        
        log_file = os.path.join(log_dir, "organizer.log")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "文件移动" in content
        assert "/source/file.pdf" in content
        assert "/target/Documents/file.pdf" in content
        assert "documents" in content

    def test_log_file_restore(self, temp_dir):
        """
        测试记录文件还原
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir)
        
        logger.log_file_restore("/target/file.pdf", "/source/file.pdf")
        
        log_file = os.path.join(log_dir, "organizer.log")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "文件还原" in content
        assert "/target/file.pdf" in content
        assert "/source/file.pdf" in content

    def test_log_schedule(self, temp_dir):
        """
        测试记录定时任务
        """
        log_dir = os.path.join(temp_dir, "test_logs")
        logger = Logger(log_dir=log_dir)
        
        logger.log_schedule_start()
        logger.log_schedule_stop()
        
        log_file = os.path.join(log_dir, "organizer.log")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "定时整理任务已启动" in content
        assert "定时整理任务已停止" in content

    def test_get_log_level(self):
        """
        测试获取日志级别
        """
        import logging
        
        assert Logger._get_log_level("DEBUG") == logging.DEBUG
        assert Logger._get_log_level("INFO") == logging.INFO
        assert Logger._get_log_level("WARNING") == logging.WARNING
        assert Logger._get_log_level("ERROR") == logging.ERROR
        assert Logger._get_log_level("CRITICAL") == logging.CRITICAL
        assert Logger._get_log_level("INVALID") == logging.INFO
        assert Logger._get_log_level("debug") == logging.DEBUG
