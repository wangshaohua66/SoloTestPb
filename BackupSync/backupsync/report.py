# -*- coding: utf-8 -*-
"""
备份报告模块
生成备份统计报告
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class BackupReport:
    """
    备份报告生成类，用于创建和保存备份统计报告
    """
    
    def __init__(self, target_dir: str):
        """
        初始化备份报告生成器
        
        参数:
            target_dir: 备份目标目录路径
        """
        self.target_dir = Path(target_dir).resolve()
    
    def _format_size(self, bytes_size: int) -> str:
        """
        将字节数转换为人类可读的格式
        
        参数:
            bytes_size: 字节数
            
        返回:
            格式化的大小字符串
        """
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.2f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.2f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"
    
    def _count_files_and_size(self, directory: Path) -> (int, int):
        """
        统计目录中的文件数量和总大小
        
        参数:
            directory: 目录路径
            
        返回:
            元组包含：文件数量，总大小（字节）
        """
        file_count = 0
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                    file_count += 1
                except (OSError, IOError):
                    continue
        
        return file_count, total_size
    
    def generate_text_report(self, stats: Dict[str, Any]) -> str:
        """
        生成文本格式的备份报告
        
        参数:
            stats: 备份统计信息字典
            
        返回:
            格式化的文本报告字符串
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("自动备份同步工具 - 备份报告")
        report_lines.append("=" * 60)
        report_lines.append("")
        report_lines.append(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"版本目录: {stats.get('version_dir', 'N/A')}")
        report_lines.append("")
        report_lines.append("-" * 60)
        report_lines.append("文件变更统计")
        report_lines.append("-" * 60)
        report_lines.append(f"新增文件数: {stats.get('added_count', 0)}")
        report_lines.append(f"修改文件数: {stats.get('modified_count', 0)}")
        report_lines.append(f"删除文件数: {stats.get('deleted_count', 0)}")
        report_lines.append(f"总计复制文件数: {stats.get('total_copied', 0)}")
        report_lines.append(f"复制文件总大小: {self._format_size(stats.get('total_size_bytes', 0))}")
        report_lines.append("")
        
        added_files = stats.get('added_files', [])
        if added_files:
            report_lines.append("-" * 60)
            report_lines.append("新增文件列表")
            report_lines.append("-" * 60)
            for file in added_files:
                report_lines.append(f"  [新增] {file}")
            report_lines.append("")
        
        modified_files = stats.get('modified_files', [])
        if modified_files:
            report_lines.append("-" * 60)
            report_lines.append("修改文件列表")
            report_lines.append("-" * 60)
            for file in modified_files:
                report_lines.append(f"  [修改] {file}")
            report_lines.append("")
        
        deleted_files = stats.get('deleted_files', [])
        if deleted_files:
            report_lines.append("-" * 60)
            report_lines.append("删除文件列表")
            report_lines.append("-" * 60)
            for file in deleted_files:
                report_lines.append(f"  [删除] {file}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        report_lines.append("报告生成完成")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def generate_html_report(self, stats: Dict[str, Any]) -> str:
        """
        生成HTML格式的备份报告
        
        参数:
            stats: 备份统计信息字典
            
        返回:
            格式化的HTML报告字符串
        """
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>备份报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-item {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .stat-value {{ color: #2c3e50; font-size: 1.5em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #e9ecef; }}
        .added {{ color: #28a745; }}
        .modified {{ color: #ffc107; }}
        .deleted {{ color: #dc3545; }}
    </style>
</head>
<body>
    <h1>自动备份同步工具 - 备份报告</h1>
    <p><strong>备份时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>版本目录:</strong> {stats.get('version_dir', 'N/A')}</p>
    
    <div class="section">
        <h2>文件变更统计</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">新增文件数</div>
                <div class="stat-value added">{stats.get('added_count', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">修改文件数</div>
                <div class="stat-value modified">{stats.get('modified_count', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">删除文件数</div>
                <div class="stat-value deleted">{stats.get('deleted_count', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">总复制文件数</div>
                <div class="stat-value">{stats.get('total_copied', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">复制文件总大小</div>
                <div class="stat-value">{self._format_size(stats.get('total_size_bytes', 0))}</div>
            </div>
        </div>
    </div>
"""
        
        added_files = stats.get('added_files', [])
        if added_files:
            html += f"""
    <div class="section">
        <h2 class="added">新增文件列表</h2>
        <table>
            <tr><th>文件路径</th></tr>
            {''.join(f'<tr><td class="added">{file}</td></tr>' for file in added_files)}
        </table>
    </div>
"""
        
        modified_files = stats.get('modified_files', [])
        if modified_files:
            html += f"""
    <div class="section">
        <h2 class="modified">修改文件列表</h2>
        <table>
            <tr><th>文件路径</th></tr>
            {''.join(f'<tr><td class="modified">{file}</td></tr>' for file in modified_files)}
        </table>
    </div>
"""
        
        deleted_files = stats.get('deleted_files', [])
        if deleted_files:
            html += f"""
    <div class="section">
        <h2 class="deleted">删除文件列表</h2>
        <table>
            <tr><th>文件路径</th></tr>
            {''.join(f'<tr><td class="deleted">{file}</td></tr>' for file in deleted_files)}
        </table>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def save_report(
        self,
        stats: Dict[str, Any],
        report_type: str = 'text',
        filename: Optional[str] = None
    ) -> Path:
        """
        保存备份报告到文件
        
        参数:
            stats: 备份统计信息字典
            report_type: 报告类型，可选值: 'text', 'html'
            filename: 报告文件名，如果为None则自动生成
            
        返回:
            保存的报告文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if filename is None:
            ext = 'txt' if report_type == 'text' else 'html'
            filename = f"backup_report_{timestamp}.{ext}"
        
        report_dir = self.target_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / filename
        
        if report_type == 'text':
            content = self.generate_text_report(stats)
        else:
            content = self.generate_html_report(stats)
        
        report_path.write_text(content, encoding='utf-8')
        
        return report_path
    
    def get_backup_history(self) -> List[Dict[str, Any]]:
        """
        获取备份历史记录
        
        返回:
            备份历史列表，每个元素包含版本信息
        """
        history = []
        
        if not self.target_dir.exists():
            return history
        
        version_dirs = sorted(
            [d for d in self.target_dir.iterdir() if d.is_dir() and d.name.startswith('v_')],
            key=lambda d: d.name,
            reverse=True
        )
        
        for version_dir in version_dirs:
            file_count, total_size = self._count_files_and_size(version_dir)
            history.append({
                'version': version_dir.name,
                'timestamp': version_dir.name.replace('v_', ''),
                'file_count': file_count,
                'total_size': total_size,
                'total_size_formatted': self._format_size(total_size)
            })
        
        return history
