from flask import current_app, jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
# 导入程序实例,把模型类导入到启动文件中
from info import create_app, db, models

# 调用工厂函数，获取程序实例app
from info.models import User
from info.utils.response_code import RET

app = create_app('development')

# 实例化管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app, db)
# 添加迁移命令给管理器
manage.add_command('db', MigrateCommand)


# ---------------创建管理员-------------
@manage.option('-n', '-name', dest='name')
@manage.option('-p', '-password', dest='password')
def createsupperuser(name, password):
    """
    创建管理员用户
    :param name:
    :param password:
    :return:
    """
    if not all([name, password]):
        print('参数不足')
        return

    # 拼凑数据库模型的字段
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')


if __name__ == '__main__':
    print(app.url_map)
    manage.run()
