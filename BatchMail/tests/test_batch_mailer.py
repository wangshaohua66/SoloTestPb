"""
批量邮件发送模块单元测试
"""

import os
from unittest.mock import MagicMock, patch

import allure

from batch_mail.batch_mailer import BatchMailer, BatchResult
from batch_mail.data_reader import Recipient
from batch_mail.logger import SendLog


@allure.feature("批量邮件")
@allure.story("BatchResult数据类")
class TestBatchResult:
    """
    BatchResult测试类
    """

    @allure.title("测试默认值")
    def test_default_values(self):
        """
        测试默认值
        """
        result = BatchResult()

        assert result.total == 0
        assert result.success == 0
        assert result.failed == 0
        assert result.logs == []

    @allure.title("测试成功率计算")
    def test_success_rate(self):
        """
        测试成功率计算
        """
        result = BatchResult(total=100, success=98, failed=2)

        assert result.success_rate == 0.98

    @allure.title("测试空列表成功率为0")
    def test_zero_success_rate(self):
        """
        测试空列表时成功率为0
        """
        result = BatchResult(total=0, success=0, failed=0)

        assert result.success_rate == 0.0

    @allure.title("测试成功率100%")
    def test_100_percent_success_rate(self):
        """
        测试全部成功时成功率为1
        """
        result = BatchResult(total=10, success=10, failed=0)

        assert result.success_rate == 1.0

    @allure.title("测试持续时间")
    def test_duration(self):
        """
        测试持续时间计算
        """
        from datetime import datetime, timedelta

        result = BatchResult(start_time=datetime.now())
        result.end_time = result.start_time + timedelta(seconds=5)

        assert result.duration >= 5.0

    @allure.title("测试转换为字典")
    def test_to_dict(self):
        """
        测试to_dict方法
        """
        from datetime import datetime

        log = SendLog(
            email="test@example.com",
            success=True,
            attempt=1,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
        )

        result = BatchResult(
            total=100,
            success=95,
            failed=5,
            logs=[log],
            start_time=datetime(2024, 1, 1, 10, 0, 0),
            end_time=datetime(2024, 1, 1, 10, 1, 0),
        )

        d = result.to_dict()

        assert d["total"] == 100
        assert d["success"] == 95
        assert d["failed"] == 5
        assert d["success_rate"] == "95.00%"
        assert len(d["logs"]) == 1
        assert "duration" in d
        assert "start_time" in d
        assert "end_time" in d

    @allure.title("测试保存JSON")
    def test_save_json(self, temp_dir):
        """
        测试保存为JSON文件
        """
        import json

        save_path = os.path.join(temp_dir, "result.json")
        result = BatchResult(total=10, success=9, failed=1)

        result.save_json(save_path)

        assert os.path.exists(save_path)

        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["total"] == 10
        assert data["success"] == 9
        assert data["failed"] == 1


@allure.feature("批量邮件")
@allure.story("BatchMailer初始化")
class TestBatchMailerInit:
    """
    BatchMailer初始化测试类
    """

    @allure.title("测试初始化")
    def test_init(self, smtp_config, temp_dir):
        """
        测试正常初始化
        """
        mailer = BatchMailer(
            smtp_config=smtp_config,
            template_dir=temp_dir,
            log_file=None,
        )

        assert mailer.smtp_config is smtp_config
        assert mailer.template_renderer is not None
        assert mailer.logger is not None

    @allure.title("测试默认重试配置")
    def test_default_retry_config(self, smtp_config):
        """
        测试默认重试配置
        """
        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)

        assert mailer.retry_config is not None
        assert mailer.retry_config.max_retries == 3


@allure.feature("批量邮件")
@allure.story("批量发送")
class TestBatchMailerSend:
    """
    BatchMailer发送测试类
    """

    @allure.title("测试批量发送成功")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_send_all_success(self, mock_sender_class, smtp_config, sample_recipients):
        """
        测试全部发送成功
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender

        mock_sender.send.side_effect = [
            SendLog(email=r.email, success=True, attempt=1)
            for r in sample_recipients
        ]

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        result = mailer.send(
            recipients=sample_recipients,
            subject_template="测试 {{ name }}",
            body_template="Hello {{ name }}",
            is_html=False,
        )

        assert result.total == 2
        assert result.success == 2
        assert result.failed == 0
        assert result.success_rate == 1.0

    @allure.title("测试批量发送部分失败")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_send_partial_failure(self, mock_sender_class, smtp_config, sample_recipients):
        """
        测试部分发送失败
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender

        mock_sender.send.side_effect = [
            SendLog(email=sample_recipients[0].email, success=True, attempt=1),
            SendLog(
                email=sample_recipients[1].email,
                success=False,
                attempt=3,
                error_message="连接超时",
            ),
        ]

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        result = mailer.send(
            recipients=sample_recipients,
            subject_template="测试",
            body_template="Hello",
            is_html=False,
        )

        assert result.total == 2
        assert result.success == 1
        assert result.failed == 1
        assert result.success_rate == 0.5

    @allure.title("测试模板渲染")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_template_rendering(self, mock_sender_class, smtp_config):
        """
        测试模板渲染
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender

        captured_messages = []

        def capture_send(email_msg):
            captured_messages.append(email_msg)
            return SendLog(email=email_msg.recipient.email, success=True, attempt=1)

        mock_sender.send.side_effect = capture_send

        recipients = [
            Recipient(email="a@example.com", name="用户A", variables={"company": "公司A"}),
            Recipient(email="b@example.com", name="用户B", variables={"company": "公司B"}),
        ]

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        mailer.send(
            recipients=recipients,
            subject_template="来自 {{ company }} 的邮件",
            body_template="您好 {{ name }}，您来自 {{ company }}",
            is_html=False,
        )

        assert len(captured_messages) == 2
        assert captured_messages[0].subject == "来自 公司A 的邮件"
        assert "用户A" in captured_messages[0].body
        assert captured_messages[1].subject == "来自 公司B 的邮件"
        assert "用户B" in captured_messages[1].body

    @allure.title("测试构建邮件失败处理")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_build_message_failure(self, mock_sender_class, smtp_config):
        """
        测试构建邮件失败时的处理
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender

        recipients = [
            Recipient(email="test@example.com", name="Test"),
        ]

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)

        mailer.template_renderer.render_subject = MagicMock(
            side_effect=Exception("Template error")
        )

        result = mailer.send(
            recipients=recipients,
            subject_template="{{ invalid",
            body_template="test",
            is_html=False,
        )

        assert result.total == 1
        assert result.failed == 1
        assert "构建邮件失败" in result.logs[0].error_message

    @allure.title("测试从文件发送")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_send_from_file(self, mock_sender_class, smtp_config, sample_csv_path):
        """
        测试从文件发送
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender
        mock_sender.send.return_value = SendLog(
            email="test@example.com", success=True, attempt=1
        )

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        result = mailer.send_from_file(
            recipients_file=sample_csv_path,
            subject_template="测试",
            body_template="Hello",
            is_html=False,
        )

        assert result.total == 3

    @allure.title("测试保存结果")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_save_result(self, mock_sender_class, smtp_config, sample_recipients, temp_dir):
        """
        测试保存发送结果
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender
        mock_sender.send.return_value = SendLog(
            email="test@example.com", success=True, attempt=1
        )

        save_path = os.path.join(temp_dir, "result.json")

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        mailer.send(
            recipients=sample_recipients,
            subject_template="测试",
            body_template="Hello",
            is_html=False,
            save_result=save_path,
        )

        assert os.path.exists(save_path)

    @allure.title("测试SMTP连接失败")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_smtp_connection_failure(self, mock_sender_class, smtp_config, sample_recipients):
        """
        测试SMTP连接失败
        """
        mock_sender_class.return_value.__enter__.side_effect = Exception("SMTP connection failed")

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        result = mailer.send(
            recipients=sample_recipients,
            subject_template="测试",
            body_template="Hello",
            is_html=False,
        )

        assert result.total == 2
        assert result.success == 0
        assert result.failed == 0
        assert result.success_rate == 0.0

    @allure.title("测试公共附件")
    @patch("batch_mail.batch_mailer.EmailSender")
    def test_common_attachments(self, mock_sender_class, smtp_config, temp_dir):
        """
        测试公共附件
        """
        mock_sender = MagicMock()
        mock_sender_class.return_value.__enter__.return_value = mock_sender

        captured_messages = []

        def capture_send(email_msg):
            captured_messages.append(email_msg)
            return SendLog(email=email_msg.recipient.email, success=True, attempt=1)

        mock_sender.send.side_effect = capture_send

        att_path = os.path.join(temp_dir, "att.txt")
        with open(att_path, "w") as f:
            f.write("test")

        recipients = [Recipient(email="test@example.com")]

        mailer = BatchMailer(smtp_config=smtp_config, log_file=None)
        mailer.send(
            recipients=recipients,
            subject_template="测试",
            body_template="Hello",
            is_html=False,
            common_attachments=[att_path],
        )

        assert att_path in captured_messages[0].attachments
