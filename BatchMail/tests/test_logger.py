"""
日志系统模块单元测试
"""

import logging
import os
import time
from datetime import datetime

import allure

from batch_mail.logger import SendLog, setup_logger


@allure.feature("日志系统")
@allure.story("SendLog数据类")
class TestSendLog:
    """
    SendLog测试类
    """

    @allure.title("测试SendLog成功记录")
    def test_send_log_success(self):
        """
        测试成功发送的日志记录
        """
        log = SendLog(
            email="test@example.com",
            success=True,
            attempt=1,
        )

        assert log.email == "test@example.com"
        assert log.success is True
        assert log.attempt == 1
        assert log.error_message is None
        assert isinstance(log.timestamp, datetime)

    @allure.title("测试SendLog失败记录")
    def test_send_log_failure(self):
        """
        测试失败发送的日志记录
        """
        log = SendLog(
            email="failed@example.com",
            success=False,
            attempt=3,
            error_message="SMTP服务器连接失败",
        )

        assert log.success is False
        assert log.attempt == 3
        assert log.error_message == "SMTP服务器连接失败"

    @allure.title("测试SendLog转换为字典")
    def test_send_log_to_dict(self):
        """
        测试to_dict方法
        """
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        log = SendLog(
            email="test@example.com",
            success=True,
            attempt=1,
            timestamp=timestamp,
        )

        d = log.to_dict()

        assert d["email"] == "test@example.com"
        assert d["success"] is True
        assert d["attempt"] == 1
        assert d["timestamp"] == "2024-01-01 12:00:00"

    @allure.title("测试SendLog字符串表示")
    def test_send_log_str_success(self):
        """
        测试成功日志的字符串表示
        """
        log = SendLog(
            email="test@example.com",
            success=True,
            attempt=1,
        )

        log_str = str(log)

        assert "test@example.com" in log_str
        assert "成功" in log_str
        assert "尝试次数: 1" in log_str

    @allure.title("测试SendLog失败字符串表示")
    def test_send_log_str_failure(self):
        """
        测试失败日志的字符串表示
        """
        log = SendLog(
            email="test@example.com",
            success=False,
            attempt=3,
            error_message="网络错误",
        )

        log_str = str(log)

        assert "失败" in log_str
        assert "尝试次数: 3" in log_str
        assert "网络错误" in log_str


@allure.feature("日志系统")
@allure.story("Logger配置")
class TestSetupLogger:
    """
    setup_logger测试类
    """

    @allure.title("测试创建Logger")
    def test_create_logger(self):
        """
        测试创建Logger
        """
        logger = setup_logger(name="test_logger", log_level="DEBUG")

        assert logger is not None
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG

    @allure.title("测试Logger级别转换")
    def test_logger_levels(self):
        """
        测试不同日志级别
        """
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        expected = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level, expected_level in zip(levels, expected):
            logger = setup_logger(name=f"test_{level}", log_level=level)
            assert logger.level == expected_level

    @allure.title("测试文件日志输出")
    def test_file_logger(self, temp_dir: str):
        """
        测试文件日志输出
        """
        logger = setup_logger(
            name="file_logger_test",
            log_level="INFO",
            log_file="test.log",
            log_dir=temp_dir,
        )

        test_message = "测试日志消息"
        logger.info(test_message)

        time.sleep(0.1)

        log_files = os.listdir(temp_dir)
        assert len(log_files) == 1

        log_path = os.path.join(temp_dir, log_files[0])
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert test_message in content

    @allure.title("测试重复调用返回同一Logger")
    def test_same_logger_on_repeated_call(self):
        """
        测试重复调用返回同一Logger
        """
        logger1 = setup_logger(name="same_logger", log_level="DEBUG")
        logger2 = setup_logger(name="same_logger", log_level="INFO")

        assert logger1 is logger2

    @allure.title("测试默认日志级别")
    def test_default_log_level(self):
        """
        测试默认日志级别
        """
        logger = setup_logger(name="default_logger", log_level="UNKNOWN")

        assert logger.level == logging.INFO
