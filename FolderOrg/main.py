#!/usr/bin/env python3
"""
文件夹自动整理工具
主入口脚本，提供命令行界面
"""

import argparse
import os
import sys
import time
from typing import Optional

from folder_organizer.config_manager import ConfigManager
from folder_organizer.file_classifier import FileClassifier
from folder_organizer.file_organizer import FileOrganizer
from folder_organizer.file_restorer import FileRestorer
from folder_organizer.logger import Logger
from folder_organizer.scheduler import Scheduler


class FolderOrganizerCLI:
    """
    文件夹整理工具命令行界面类
    提供命令行参数解析和功能调用
    """

    def __init__(self):
        """
        初始化命令行界面
        """
        self.config_manager: Optional[ConfigManager] = None
        self.logger: Optional[Logger] = None
        self.classifier: Optional[FileClassifier] = None
        self.organizer: Optional[FileOrganizer] = None
        self.restorer: Optional[FileRestorer] = None
        self.scheduler: Optional[Scheduler] = None

    def _init_components(self, source_dir: Optional[str] = None, recursive: bool = False, flatten: bool = False):
        """
        初始化所有组件

        Args:
            source_dir: 源目录路径
            recursive: 是否递归处理子目录
            flatten: 是否扁平化整理
        """
        self.config_manager = ConfigManager()
        
        log_config = self.config_manager.get("logging", {})
        self.logger = Logger(
            log_dir=log_config.get("log_dir", "logs"),
            log_level=log_config.get("log_level", "INFO"),
            max_log_size=log_config.get("max_log_size", 10485760),
            backup_count=log_config.get("backup_count", 5)
        )
        
        categories = self.config_manager.get("categories", {})
        self.classifier = FileClassifier(categories)
        
        if source_dir:
            self.organizer = FileOrganizer(source_dir, self.classifier, recursive=recursive, flatten=flatten)
            move_history = self.organizer.get_move_history()
            self.restorer = FileRestorer(move_history)

    def cmd_organize(self, args: argparse.Namespace) -> int:
        """
        执行文件整理命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        source_dir = args.source_dir or os.getcwd()
        recursive = args.recursive or False
        flatten = args.flatten or False
        
        self._init_components(source_dir, recursive=recursive, flatten=flatten)
        
        if self.logger:
            self.logger.info(f"开始整理目录: {source_dir}")
            if recursive:
                self.logger.info("递归处理子目录已启用")
            if flatten:
                self.logger.info("扁平化整理模式已启用（不保持子目录结构）")
        
        if not self.organizer:
            if self.logger:
                self.logger.error("整理器初始化失败")
            return 1
        
        result = self.organizer.organize(recursive=recursive, flatten=flatten)
        
        if self.logger:
            self.logger.log_organize_result(result)
        
        print(f"整理完成:")
        print(f"  总文件数: {result['total_files']}")
        print(f"  成功移动: {result['moved_files']}")
        print(f"  移动失败: {result['failed_files']}")
        print(f"  耗时: {result['elapsed_time']:.2f}秒")
        if 'recursive' in result:
            print(f"  递归模式: {'是' if result['recursive'] else '否'}")
        
        if result['category_stats']:
            print("  分类统计:")
            for category, count in result['category_stats'].items():
                if count > 0:
                    print(f"    - {category}: {count}个文件")
        
        return 0

    def cmd_restore(self, args: argparse.Namespace) -> int:
        """
        执行文件还原命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        source_dir = args.source_dir or os.getcwd()
        self._init_components(source_dir)
        
        if not self.restorer:
            if self.logger:
                self.logger.error("还原器初始化失败")
            return 1
        
        if args.all:
            result = self.restorer.restore_all()
            print(f"还原所有文件: 成功 {result['success_count']} 个, 失败 {result['failed_count']} 个")
        elif args.category:
            result = self.restorer.restore_by_category(args.category)
            print(f"还原分类 '{args.category}': 成功 {result['success_count']} 个, 失败 {result['failed_count']} 个")
        else:
            count = args.last or 1
            result = self.restorer.restore_last(count)
            print(f"还原最近 {count} 个文件: 成功 {result['success_count']} 个, 失败 {result['failed_count']} 个")
        
        if self.logger:
            for file_info in result['restored_files']:
                self.logger.log_file_restore(file_info['source'], file_info['target'])
        
        return 0

    def cmd_history(self, args: argparse.Namespace) -> int:
        """
        显示移动历史命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        source_dir = args.source_dir or os.getcwd()
        self._init_components(source_dir)
        
        if not self.organizer:
            return 1
        
        history = self.organizer.get_move_history(args.limit)
        
        if not history:
            print("没有移动历史记录")
            return 0
        
        print(f"移动历史记录（共 {len(history)} 条）:")
        print("-" * 80)
        for i, entry in enumerate(reversed(history), 1):
            print(f"{i}. [{entry['timestamp']}]")
            print(f"   分类: {entry['category']}")
            print(f"   源: {entry['source_path']}")
            print(f"   目标: {entry['target_path']}")
            print()
        
        return 0

    def cmd_cleanup_history(self, args: argparse.Namespace) -> int:
        """
        清理无效历史记录命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        source_dir = args.source_dir or os.getcwd()
        self._init_components(source_dir)
        
        if not self.organizer:
            return 1
        
        mode = args.mode or "conservative"
        dry_run = args.dry_run
        skip_confirm = getattr(args, 'skip_confirm', False)
        
        if dry_run:
            print("=== 预览模式（不实际执行清理）===")
        
        if mode == "aggressive" and not skip_confirm and not dry_run:
            print("警告：激进模式会删除目标文件不存在的历史记录，可能影响还原功能。")
            response = input("确认继续？(y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return 0
        
        result = self.organizer.cleanup_invalid_history(mode=mode, dry_run=dry_run)
        
        print(f"历史记录清理{'预览' if dry_run else '完成'}:")
        print(f"  清理模式: {'激进' if result['mode'] == 'aggressive' else '保守'}")
        print(f"  总记录数: {result['total_records']}")
        print(f"  发现无效记录: {result['cleaned_records']}")
        print(f"  剩余有效记录: {result['remaining_records']}")
        
        if result['invalid_reasons']:
            print(f"  无效原因（前10条）:")
            for i, reason in enumerate(result['invalid_reasons'], 1):
                print(f"    {i}. {reason}")
        
        if self.logger and not dry_run:
            self.logger.info(f"清理了 {result['cleaned_records']} 条无效历史记录，剩余 {result['remaining_records']} 条有效记录")
        
        return 0

    def cmd_schedule(self, args: argparse.Namespace) -> int:
        """
        执行定时任务命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        source_dir = args.source_dir or os.getcwd()
        self._init_components(source_dir)
        
        if not self.organizer or not self.logger:
            return 1
        
        def organize_callback():
            if self.organizer:
                return self.organizer.organize()
            return {}
        
        self.scheduler = Scheduler(organize_callback)
        self.scheduler.set_logger(self.logger)
        
        if args.type == "daily":
            self.scheduler.schedule_daily(args.time or "00:00")
        elif args.type == "hourly":
            self.scheduler.schedule_hourly(int(args.interval or 1))
        elif args.type == "minutes":
            self.scheduler.schedule_minutes(int(args.interval or 30))
        elif args.type == "weekly":
            self.scheduler.schedule_weekly(args.day or "monday", args.time or "00:00")
        
        self.scheduler.start()
        
        print("定时任务已启动，按 Ctrl+C 停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止定时任务...")
            self.scheduler.stop()
            print("定时任务已停止")
        
        return 0

    def cmd_config(self, args: argparse.Namespace) -> int:
        """
        执行配置管理命令

        Args:
            args: 命令行参数

        Returns:
            退出码
        """
        self._init_components()
        
        if not self.config_manager:
            return 1
        
        if args.list:
            config = self.config_manager.get_config()
            import json
            print(json.dumps(config, ensure_ascii=False, indent=4))
        elif args.set:
            key, value = args.set.split("=", 1)
            self.config_manager.set_config(key, value)
            self.config_manager.save_config()
            print(f"配置已更新: {key} = {value}")
        elif args.add_category:
            name = args.add_category
            extensions = [ext.strip() for ext in args.extensions.split(",")] if args.extensions else []
            target_dir = args.target_dir or name
            self.config_manager.add_category(name, extensions, target_dir)
            self.config_manager.save_config()
            print(f"已添加分类: {name}")
        elif args.remove_category:
            if self.config_manager.remove_category(args.remove_category):
                self.config_manager.save_config()
                print(f"已删除分类: {args.remove_category}")
            else:
                print(f"分类不存在: {args.remove_category}")
        
        return 0

    def run(self) -> int:
        """
        运行命令行界面

        Returns:
            退出码
        """
        parser = argparse.ArgumentParser(
            description="文件夹自动整理工具",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        organize_parser = subparsers.add_parser("organize", help="整理文件夹")
        organize_parser.add_argument("-s", "--source-dir", help="源目录路径（默认为当前目录）")
        organize_parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录中的文件")
        organize_parser.add_argument("-f", "--flatten", action="store_true", 
                                     help="扁平化整理：所有文件直接放到分类目录，不保持子目录结构（与--recursive配合使用）")
        organize_parser.set_defaults(func=self.cmd_organize)
        
        restore_parser = subparsers.add_parser("restore", help="还原文件")
        restore_parser.add_argument("-s", "--source-dir", help="源目录路径（默认为当前目录）")
        restore_group = restore_parser.add_mutually_exclusive_group()
        restore_group.add_argument("--last", type=int, help="还原最近N个文件")
        restore_group.add_argument("--category", help="还原指定分类的所有文件")
        restore_group.add_argument("--all", action="store_true", help="还原所有文件")
        restore_parser.set_defaults(func=self.cmd_restore)
        
        history_parser = subparsers.add_parser("history", help="查看移动历史")
        history_parser.add_argument("-s", "--source-dir", help="源目录路径（默认为当前目录）")
        history_parser.add_argument("--limit", type=int, help="显示最近N条记录")
        history_parser.set_defaults(func=self.cmd_history)
        
        schedule_parser = subparsers.add_parser("schedule", help="定时整理")
        schedule_parser.add_argument("-s", "--source-dir", help="源目录路径（默认为当前目录）")
        schedule_parser.add_argument("--type", choices=["daily", "hourly", "minutes", "weekly"], required=True, help="定时类型")
        schedule_parser.add_argument("--time", help="执行时间（格式: HH:MM）")
        schedule_parser.add_argument("--interval", help="间隔小时/分钟数")
        schedule_parser.add_argument("--day", help="每周几（monday, tuesday等）")
        schedule_parser.set_defaults(func=self.cmd_schedule)
        
        config_parser = subparsers.add_parser("config", help="管理配置")
        config_group = config_parser.add_mutually_exclusive_group()
        config_group.add_argument("--list", action="store_true", help="列出当前配置")
        config_group.add_argument("--set", help="设置配置项（格式: key=value）")
        config_group.add_argument("--add-category", help="添加新分类")
        config_group.add_argument("--remove-category", help="删除分类")
        config_parser.add_argument("--extensions", help="分类的文件扩展名（逗号分隔）")
        config_parser.add_argument("--target-dir", help="分类的目标目录")
        config_parser.set_defaults(func=self.cmd_config)
        
        cleanup_parser = subparsers.add_parser("cleanup", help="清理无效的历史记录")
        cleanup_parser.add_argument("-s", "--source-dir", help="源目录路径（默认为当前目录）")
        cleanup_parser.add_argument("--mode", choices=["conservative", "aggressive"], default="conservative",
                                     help="清理模式：conservative（保守，只清理格式不完整）/ aggressive（激进，清理所有无效）")
        cleanup_parser.add_argument("--dry-run", action="store_true", help="预览模式，只显示要清理的内容不实际执行")
        cleanup_parser.add_argument("-y", "--yes", dest="skip_confirm", action="store_true", 
                                     help="跳过所有确认提示，直接执行清理")
        cleanup_parser.add_argument("--force", dest="skip_confirm", action="store_true", 
                                     help="跳过所有确认提示，直接执行清理（--yes的别名）")
        cleanup_parser.set_defaults(func=self.cmd_cleanup_history)
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        return args.func(args)


def main():
    """
    主函数
    """
    cli = FolderOrganizerCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
