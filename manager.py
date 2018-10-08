# author        TuringEmmy 
# createtime    18-10-8  下午12:17
# coding=utf-8
# doc           PyCharm

from flask import session
from config import Config
from flask_script import Manager
# 用于数据迁移
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

# 调用工厂模式实例app
app = create_app('develpoment')
manage = Manager(app)

# 使用迁移框架
Migrate(app, db)
# 添加迁移命令给管理器
manage.add_command("db", MigrateCommand)


@app.route('/index')
def index():
    session['user'] = 'turingemmy'
    return "turing emmy is ok"


if __name__ == '__main__':
    # app.run()
    manage.run()
