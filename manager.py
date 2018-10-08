# author        TuringEmmy 
# createtime    18-10-8  下午12:17
# coding=utf-8
# doc           PyCharm

from flask import Flask, session
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_session import Session

# 用于数据迁移
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
# session的设置将数据保存到redis的数据库当中

db = SQLAlchemy(app)
# 加载shiulihua管理器对象

app.config.from_object(Config)
manage = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令给管理器
manage.add_command("db",MigrateCommand)

rb = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

Session(app)


@app.route('/index')
def index():
    session['user'] = 'turingemmy'
    return "turing emmy is ok"


if __name__ == '__main__':
    # app.run()
    manage.run()
