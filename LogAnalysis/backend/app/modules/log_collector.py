# -*- coding: utf-8 -*-
"""
日志收集模块
支持从文件、标准输出、网络端口等多种来源收集日志
"""
import re
import json
import os
import socket
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable

from .. import db
from ..models import LogEntry, LogSource
from .log_parser import LogParser


class FileLogCollector:
    """
    文件日志收集器
    监听指定文件，实时收集新增的日志行
    """
    
    def __init__(self, file_path: str, on_log_received: Callable[[dict], None]):
        """
        初始化文件日志收集器
        
        Args:
            file_path: 日志文件路径
            on_log_received: 收到日志时的回调函数
        """
        self.file_path = file_path
        self.on_log_received = on_log_received
        self.running = False
        self.thread = None
        self.parser = LogParser()
    
    def start(self):
        """
        启动文件监听
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"日志文件不存在: {self.file_path}")
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_file, daemon=True)
        self.thread.start()
    
    def stop(self):
        """
        停止文件监听
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _watch_file(self):
        """
        监听文件变化
        """
        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                if line:
                    line = line.strip()
                    if line:
                        self._process_line(line)
                else:
                    time.sleep(1)
    
    def _process_line(self, line: str):
        """
        处理读取到的日志行
        
        Args:
            line: 日志行内容
        """
        parsed = self.parser.parse(line)
        parsed['raw_data'] = line
        parsed['source_type'] = 'file'
        parsed['source_config'] = json.dumps({'file_path': self.file_path})
        self.on_log_received(parsed)


class NetworkLogCollector:
    """
    网络日志收集器
    通过TCP/UDP端口接收日志数据
    """
    
    def __init__(self, host: str, port: int, protocol: str = 'tcp', 
                 on_log_received: Callable[[dict], None] = None):
        """
        初始化网络日志收集器
        
        Args:
            host: 监听地址
            port: 监听端口
            protocol: 协议类型（tcp/udp）
            on_log_received: 收到日志时的回调函数
        """
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.on_log_received = on_log_received
        self.running = False
        self.server_socket = None
        self.thread = None
        self.parser = LogParser()
    
    def start(self):
        """
        启动网络监听
        """
        self.running = True
        
        if self.protocol == 'tcp':
            self.thread = threading.Thread(target=self._tcp_server, daemon=True)
        else:
            self.thread = threading.Thread(target=self._udp_server, daemon=True)
        
        self.thread.start()
    
    def stop(self):
        """
        停止网络监听
        """
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        if self.thread:
            self.thread.join(timeout=2)
    
    def _tcp_server(self):
        """
        TCP服务端
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.server_socket.settimeout(1)
        
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_tcp_client,
                    args=(client_socket, addr),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception:
                if self.running:
                    time.sleep(1)
    
    def _handle_tcp_client(self, client_socket: socket.socket, addr: tuple):
        """
        处理TCP客户端连接
        
        Args:
            client_socket: 客户端Socket
            addr: 客户端地址
        """
        buffer = ''
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data.decode('utf-8', errors='ignore')
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self._process_line(line, addr)
        except Exception:
            pass
        finally:
            client_socket.close()
    
    def _udp_server(self):
        """
        UDP服务端
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.settimeout(1)
        
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                lines = data.decode('utf-8', errors='ignore').split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        self._process_line(line, addr)
            except socket.timeout:
                continue
            except Exception:
                if self.running:
                    time.sleep(1)
    
    def _process_line(self, line: str, addr: tuple = None):
        """
        处理接收到的日志行
        
        Args:
            line: 日志行内容
            addr: 来源地址
        """
        parsed = self.parser.parse(line)
        parsed['raw_data'] = line
        parsed['source_type'] = 'network'
        parsed['source_config'] = json.dumps({
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'remote_addr': str(addr) if addr else None
        })
        if self.on_log_received:
            self.on_log_received(parsed)


class LogCollectorManager:
    """
    日志收集管理器
    管理多个日志收集器，提供统一的日志收集接口
    """
    
    def __init__(self):
        """
        初始化收集管理器
        """
        self.collectors: Dict[str, object] = {}
        self._lock = threading.Lock()
        self._app = None
    
    def set_app(self, app):
        """
        设置Flask应用实例，用于在后台线程中使用
        
        Args:
            app: Flask应用实例
        """
        self._app = app
    
    def start_file_collector(self, source_id: str, file_path: str) -> bool:
        """
        启动文件日志收集器
        
        Args:
            source_id: 来源标识
            file_path: 日志文件路径
        
        Returns:
            是否启动成功
        """
        with self._lock:
            if source_id in self.collectors:
                return False
            
            try:
                collector = FileLogCollector(file_path, self._on_log_received)
                collector.start()
                self.collectors[source_id] = collector
                return True
            except Exception as e:
                print(f"启动文件收集器失败: {e}")
                return False
    
    def start_network_collector(self, source_id: str, host: str, port: int, 
                                 protocol: str = 'tcp') -> bool:
        """
        启动网络日志收集器
        
        Args:
            source_id: 来源标识
            host: 监听地址
            port: 监听端口
            protocol: 协议类型
        
        Returns:
            是否启动成功
        """
        with self._lock:
            if source_id in self.collectors:
                return False
            
            try:
                collector = NetworkLogCollector(host, port, protocol, self._on_log_received)
                collector.start()
                self.collectors[source_id] = collector
                return True
            except Exception as e:
                print(f"启动网络收集器失败: {e}")
                return False
    
    def stop_collector(self, source_id: str) -> bool:
        """
        停止指定的收集器
        
        Args:
            source_id: 来源标识
        
        Returns:
            是否停止成功
        """
        with self._lock:
            if source_id not in self.collectors:
                return False
            
            try:
                collector = self.collectors.pop(source_id)
                collector.stop()
                return True
            except Exception as e:
                print(f"停止收集器失败: {e}")
                return False
    
    def stop_all(self):
        """
        停止所有收集器
        """
        with self._lock:
            for source_id in list(self.collectors.keys()):
                try:
                    self.collectors[source_id].stop()
                except Exception:
                    pass
            self.collectors.clear()
    
    def _on_log_received(self, log_data: dict):
        """
        收到日志时的回调
        
        Args:
            log_data: 解析后的日志数据
        """
        try:
            self._save_log(log_data)
        except Exception as e:
            print(f"保存日志失败: {e}")
    
    def _save_log(self, log_data: dict):
        """
        保存日志到数据库
        
        Args:
            log_data: 日志数据
        """
        if self._app:
            with self._app.app_context():
                self._do_save_log(log_data)
        else:
            from flask import current_app
            try:
                with current_app.app_context():
                    self._do_save_log(log_data)
            except RuntimeError as e:
                print(f"保存日志失败（无应用上下文）: {e}")
    
    def _do_save_log(self, log_data: dict):
        """
        执行实际的日志保存
        
        Args:
            log_data: 日志数据
        """
        entry = LogEntry(
            timestamp=log_data.get('timestamp') or datetime.utcnow(),
            level=log_data.get('level', 'INFO'),
            module=log_data.get('module'),
            message=log_data.get('message', ''),
            service_name=log_data.get('service_name'),
            host=log_data.get('host'),
            trace_id=log_data.get('trace_id'),
            raw_data=log_data.get('raw_data'),
            parsed=log_data.get('parsed', True)
        )
        
        db.session.add(entry)
        db.session.commit()


collector_manager = LogCollectorManager()
