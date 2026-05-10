"""
书法字体识别器后端服务启动入口
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from app import app

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("书法字体识别器后端服务启动")
    logger.info(f"服务端口: 5003")
    logger.info(f"日志文件: {LOG_FILE}")
    logger.info("=" * 50)

    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True
    )
