# author        TuringEmmy 
# createtime    18-10-8  下午6:27
# coding=utf-8
# doc           PyCharm

from flask import Blueprint
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# 导入Confie类,导入字典
from config import Config,config_dict
from flask_session import Session

# 导入日志
import logging
# 创建日志记录其，日志等级，输入日志等级和个数，大小。保存日志文件个数上限
from logging.handlers import RotatingFileHandler
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

# 先实例化sqlqlchemy程序实例
db = SQLAlchemy()

def create_app(config__name):
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config_dict[config__name])
    db.init_app(app)
    Session(app)
    return app
