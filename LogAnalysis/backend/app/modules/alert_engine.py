# -*- coding: utf-8 -*-
"""
异常告警模块
根据规则检测异常日志，触发告警通知
"""
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from sqlalchemy import and_

from .. import db
from ..models import LogEntry, AlertRule, Alert


class AlertEngine:
    """
    告警引擎
    检测异常日志并触发告警
    """
    
    def __init__(self):
        """
        初始化告警引擎
        """
        self._running = False
        self._check_thread = None
        self._alert_handlers: List[Callable[[Alert], None]] = []
        self._app = None
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """
        添加告警处理器
        
        Args:
            handler: 告警处理回调函数
        """
        self._alert_handlers.append(handler)
    
    def start(self, check_interval: int = 30, app=None):
        """
        启动告警检测
        
        Args:
            check_interval: 检查间隔（秒）
            app: Flask应用实例（用于在后台线程中使用
        """
        if self._running:
            return
        
        if app:
            self._app = app
        
        self._running = True
        self._check_thread = threading.Thread(
            target=self._check_loop,
            args=(check_interval,),
            daemon=True
        )
        self._check_thread.start()
    
    def stop(self):
        """
        停止告警检测
        """
        self._running = False
        if self._check_thread:
            self._check_thread.join(timeout=5)
    
    def _check_loop(self, interval: int):
        """
        检测循环
        
        Args:
            interval: 检查间隔（秒）
        """
        while self._running:
            try:
                self._check_all_rules()
            except Exception as e:
                print(f"告警检测异常: {e}")
            
            time.sleep(interval)
    
    def _check_all_rules(self):
        """
        检查所有激活的告警规则
        """
        if self._app:
            with self._app.app_context():
                self._do_check_all_rules()
        else:
            from flask import current_app
            try:
                with current_app.app_context():
                    self._do_check_all_rules()
            except RuntimeError:
                pass
    
    def _do_check_all_rules(self):
        """
        执行实际的规则检查
        """
        rules = AlertRule.query.filter_by(is_active=True).all()
        
        for rule in rules:
            try:
                should_check = self._should_check_rule(rule)
                if should_check:
                    self._check_single_rule(rule)
                    rule.last_checked_at = datetime.utcnow()
                    db.session.commit()
            except Exception as e:
                print(f"检查规则 {rule.name} 失败: {e}")
                db.session.rollback()
    
    def _should_check_rule(self, rule: AlertRule) -> bool:
        """
        判断是否应该检查规则
        
        Args:
            rule: 告警规则
        
        Returns:
            是否需要检查
        """
        if not rule.last_checked_at:
            return True
        
        elapsed = (datetime.utcnow() - rule.last_checked_at).total_seconds()
        return elapsed >= rule.check_interval
    
    def _check_single_rule(self, rule: AlertRule):
        """
        检查单个规则是否触发告警
        
        Args:
            rule: 告警规则
        """
        condition = json.loads(rule.condition_value)
        triggered = False
        matched_logs = []
        
        if rule.condition_type == 'keyword':
            triggered, matched_logs = self._check_keyword_condition(condition)
        elif rule.condition_type == 'level_threshold':
            triggered, matched_logs = self._check_level_threshold(condition)
        elif rule.condition_type == 'error_rate':
            triggered, matched_logs = self._check_error_rate(condition)
        elif rule.condition_type == 'custom_query':
            triggered, matched_logs = self._check_custom_query(condition)
        
        if triggered:
            self._trigger_alert(rule, matched_logs)
    
    def _check_keyword_condition(self, condition: Dict) -> tuple:
        """
        检查关键词条件
        
        Args:
            condition: 条件配置
        
        Returns:
            (是否触发, 匹配的日志列表)
        """
        keywords = condition.get('keywords', [])
        time_window = condition.get('time_window_minutes', 5)
        threshold = condition.get('threshold', 1)
        
        start_time = datetime.utcnow() - timedelta(minutes=time_window)
        
        query = LogEntry.query.filter(
            LogEntry.timestamp >= start_time
        )
        
        from sqlalchemy import or_
        keyword_filters = []
        for keyword in keywords:
            keyword_filters.append(LogEntry.message.like(f'%{keyword}%'))
        
        if keyword_filters:
            query = query.filter(or_(*keyword_filters))
        
        matched_logs = query.order_by(LogEntry.timestamp.desc()).limit(100).all()
        
        triggered = len(matched_logs) >= threshold
        
        return triggered, [log.to_dict() for log in matched_logs[:10]]
    
    def _check_level_threshold(self, condition: Dict) -> tuple:
        """
        检查日志级别阈值条件
        
        Args:
            condition: 条件配置
        
        Returns:
            (是否触发, 匹配的日志列表)
        """
        level = condition.get('level', 'ERROR')
        time_window = condition.get('time_window_minutes', 5)
        threshold = condition.get('threshold', 10)
        
        start_time = datetime.utcnow() - timedelta(minutes=time_window)
        
        matched_logs = LogEntry.query.filter(
            LogEntry.timestamp >= start_time,
            LogEntry.level == level
        ).order_by(
            LogEntry.timestamp.desc()
        ).limit(100).all()
        
        triggered = len(matched_logs) >= threshold
        
        return triggered, [log.to_dict() for log in matched_logs[:10]]
    
    def _check_error_rate(self, condition: Dict) -> tuple:
        """
        检查错误率条件
        
        Args:
            condition: 条件配置
        
        Returns:
            (是否触发, 匹配的日志列表)
        """
        rate_threshold = condition.get('rate_threshold') or condition.get('threshold', 5.0)
        time_window = condition.get('time_window_minutes', 5)
        min_total = condition.get('min_total_logs', 5)
        
        from .log_aggregator import log_aggregator
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=time_window)
        
        error_rate = log_aggregator.calculate_error_rate(start_time, end_time)
        
        matched_logs = LogEntry.query.filter(
            LogEntry.timestamp >= start_time,
            LogEntry.level.in_(['ERROR', 'FATAL', 'ERR'])
        ).order_by(
            LogEntry.timestamp.desc()
        ).limit(10).all()
        
        total_logs = LogEntry.query.filter(
            LogEntry.timestamp >= start_time
        ).count()
        
        triggered = error_rate >= rate_threshold and total_logs >= min_total
        
        return triggered, [log.to_dict() for log in matched_logs]
    
    def _check_custom_query(self, condition: Dict) -> tuple:
        """
        检查自定义查询条件
        
        Args:
            condition: 条件配置
        
        Returns:
            (是否触发, 匹配的日志列表)
        """
        keyword = condition.get('keyword') or condition.get('query', '')
        time_window = condition.get('time_window_minutes', 5)
        threshold = condition.get('threshold', 1)
        
        start_time = datetime.utcnow() - timedelta(minutes=time_window)
        
        query = LogEntry.query.filter(
            LogEntry.timestamp >= start_time
        )
        
        if keyword:
            query = query.filter(LogEntry.message.like(f'%{keyword}%'))
        
        if condition.get('level'):
            query = query.filter(LogEntry.level == condition['level'])
        
        if condition.get('service_name'):
            query = query.filter(LogEntry.service_name == condition['service_name'])
        
        matched_logs = query.order_by(
            LogEntry.timestamp.desc()
        ).limit(100).all()
        
        triggered = len(matched_logs) >= threshold
        
        return triggered, [log.to_dict() for log in matched_logs[:10]]
    
    def _trigger_alert(self, rule: AlertRule, matched_logs: List[Dict]):
        """
        触发告警
        
        Args:
            rule: 触发的告警规则
            matched_logs: 匹配的日志列表
        """
        existing_alert = Alert.query.filter(
            Alert.rule_id == rule.id,
            Alert.is_resolved == False
        ).first()
        
        if existing_alert:
            existing_alert.trigger_count += 1
            existing_alert.last_triggered_at = datetime.utcnow()
            existing_alert.logs = json.dumps(matched_logs, ensure_ascii=False)
            alert = existing_alert
        else:
            alert = Alert(
                rule_id=rule.id,
                title=rule.name,
                message=rule.description or f'告警规则 {rule.name} 已触发',
                level=rule.level,
                logs=json.dumps(matched_logs, ensure_ascii=False)
            )
            db.session.add(alert)
        
        db.session.commit()
        
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"告警处理器执行失败: {e}")
    
    def create_rule(self, name: str, condition_type: str, condition_value: Dict,
                    level: str = 'WARNING', description: str = None,
                    check_interval: int = 60, is_active: bool = True) -> AlertRule:
        """
        创建告警规则
        
        Args:
            name: 规则名称
            condition_type: 条件类型
            condition_value: 条件值（字典）
            level: 告警级别
            description: 规则描述
            check_interval: 检查间隔（秒）
            is_active: 是否激活
        
        Returns:
            创建的告警规则
        """
        rule = AlertRule(
            name=name,
            condition_type=condition_type,
            condition_value=json.dumps(condition_value, ensure_ascii=False),
            level=level,
            description=description,
            check_interval=check_interval,
            is_active=is_active
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return rule
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = 'system'):
        """
        确认告警
        
        Args:
            alert_id: 告警ID
            acknowledged_by: 确认人
        """
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            db.session.commit()
    
    def resolve_alert(self, alert_id: int, resolved_note: str = None):
        """
        解决告警
        
        Args:
            alert_id: 告警ID
            resolved_note: 解决说明
        """
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            alert.resolved_note = resolved_note
            db.session.commit()


alert_engine = AlertEngine()
