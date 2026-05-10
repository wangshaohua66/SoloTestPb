"""
书法字体识别器后端应用初始化模块
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from app import routes
