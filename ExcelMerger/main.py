#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据合并工具 - 主程序入口
提供命令行接口用于合并多个Excel文件
"""

import click
import os
from excel_merger import ExcelMerger, ExcelReader, MergeReporter


@click.group()
def cli():
    """Excel数据合并工具 - 支持多种合并策略"""
    pass


@cli.command()
@click.option('--input-dir', '-i', required=True, type=click.Path(exists=True), help='输入目录路径')
@click.option('--output', '-o', required=True, type=click.Path(), help='输出文件路径')
@click.option('--sheet-name', '-s', default=None, help='工作表名称')
@click.option('--remove-duplicates/--no-remove-duplicates', default=True, help='是否去重')
@click.option('--missing-strategy', default='fill', type=click.Choice(['drop', 'fill', 'ffill', 'bfill', 'mean', 'median', 'mode']), help='缺失值处理策略')
@click.option('--missing-fill-value', default='', help='缺失值填充值')
@click.option('--report-dir', default=None, type=click.Path(), help='报告输出目录')
@click.option('--report-format', default='txt', type=click.Choice(['txt', 'json']), help='报告格式')
def merge_row(input_dir, output, sheet_name, remove_duplicates, missing_strategy, missing_fill_value, report_dir, report_format):
    """按行合并（追加数据）"""
    click.echo(f"开始按行合并...")
    click.echo(f"输入目录: {input_dir}")
    click.echo(f"输出文件: {output}")

    reader = ExcelReader()
    merger = ExcelMerger()
    reporter = MergeReporter()

    file_paths = reader.get_files_from_directory(input_dir)
    click.echo(f"找到 {len(file_paths)} 个文件")

    if not file_paths:
        click.echo("错误: 目录中没有找到支持的文件")
        return

    try:
        result, stats = merger.merge_by_row(
            file_paths,
            sheet_name=sheet_name,
            remove_duplicates=remove_duplicates,
            missing_strategy=missing_strategy,
            missing_fill_value=missing_fill_value
        )

        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
        merger.save_result(result, output)
        click.echo(f"合并成功！结果已保存到: {output}")

        reporter.print_summary(stats)

        if report_dir:
            report = reporter.generate_report(stats, report_dir, report_format)
            click.echo(f"报告已生成")

    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)


@cli.command()
@click.option('--input-dir', '-i', required=True, type=click.Path(exists=True), help='输入目录路径')
@click.option('--output', '-o', required=True, type=click.Path(), help='输出文件路径')
@click.option('--sheet-name', '-s', default=None, help='工作表名称')
@click.option('--join-method', default='outer', type=click.Choice(['inner', 'outer']), help='列合并方式')
@click.option('--report-dir', default=None, type=click.Path(), help='报告输出目录')
@click.option('--report-format', default='txt', type=click.Choice(['txt', 'json']), help='报告格式')
def merge_col(input_dir, output, sheet_name, join_method, report_dir, report_format):
    """按列合并（合并字段）"""
    click.echo(f"开始按列合并...")
    click.echo(f"输入目录: {input_dir}")
    click.echo(f"输出文件: {output}")

    reader = ExcelReader()
    merger = ExcelMerger()
    reporter = MergeReporter()

    file_paths = reader.get_files_from_directory(input_dir)
    click.echo(f"找到 {len(file_paths)} 个文件")

    if not file_paths:
        click.echo("错误: 目录中没有找到支持的文件")
        return

    try:
        result, stats = merger.merge_by_column(
            file_paths,
            sheet_name=sheet_name,
            join=join_method
        )

        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
        merger.save_result(result, output)
        click.echo(f"合并成功！结果已保存到: {output}")

        reporter.print_summary(stats)

        if report_dir:
            report = reporter.generate_report(stats, report_dir, report_format)
            click.echo(f"报告已生成")

    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)


@cli.command()
@click.option('--input-dir', '-i', required=True, type=click.Path(exists=True), help='输入目录路径')
@click.option('--output', '-o', required=True, type=click.Path(), help='输出文件路径')
@click.option('--key', '-k', required=True, help='关联键列名')
@click.option('--join-type', default='inner', type=click.Choice(['inner', 'left', 'right', 'outer']), help='关联类型')
@click.option('--sheet-name', '-s', default=None, help='工作表名称')
@click.option('--report-dir', default=None, type=click.Path(), help='报告输出目录')
@click.option('--report-format', default='txt', type=click.Choice(['txt', 'json']), help='报告格式')
def merge_join(input_dir, output, key, join_type, sheet_name, report_dir, report_format):
    """按指定键值进行关联合并（类似SQL JOIN）"""
    click.echo(f"开始关联合并...")
    click.echo(f"输入目录: {input_dir}")
    click.echo(f"输出文件: {output}")
    click.echo(f"关联键: {key}")
    click.echo(f"关联类型: {join_type}")

    reader = ExcelReader()
    merger = ExcelMerger()
    reporter = MergeReporter()

    file_paths = reader.get_files_from_directory(input_dir)
    click.echo(f"找到 {len(file_paths)} 个文件")

    if not file_paths:
        click.echo("错误: 目录中没有找到支持的文件")
        return

    try:
        result, stats = merger.merge_by_join(
            file_paths,
            join_key=key,
            how=join_type,
            sheet_name=sheet_name
        )

        os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
        merger.save_result(result, output)
        click.echo(f"合并成功！结果已保存到: {output}")

        reporter.print_summary(stats)

        if report_dir:
            report = reporter.generate_report(stats, report_dir, report_format)
            click.echo(f"报告已生成")

    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
def list_files(input_dir):
    """列出目录中的所有支持的Excel/CSV文件"""
    reader = ExcelReader()
    file_paths = reader.get_files_from_directory(input_dir)

    click.echo(f"在 {input_dir} 中找到 {len(file_paths)} 个文件:")
    for i, path in enumerate(file_paths, 1):
        click.echo(f"  {i}. {os.path.basename(path)}")
        try:
            info = reader.get_file_info(path)
            if info:
                click.echo(f"     行数: {info.get('rows', 'N/A')}, 列数: {len(info.get('columns', []))}")
        except:
            pass


if __name__ == '__main__':
    cli()
