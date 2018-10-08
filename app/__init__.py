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

# 先实例化sqlqlchemy程序实例
db = SQLAlchemy()

def create_app(config__name):
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config_dict[config__name])
    db.init_app(app)
    Session(app)
    return app
