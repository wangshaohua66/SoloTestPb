"""
调度器模块单元测试。
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from reportgen.scheduler import ReportScheduler


class TestReportScheduler:
    """
    ReportScheduler类的单元测试。
    """

    def test_init(self):
        """
        测试初始化。
        """
        scheduler = ReportScheduler()
        assert scheduler.jobs == []
        assert scheduler._running == False

    def test_clear_all_jobs(self):
        """
        测试清除所有任务。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        scheduler.add_daily_job("09:00", dummy_job)
        assert len(scheduler.jobs) == 1
        
        scheduler.clear_all_jobs()
        assert scheduler.jobs == []

    def test_add_daily_job(self):
        """
        测试添加每日任务。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        job = scheduler.add_daily_job("09:00", dummy_job)
        assert job is not None
        assert len(scheduler.jobs) == 1

    def test_add_hourly_job(self):
        """
        测试添加每小时任务。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        job = scheduler.add_hourly_job(1, dummy_job)
        assert job is not None
        assert len(scheduler.jobs) == 1

    def test_add_interval_job(self):
        """
        测试添加间隔分钟任务。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        job = scheduler.add_interval_job(30, dummy_job)
        assert job is not None
        assert len(scheduler.jobs) == 1

    def test_add_weekly_job(self):
        """
        测试添加每周任务。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        job = scheduler.add_weekly_job("monday", "09:00", dummy_job)
        assert job is not None
        assert len(scheduler.jobs) == 1

    def test_add_weekly_job_invalid_day(self):
        """
        测试添加每周任务时使用无效日期。
        """
        scheduler = ReportScheduler()
        
        def dummy_job():
            pass
        
        with pytest.raises(ValueError, match="无效的日期"):
            scheduler.add_weekly_job("invalid_day", "09:00", dummy_job)

    def test_stop(self):
        """
        测试停止调度器。
        """
        scheduler = ReportScheduler()
        scheduler._running = True
        
        scheduler.stop()
        assert scheduler._running == False

    def test_send_report_email(self, temp_dir):
        """
        测试发送报表邮件（使用mock）。
        """
        scheduler = ReportScheduler()
        
        # 创建一个测试文件
        test_file = os.path.join(temp_dir, "test_report.xlsx")
        with open(test_file, "w") as f:
            f.write("test content")
        
        email_config = {
            "smtp_host": "smtp.test.com",
            "smtp_port": 465,
            "sender": "test@test.com",
            "password": "password",
            "recipients": ["user@test.com"],
            "use_ssl": True
        }
        
        # 使用mock来避免实际发送邮件
        with patch.object(scheduler, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = scheduler.send_report_email(
                email_config=email_config,
                report_path=test_file,
                report_name="测试报表"
            )
            
            assert result == True
            mock_send.assert_called_once()

    def test_send_email_with_ssl(self, temp_dir):
        """
        测试使用SSL发送邮件（使用mock）。
        """
        scheduler = ReportScheduler()
        
        # 创建一个测试附件
        attachment_file = os.path.join(temp_dir, "test_attachment.txt")
        with open(attachment_file, "w") as f:
            f.write("test content")
        
        with patch('reportgen.scheduler.scheduler.smtplib') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.SMTP_SSL.return_value = mock_server
            
            result = scheduler.send_email(
                smtp_host="smtp.test.com",
                smtp_port=465,
                sender="test@test.com",
                password="password",
                recipients=["user@test.com"],
                subject="测试邮件",
                body="测试内容",
                attachments=[attachment_file],
                use_ssl=True
            )
            
            assert result == True
            mock_smtp.SMTP_SSL.assert_called_once_with("smtp.test.com", 465)
            mock_server.login.assert_called_once_with("test@test.com", "password")
            mock_server.sendmail.assert_called_once()
            mock_server.quit.assert_called_once()

    def test_send_email_without_ssl(self):
        """
        测试不使用SSL发送邮件（使用mock）。
        """
        scheduler = ReportScheduler()
        
        with patch('reportgen.scheduler.scheduler.smtplib') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.SMTP.return_value = mock_server
            
            result = scheduler.send_email(
                smtp_host="smtp.test.com",
                smtp_port=587,
                sender="test@test.com",
                password="password",
                recipients=["user1@test.com", "user2@test.com"],
                subject="测试邮件",
                body="测试内容",
                use_ssl=False
            )
            
            assert result == True
            mock_smtp.SMTP.assert_called_once_with("smtp.test.com", 587)

    def test_send_email_without_attachments(self):
        """
        测试发送不带附件的邮件（使用mock）。
        """
        scheduler = ReportScheduler()
        
        with patch('reportgen.scheduler.scheduler.smtplib') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.SMTP_SSL.return_value = mock_server
            
            result = scheduler.send_email(
                smtp_host="smtp.test.com",
                smtp_port=465,
                sender="test@test.com",
                password="password",
                recipients=["user@test.com"],
                subject="测试邮件",
                body="测试内容",
                attachments=None,
                use_ssl=True
            )
            
            assert result == True

    def test_send_email_failure(self):
        """
        测试邮件发送失败时抛出ValueError。
        """
        scheduler = ReportScheduler()
        
        with patch('reportgen.scheduler.scheduler.smtplib') as mock_smtp:
            mock_smtp.SMTP_SSL.side_effect = Exception("Connection error")
            
            with pytest.raises(ValueError, match="邮件发送失败"):
                scheduler.send_email(
                    smtp_host="smtp.test.com",
                    smtp_port=465,
                    sender="test@test.com",
                    password="password",
                    recipients=["user@test.com"],
                    subject="测试邮件",
                    body="测试内容",
                    use_ssl=True
                )

    def test_run_pending(self):
        """
        测试运行待执行的任务。
        """
        scheduler = ReportScheduler()
        
        with patch('reportgen.scheduler.scheduler.schedule') as mock_schedule:
            scheduler.run_pending()
            mock_schedule.run_pending.assert_called_once()

    def test_start_and_stop(self):
        """
        测试启动和停止调度器。
        """
        scheduler = ReportScheduler()
        call_count = [0]
        
        def mock_run_pending():
            call_count[0] += 1
            if call_count[0] >= 2:
                scheduler.stop()
        
        with patch('reportgen.scheduler.scheduler.schedule.run_pending', side_effect=mock_run_pending):
            with patch('reportgen.scheduler.scheduler.time.sleep', return_value=None):
                scheduler.start(check_interval=1)
        
        assert scheduler._running == False
        assert call_count[0] >= 2
