from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# 导入程序实例,把模型类导入到启动文件中
from info import create_app,db,models


# 调用工厂函数，获取程序实例app
app = create_app('development')

# 实例化管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令给管理器
manage.add_command('db',MigrateCommand)




if __name__ == '__main__':
    print(app.url_map)
    manage.run()