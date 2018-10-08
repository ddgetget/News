# author        TuringEmmy 
# createtime    18-10-8  下午12:17
# coding=utf-8
# doc           PyCharm

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# 创建redise数据库
import redis
# 开启csrf
from flask_wtf.csrf import CSRFProtect
# session的设置将数据保存到redis的数据库当中
from flask_session import Session


app = Flask(__name__)


class Config(object):
    """project config information"""
    DEBUG = True
    # mysql数据哭的配置信息
    SQLAlchemy_DATABASE_URI = "mysql://root:mysql@localhost:3306/news"
    CHEMY_TRACE_MODIFICATIONS = False
    # redis数据哭的配置
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379
    CSRFProtect(app)
    # 指定session保存到redis当中
    SESSION_TYPE='redis'
    # 使cookie的session_id加密签名处理
    SESSION_USE_SIGNER=True
    # 设置session的有效期
    PERMANENT_SESSION_LIFETIME=86400

app.config.from_object(Config)
db = SQLAlchemy(app)
rb=redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
Session(app)


@app.route('/index')
def index():
    return "index"


if __name__ == '__main__':
    app.run()
