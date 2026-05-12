"""
数据库操作模块
使用SQLite本地文件数据库存储识别历史记录
"""

import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'font_identifier.db')


class Database:
    """
    数据库操作类
    封装SQLite数据库的基本操作
    """

    def __init__(self, db_path=None):
        """
        初始化数据库连接
        
        参数:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or DB_PATH
        self._ensure_db_directory()
        self._init_database()

    def _ensure_db_directory(self):
        """
        确保数据库目录存在
        """
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"创建数据库目录: {db_dir}")

    def _init_database(self):
        """
        初始化数据库表结构
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recognition_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                recognized_font TEXT NOT NULL,
                confidence REAL NOT NULL,
                result_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fonts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                english_name TEXT,
                description TEXT,
                history TEXT,
                stroke_features TEXT,
                structure_features TEXT,
                style_features TEXT,
                representative_works TEXT,
                key_characteristics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_recognition_history_created 
            ON recognition_history(created_at)
        ''')

        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")

    def get_connection(self):
        """
        获取数据库连接
        
        返回:
            SQLite连接对象
        """
        return sqlite3.connect(self.db_path)

    def add_recognition(self, input_text, recognized_font, confidence, result_json=None):
        """
        添加识别记录
        
        参数:
            input_text: 用户输入的文本
            recognized_font: 识别出的字体名称
            confidence: 置信度
            result_json: 完整结果的JSON字符串
            
        返回:
            新记录的ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO recognition_history 
            (input_text, recognized_font, confidence, result_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (input_text, recognized_font, confidence, result_json, datetime.now()))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"添加识别记录: ID={record_id}, 字体={recognized_font}")
        return record_id

    def get_recognition_history(self, limit=50, offset=0):
        """
        获取识别历史记录
        
        参数:
            limit: 返回记录数限制
            offset: 偏移量
            
        返回:
            历史记录列表
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM recognition_history 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'input_text': row['input_text'],
                'recognized_font': row['recognized_font'],
                'confidence': row['confidence'],
                'result_json': row['result_json'],
                'created_at': row['created_at']
            })

        return history

    def get_recognition_by_id(self, record_id):
        """
        根据ID获取识别记录
        
        参数:
            record_id: 记录ID
            
        返回:
            记录字典，不存在返回None
        """
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM recognition_history WHERE id = ?
        ''', (record_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'input_text': row['input_text'],
                'recognized_font': row['recognized_font'],
                'confidence': row['confidence'],
                'result_json': row['result_json'],
                'created_at': row['created_at']
            }
        return None

    def get_recognition_count(self):
        """
        获取识别记录总数
        
        返回:
            记录总数
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM recognition_history')
        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_font_recognition_stats(self):
        """
        获取各字体识别统计
        
        返回:
            字体统计字典
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT recognized_font, COUNT(*) as count, AVG(confidence) as avg_confidence
            FROM recognition_history 
            GROUP BY recognized_font
            ORDER BY count DESC
        ''')

        rows = cursor.fetchall()
        conn.close()

        stats = []
        for row in rows:
            stats.append({
                'font': row[0],
                'count': row[1],
                'avg_confidence': round(row[2], 2) if row[2] else 0
            })

        return stats


def get_database():
    """
    获取数据库实例（单例模式）
    
    返回:
        Database实例
    """
    return Database()
