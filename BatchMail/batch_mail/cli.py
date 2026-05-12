"""
命令行接口模块
提供命令行工具入口，方便用户直接使用
"""

import argparse
import sys

from .batch_mailer import BatchMailer
from .config.settings import load_retry_config, load_smtp_config


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description="批量邮件发送工具 - 支持CSV/Excel收件人、Jinja2模板、附件、HTML格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用环境变量配置SMTP
  python -m batch_mail.cli -r recipients.csv -s "你好, {{ name }}" -t templates/email.html

  # 指定SMTP配置
  python -m batch_mail.cli --smtp-host smtp.example.com --smtp-port 465 \
      --smtp-username user@example.com --smtp-password secret \
      -r recipients.csv -s "促销邮件" -t templates/promo.html

  # 添加附件
  python -m batch_mail.cli -r recipients.xlsx -s "通知" -t "通知正文: {{ content }}" \
      --attach report.pdf

  # 保存发送结果
  python -m batch_mail.cli -r recipients.csv -s "测试" -t "hello" \
      --save-result result.json
""",
    )

    parser.add_argument(
        "-r",
        "--recipients",
        required=True,
        help="收件人数据文件路径 (CSV 或 Excel)",
    )
    parser.add_argument(
        "-s",
        "--subject",
        required=True,
        help="邮件主题（支持Jinja2模板语法）",
    )
    parser.add_argument(
        "-t",
        "--template",
        required=True,
        help="邮件正文模板（文件路径或内联字符串）",
    )

    smtp_group = parser.add_argument_group("SMTP配置")
    smtp_group.add_argument(
        "--smtp-host",
        default=None,
        help="SMTP服务器地址 (可通过环境变量 SMTP_HOST 设置)",
    )
    smtp_group.add_argument(
        "--smtp-port",
        type=int,
        default=None,
        help="SMTP端口 (默认: 465, 可通过环境变量 SMTP_PORT 设置)",
    )
    smtp_group.add_argument(
        "--smtp-username",
        default=None,
        help="SMTP用户名 (可通过环境变量 SMTP_USERNAME 设置)",
    )
    smtp_group.add_argument(
        "--smtp-password",
        default=None,
        help="SMTP密码/授权码 (可通过环境变量 SMTP_PASSWORD 设置)",
    )
    smtp_group.add_argument(
        "--sender-name",
        default=None,
        help="发件人显示名称 (可通过环境变量 SENDER_NAME 设置)",
    )
    smtp_group.add_argument(
        "--use-tls",
        action="store_true",
        default=True,
        help="使用STARTTLS加密 (默认开启)",
    )
    smtp_group.add_argument(
        "--use-ssl",
        action="store_true",
        default=False,
        help="使用SSL加密",
    )

    retry_group = parser.add_argument_group("重试配置")
    retry_group.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="最大重试次数 (默认: 3)",
    )
    retry_group.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="重试初始延迟(秒) (默认: 2.0)",
    )

    options_group = parser.add_argument_group("其他选项")
    options_group.add_argument(
        "--text",
        action="store_true",
        default=False,
        help="使用纯文本格式邮件 (默认: HTML)",
    )
    options_group.add_argument(
        "--attach",
        action="append",
        default=[],
        help="添加附件 (可重复指定)",
    )
    options_group.add_argument(
        "--template-dir",
        default=None,
        help="模板文件目录 (默认: 当前目录)",
    )
    options_group.add_argument(
        "--save-result",
        default=None,
        help="保存发送结果到JSON文件",
    )
    options_group.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别 (默认: INFO)",
    )
    options_group.add_argument(
        "--no-log-file",
        action="store_true",
        default=False,
        help="不输出日志到文件",
    )

    return parser.parse_args()


def build_smtp_config_dict(args: argparse.Namespace) -> dict:
    """
    从命令行参数构建SMTP配置字典

    Args:
        args: 命令行参数

    Returns:
        dict: SMTP配置字典
    """
    config = {}
    if args.smtp_host:
        config["smtp_host"] = args.smtp_host
    if args.smtp_port:
        config["smtp_port"] = str(args.smtp_port)
    if args.smtp_username:
        config["smtp_username"] = args.smtp_username
    if args.smtp_password:
        config["smtp_password"] = args.smtp_password
    if args.sender_name:
        config["sender_name"] = args.sender_name
    config["smtp_use_tls"] = str(args.use_tls)
    config["smtp_use_ssl"] = str(args.use_ssl)
    return config


def build_retry_config_dict(args: argparse.Namespace) -> dict:
    """
    从命令行参数构建重试配置字典

    Args:
        args: 命令行参数

    Returns:
        dict: 重试配置字典
    """
    return {
        "max_retries": str(args.max_retries),
        "retry_delay": str(args.retry_delay),
    }


def main() -> int:
    """
    主函数入口

    Returns:
        int: 退出码 (0成功, 1失败)
    """
    args = parse_args()

    try:
        smtp_config = load_smtp_config(build_smtp_config_dict(args))
        retry_config = load_retry_config(build_retry_config_dict(args))

        log_file = None if args.no_log_file else "batch_mail.log"

        mailer = BatchMailer(
            smtp_config=smtp_config,
            template_dir=args.template_dir,
            retry_config=retry_config,
            log_level=args.log_level,
            log_file=log_file,
        )

        result = mailer.send_from_file(
            recipients_file=args.recipients,
            subject_template=args.subject,
            body_template=args.template,
            is_html=not args.text,
            common_attachments=args.attach,
            save_result=args.save_result,
        )

        return 0 if result.success_rate >= 0.98 else 1

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
