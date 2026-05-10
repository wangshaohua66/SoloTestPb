# -*- coding: utf-8 -*-
"""
日志解析模块
自动解析日志时间、级别、模块、内容等字段，支持自定义解析规则
"""
import re
import json
from datetime import datetime
from typing import Dict, Optional, List

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL', 'WARN', 'ERR', 'TRACE']


class LogParser:
    """
    日志解析器
    支持多种常见日志格式的自动识别和解析
    """
    
    def __init__(self):
        """
        初始化日志解析器
        加载预设的解析规则和自定义规则
        """
        self.patterns = self._get_builtin_patterns()
        self._custom_rules: List[Dict] = []
    
    def _get_builtin_patterns(self) -> List[Dict]:
        """
        获取内置的日志解析规则
        
        Returns:
            规则列表，每个规则包含正则表达式、分组映射等信息
        """
        return [
            {
                'name': 'nginx_access',
                'pattern': re.compile(
                    r'^(?P<host>\S+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
                    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
                    r'(?P<status>\d+) (?P<size>\d+) '
                    r'"(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"$'
                ),
                'time_format': '%d/%b/%Y:%H:%M:%S %z',
                'service': 'nginx'
            },
            {
                'name': 'nginx_error',
                'pattern': re.compile(
                    r'^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
                    r'\[(?P<level>\w+)\] (?P<pid>\d+)#(?P<tid>\d+): '
                    r'(?:\*(?P<connection>\d+) )?(?P<message>.*)$'
                ),
                'time_format': '%Y/%m/%d %H:%M:%S',
                'service': 'nginx'
            },
            {
                'name': 'syslog_rfc3164',
                'pattern': re.compile(
                    r'^(?P<month>\w{3})\s+(?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) '
                    r'(?P<host>\S+) (?P<module>\S+)(?:\[(?P<pid>\d+)\])?: (?P<message>.*)$'
                ),
                'time_format': None,
                'service': 'syslog'
            },
            {
                'name': 'python_default',
                'pattern': re.compile(
                    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
                    r'(?P<name>\S+) - (?P<level>\w+) - (?P<message>.*)$'
                ),
                'time_format': '%Y-%m-%d %H:%M:%S,%f',
                'service': 'python'
            },
            {
                'name': 'python_simple',
                'pattern': re.compile(
                    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
                    r'(?P<level>\w+):(?P<module>\S*):(?P<message>.*)$'
                ),
                'time_format': '%Y-%m-%d %H:%M:%S',
                'service': 'python'
            },
            {
                'name': 'java_logback',
                'pattern': re.compile(
                    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) '
                    r'\[(?P<thread>[^\]]+)\] (?P<level>\w+) '
                    r'(?P<module>\S+) - (?P<message>.*)$'
                ),
                'time_format': '%Y-%m-%d %H:%M:%S.%f',
                'service': 'java'
            },
            {
                'name': 'tomcat_access',
                'pattern': re.compile(
                    r'^(?P<host>\S+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
                    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
                    r'(?P<status>\d+) (?P<size>\S+)$'
                ),
                'time_format': '%d/%b/%Y:%H:%M:%S %z',
                'service': 'tomcat'
            },
            {
                'name': 'docker_json',
                'pattern': re.compile(
                    r'^\{.*"time":"(?P<timestamp>[^"]+)".*"log":"(?P<message>[^"]+)".*\}$'
                ),
                'time_format': None,
                'service': 'docker'
            },
            {
                'name': 'json_generic',
                'pattern': None,
                'type': 'json',
                'service': 'json'
            },
            {
                'name': 'simple_timestamp',
                'pattern': re.compile(
                    r'^\[(?P<timestamp>[^\]]+)\]\s*(?P<level>\w+)?\s*(?P<message>.*)$'
                ),
                'time_format': None,
                'service': 'generic'
            }
        ]
    
    def load_custom_rules(self, rules: List[Dict]):
        """
        加载自定义解析规则
        
        Args:
            rules: 自定义规则列表，每个规则包含pattern、time_format等字段
        """
        self._custom_rules = []
        
        for rule in rules:
            try:
                custom_rule = {
                    'name': rule.get('name', 'custom'),
                    'pattern': re.compile(rule['pattern']),
                    'time_format': rule.get('time_format'),
                    'service': rule.get('service', 'custom'),
                    'priority': rule.get('priority', 0)
                }
                self._custom_rules.append(custom_rule)
            except Exception as e:
                print(f"加载自定义规则失败: {e}")
    
    def parse(self, log_line: str) -> Dict:
        """
        解析日志行
        
        Args:
            log_line: 原始日志行
        
        Returns:
            解析后的日志数据字典
        """
        log_line = log_line.strip()
        if not log_line:
            return self._create_default_result(log_line)
        
        all_rules = self._custom_rules + self.patterns
        
        for rule in all_rules:
            if rule.get('type') == 'json':
                result = self._try_parse_json(log_line)
                if result:
                    return result
            else:
                pattern = rule.get('pattern')
                if pattern:
                    match = pattern.match(log_line)
                    if match:
                        return self._extract_from_match(match, rule, log_line)
        
        return self._create_default_result(log_line)
    
    def _try_parse_json(self, log_line: str) -> Optional[Dict]:
        """
        尝试将日志行解析为JSON格式
        
        Args:
            log_line: 原始日志行
        
        Returns:
            解析结果或None
        """
        try:
            data = json.loads(log_line)
            if not isinstance(data, dict):
                return None
            
            result = {
                'message': log_line,
                'raw_data': log_line,
                'parsed': True,
                'service_name': 'json'
            }
            
            for key in ['timestamp', 'time', '@timestamp', 'datetime']:
                if key in data:
                    timestamp = self._parse_time(str(data[key]), None)
                    if timestamp:
                        result['timestamp'] = timestamp
                    break
            
            for key in ['level', 'log_level', 'severity', 'loglevel']:
                if key in data:
                    level = str(data[key]).upper()
                    for std_level in LOG_LEVELS:
                        if std_level in level:
                            result['level'] = std_level
                            break
                    if 'level' not in result:
                        result['level'] = level
                    break
            
            for key in ['module', 'logger', 'source', 'component', 'tag']:
                if key in data:
                    result['module'] = str(data[key])
                    break
            
            for key in ['message', 'msg', 'log', 'content', 'text']:
                if key in data:
                    result['message'] = str(data[key])
                    break
            
            for key in ['service', 'service_name', 'app', 'application']:
                if key in data:
                    result['service_name'] = str(data[key])
                    break
            
            for key in ['host', 'hostname', 'server']:
                if key in data:
                    result['host'] = str(data[key])
                    break
            
            for key in ['trace_id', 'traceid', 'request_id', 'reqid']:
                if key in data:
                    result['trace_id'] = str(data[key])
                    break
            
            return result
        except Exception:
            return None
    
    def _extract_from_match(self, match: re.Match, rule: Dict, log_line: str) -> Dict:
        """
        从正则匹配中提取字段
        
        Args:
            match: 正则匹配对象
            rule: 规则信息
            log_line: 原始日志行
        
        Returns:
            解析结果字典
        """
        groups = match.groupdict()
        
        result = {
            'message': log_line,
            'raw_data': log_line,
            'parsed': True,
            'service_name': rule.get('service', 'generic')
        }
        
        if 'timestamp' in groups:
            timestamp_str = groups['timestamp']
            time_format = rule.get('time_format')
            timestamp = self._parse_time(timestamp_str, time_format)
            if timestamp:
                result['timestamp'] = timestamp
        
        if 'level' in groups:
            level = groups['level'].upper()
            for std_level in LOG_LEVELS:
                if std_level in level:
                    result['level'] = std_level
                    break
            if 'level' not in result:
                result['level'] = 'INFO'
        
        if 'module' in groups:
            result['module'] = groups['module']
        elif 'name' in groups:
            result['module'] = groups['name']
        
        if 'message' in groups:
            result['message'] = groups['message']
        
        if 'host' in groups:
            result['host'] = groups['host']
        
        if 'path' in groups and 'method' in groups:
            result['message'] = f"{groups['method']} {groups['path']} {result.get('message', '')}"
        
        if 'status' in groups:
            status = groups['status']
            if status.isdigit():
                status_code = int(status)
                if status_code >= 500:
                    result['level'] = 'ERROR'
                elif status_code >= 400:
                    result['level'] = 'WARNING'
        
        return result
    
    def _parse_time(self, time_str: str, time_format: Optional[str]) -> Optional[datetime]:
        """
        解析时间字符串
        
        Args:
            time_str: 时间字符串
            time_format: 时间格式（可选）
        
        Returns:
            datetime对象或None
        """
        if time_format:
            try:
                return datetime.strptime(time_str, time_format)
            except Exception:
                pass
        
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S,%f',
            '%Y-%m-%d %H:%M:%S.%f',
            '%d/%b/%Y:%H:%M:%S %z',
            '%Y/%m/%d %H:%M:%S',
            '%Y.%m.%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except Exception:
                continue
        
        try:
            from dateutil import parser
            return parser.parse(time_str)
        except Exception:
            pass
        
        return None
    
    def _create_default_result(self, log_line: str) -> Dict:
        """
        创建默认的解析结果
        
        Args:
            log_line: 原始日志行
        
        Returns:
            解析结果字典
        """
        level = 'INFO'
        upper_line = log_line.upper()
        for std_level in LOG_LEVELS:
            if std_level in upper_line:
                level = std_level
                break
        
        return {
            'timestamp': None,
            'level': level,
            'module': None,
            'message': log_line,
            'raw_data': log_line,
            'parsed': False,
            'service_name': 'unknown'
        }
    
    def detect_format(self, log_line: str) -> Optional[str]:
        """
        检测日志格式
        
        Args:
            log_line: 原始日志行
        
        Returns:
            检测到的格式名称或None
        """
        all_rules = self._custom_rules + self.patterns
        
        for rule in all_rules:
            if rule.get('type') == 'json':
                try:
                    json.loads(log_line)
                    return 'json_generic'
                except Exception:
                    continue
            else:
                pattern = rule.get('pattern')
                if pattern and pattern.match(log_line):
                    return rule.get('name')
        
        return None
