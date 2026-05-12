# -*- coding: utf-8 -*-
"""
自动备份同步工具 - 主入口
"""
import argparse
import sys
from backupsync import BackupSync, BackupScheduler, BackupReport


def run_backup(args):
    """
    执行单次备份任务
    """
    backup = BackupSync(
        source_dir=args.source,
        target_dir=args.target,
        exclude_patterns=args.exclude_patterns or [],
        exclude_extensions=args.exclude_extensions or [],
        exclude_dirs=args.exclude_dirs or [],
        version_count=args.version_count
    )
    
    print(f"开始备份...")
    print(f"源目录: {args.source}")
    print(f"目标目录: {args.target}")
    
    stats = backup.sync()
    
    print("\n" + "=" * 50)
    print("备份完成!")
    print(f"新增文件: {stats['added_count']} 个")
    print(f"修改文件: {stats['modified_count']} 个")
    print(f"删除文件: {stats['deleted_count']} 个")
    print(f"复制文件总大小: {stats['total_size_bytes']} 字节")
    print(f"版本目录: {stats['version_dir']}")
    print("=" * 50 + "\n")
    
    if args.report:
        report = BackupReport(args.target)
        report_path = report.save_report(stats, report_type=args.report_type)
        print(f"报告已保存: {report_path}")
    
    if args.compress:
        try:
            zip_path = backup.compress_version()
            print(f"版本已压缩: {zip_path}")
        except Exception as e:
            print(f"压缩失败: {e}")


def run_schedule(args):
    """
    启动定时备份任务
    """
    backup = BackupSync(
        source_dir=args.source,
        target_dir=args.target,
        exclude_patterns=args.exclude_patterns or [],
        exclude_extensions=args.exclude_extensions or [],
        exclude_dirs=args.exclude_dirs or [],
        version_count=args.version_count
    )
    
    scheduler = BackupScheduler(backup_func=backup.sync)
    
    if args.daily:
        scheduler.schedule_daily(args.daily)
        print(f"已设置每日 {args.daily} 执行备份")
    
    if args.hourly is not None:
        scheduler.schedule_hourly(args.hourly)
        print(f"已设置每小时第 {args.hourly} 分钟执行备份")
    
    if args.minutely:
        scheduler.schedule_minutely(args.minutely)
        print(f"已设置每 {args.minutely} 分钟执行备份")
    
    if args.weekly:
        day, time_str = args.weekly.split()
        scheduler.schedule_weekly(day, time_str)
        print(f"已设置每周 {day} {time_str} 执行备份")
    
    print("\n定时备份调度器已启动，按 Ctrl+C 停止...\n")
    scheduler.start(check_interval=args.interval)


def show_history(args):
    """
    显示备份历史
    """
    report = BackupReport(args.target)
    history = report.get_backup_history()
    
    if not history:
        print("没有找到备份历史记录")
        return
    
    print("=" * 80)
    print("备份历史记录")
    print("=" * 80)
    print(f"{'版本':<25} {'文件数':<10} {'大小':<15} {'时间':<20}")
    print("-" * 80)
    
    for item in history:
        print(f"{item['version']:<25} {item['file_count']:<10} {item['total_size_formatted']:<15} {item['timestamp']:<20}")
    
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='自动备份同步工具 - 支持增量备份和定时任务',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 执行单次备份
  python main.py backup --source /path/to/source --target /path/to/backup
  
  # 每日凌晨2点自动备份
  python main.py schedule --source /path/to/source --target /path/to/backup --daily 02:00
  
  # 每30分钟备份一次
  python main.py schedule --source /path/to/source --target /path/to/backup --minutely 30
  
  # 查看备份历史
  python main.py history --target /path/to/backup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    backup_parser = subparsers.add_parser('backup', help='执行单次备份')
    backup_parser.add_argument('--source', required=True, help='源目录路径')
    backup_parser.add_argument('--target', required=True, help='目标目录路径')
    backup_parser.add_argument('--exclude-patterns', nargs='*', help='要排除的文件/目录模式')
    backup_parser.add_argument('--exclude-extensions', nargs='*', help='要排除的文件扩展名')
    backup_parser.add_argument('--exclude-dirs', nargs='*', help='要排除的目录名')
    backup_parser.add_argument('--version-count', type=int, default=5, help='保留的历史版本数 (默认: 5)')
    backup_parser.add_argument('--report', action='store_true', help='生成备份报告')
    backup_parser.add_argument('--report-type', choices=['text', 'html'], default='text', help='报告类型 (默认: text)')
    backup_parser.add_argument('--compress', action='store_true', help='压缩备份版本')
    
    schedule_parser = subparsers.add_parser('schedule', help='启动定时备份')
    schedule_parser.add_argument('--source', required=True, help='源目录路径')
    schedule_parser.add_argument('--target', required=True, help='目标目录路径')
    schedule_parser.add_argument('--exclude-patterns', nargs='*', help='要排除的文件/目录模式')
    schedule_parser.add_argument('--exclude-extensions', nargs='*', help='要排除的文件扩展名')
    schedule_parser.add_argument('--exclude-dirs', nargs='*', help='要排除的目录名')
    schedule_parser.add_argument('--version-count', type=int, default=5, help='保留的历史版本数 (默认: 5)')
    schedule_parser.add_argument('--daily', help='每日执行时间 (格式: HH:MM)')
    schedule_parser.add_argument('--hourly', type=int, help='每小时的第几分钟执行 (0-59)')
    schedule_parser.add_argument('--minutely', type=int, help='每隔几分钟执行')
    schedule_parser.add_argument('--weekly', help='每周执行 (格式: "星期 HH:MM", 如: "monday 02:00")')
    schedule_parser.add_argument('--interval', type=int, default=1, help='检查间隔秒数 (默认: 1)')
    
    history_parser = subparsers.add_parser('history', help='查看备份历史')
    history_parser.add_argument('--target', required=True, help='备份目标目录路径')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        run_backup(args)
    elif args.command == 'schedule':
        run_schedule(args)
    elif args.command == 'history':
        show_history(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
