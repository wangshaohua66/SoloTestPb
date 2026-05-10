# -*- coding: utf-8 -*-
"""
应用启动入口文件
启动Flask开发服务器
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app('development')

if __name__ == '__main__':
    print('=' * 60)
    print('       文物修复记录系统 - 后端服务')
    print('=' * 60)
    print(f'服务地址: http://127.0.0.1:5002')
    print(f'API文档:  http://127.0.0.1:5002/')
    print('=' * 60)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
