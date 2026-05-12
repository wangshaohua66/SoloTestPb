"""
批量邮件发送管理器
负责协调所有模块，完成批量邮件发送任务
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config.settings import RetryConfig, SMTPConfig
from .data_reader import DataReader, Recipient
from .email_sender import EmailMessage, EmailSender
from .logger import SendLog, setup_logger
from .template_renderer import TemplateRenderer


@dataclass
class BatchResult:
    """
    批量发送结果数据类
    封装整个批量发送任务的统计结果
    """

    total: int = 0
    success: int = 0
    failed: int = 0
    logs: List[SendLog] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """
        计算成功率

        Returns:
            float: 成功率（0-1之间）
        """
        if self.total == 0:
            return 0.0
        return self.success / self.total

    @property
    def duration(self) -> float:
        """
        计算发送持续时间（秒）

        Returns:
            float: 持续时间（秒）
        """
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 结果字典
        """
        return {
            "total": self.total,
            "success": self.success,
            "failed": self.failed,
            "success_rate": f"{self.success_rate * 100:.2f}%",
            "duration": f"{self.duration:.2f}秒",
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            "logs": [log.to_dict() for log in self.logs],
        }

    def save_json(self, file_path: str) -> None:
        """
        保存结果为JSON文件

        Args:
            file_path: 保存路径
        """
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


class BatchMailer:
    """
    批量邮件发送器类
    整合所有模块，提供高级批量发送接口
    """

    def __init__(
        self,
        smtp_config: SMTPConfig,
        template_dir: Optional[str] = None,
        retry_config: Optional[RetryConfig] = None,
        log_level: str = "INFO",
        log_file: Optional[str] = "batch_mail.log",
    ) -> None:
        """
        初始化批量邮件发送器

        Args:
            smtp_config: SMTP配置
            template_dir: 模板目录
            retry_config: 重试配置
            log_level: 日志级别
            log_file: 日志文件名
        """
        self.smtp_config = smtp_config
        self.retry_config = retry_config or RetryConfig()
        self.template_renderer = TemplateRenderer(template_dir=template_dir)
        self.logger = setup_logger(
            name="batch_mail",
            log_level=log_level,
            log_file=log_file,
        )

    def send_from_file(
        self,
        recipients_file: str,
        subject_template: str,
        body_template: str,
        is_html: bool = True,
        common_attachments: Optional[List[str]] = None,
        save_result: Optional[str] = None,
    ) -> BatchResult:
        """
        从收件人文件发送批量邮件

        Args:
            recipients_file: 收件人文件路径（CSV/Excel）
            subject_template: 邮件主题模板
            body_template: 邮件正文模板（文件路径或字符串）
            is_html: 是否为HTML格式
            common_attachments: 公共附件列表（所有收件人都收到）
            save_result: 结果保存路径（JSON格式）

        Returns:
            BatchResult: 批量发送结果
        """
        self.logger.info(f"开始读取收件人数据: {recipients_file}")
        reader = DataReader(recipients_file)
        recipients = reader.read()
        self.logger.info(f"读取到 {len(recipients)} 个收件人")

        return self.send(
            recipients=recipients,
            subject_template=subject_template,
            body_template=body_template,
            is_html=is_html,
            common_attachments=common_attachments,
            save_result=save_result,
        )

    def send(
        self,
        recipients: List[Recipient],
        subject_template: str,
        body_template: str,
        is_html: bool = True,
        common_attachments: Optional[List[str]] = None,
        save_result: Optional[str] = None,
    ) -> BatchResult:
        """
        发送批量邮件

        Args:
            recipients: 收件人列表
            subject_template: 邮件主题模板
            body_template: 邮件正文模板（文件路径或字符串）
            is_html: 是否为HTML格式
            common_attachments: 公共附件列表
            save_result: 结果保存路径

        Returns:
            BatchResult: 批量发送结果
        """
        result = BatchResult(total=len(recipients))
        common_attachments = common_attachments or []

        self.logger.info(f"开始批量发送邮件，共 {len(recipients)} 封")

        try:
            with EmailSender(self.smtp_config, self.retry_config) as sender:
                for i, recipient in enumerate(recipients, 1):
                    try:
                        email_msg = self._build_email_message(
                            recipient=recipient,
                            subject_template=subject_template,
                            body_template=body_template,
                            is_html=is_html,
                            common_attachments=common_attachments,
                        )

                        log = sender.send(email_msg)
                        result.logs.append(log)

                        if log.success:
                            result.success += 1
                            self.logger.info(
                                f"[{i}/{len(recipients)}] 发送成功: {recipient.email}"
                            )
                        else:
                            result.failed += 1
                            self.logger.error(
                                f"[{i}/{len(recipients)}] 发送失败: {recipient.email} - "
                                f"{log.error_message}"
                            )
                    except Exception as e:
                        error_msg = f"构建邮件失败: {e}"
                        result.failed += 1
                        result.logs.append(
                            SendLog(
                                email=recipient.email,
                                success=False,
                                attempt=0,
                                error_message=error_msg,
                            )
                        )
                        self.logger.error(
                            f"[{i}/{len(recipients)}] {recipient.email} - {error_msg}"
                        )
        except Exception as e:
            self.logger.error(f"SMTP连接失败: {e}")
        finally:
            result.end_time = datetime.now()
            self._log_summary(result)

            if save_result:
                result.save_json(save_result)
                self.logger.info(f"结果已保存到: {save_result}")

        return result

    def _build_email_message(
        self,
        recipient: Recipient,
        subject_template: str,
        body_template: str,
        is_html: bool,
        common_attachments: List[str],
    ) -> EmailMessage:
        """
        构建单个邮件消息

        Args:
            recipient: 收件人
            subject_template: 主题模板
            body_template: 正文模板
            is_html: 是否HTML
            common_attachments: 公共附件

        Returns:
            EmailMessage: 邮件消息对象
        """
        context = {
            "name": recipient.name,
            "email": recipient.email,
            **recipient.variables,
        }

        subject = self.template_renderer.render_subject(subject_template, context)
        body = self.template_renderer.render_body(body_template, context, is_html)

        return EmailMessage(
            subject=subject,
            body=body,
            recipient=recipient,
            is_html=is_html,
            attachments=common_attachments,
        )

    def _log_summary(self, result: BatchResult) -> None:
        """
        记录发送摘要

        Args:
            result: 发送结果
        """
        self.logger.info("=" * 60)
        self.logger.info("发送任务完成")
        self.logger.info(f"总数: {result.total}")
        self.logger.info(f"成功: {result.success}")
        self.logger.info(f"失败: {result.failed}")
        self.logger.info(f"成功率: {result.success_rate * 100:.2f}%")
        self.logger.info(f"耗时: {result.duration:.2f}秒")
        self.logger.info("=" * 60)
