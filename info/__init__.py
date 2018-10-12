from flask import Flask
# 导入Config类，导入config_dict字典
from config import Config, config_dict
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
# 导入日志模块
import logging
# 日志处理模块，设置日志的位置、大小等信息
from logging.handlers import RotatingFileHandler
from redis import StrictRedis

# 先实例化sqlalchemy对象
db = SQLAlchemy()
# 实例化redis对象,用来实现存储和业务相关的数据
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

# 导入flask_wtf扩展提供的csrf保护和验证功能
from flask_wtf import CSRFProtect, csrf


# 定义工厂函数，实现动态的根据传入参数的不同，生产不同环境下的app
def create_app(config_name):
    app = Flask(__name__)

    # 加载配置对象,接收工厂函数传入的参数
    app.config.from_object(config_dict[config_name])

    # 使用函数让db和程序实例进行关联
    db.init_app(app)

    Session(app)
    # 项目开启csrf保护
    CSRFProtect(app)

    # 生成csrf_token,通过请求钩子，在每次请求后，往客户端浏览器的cookie中设置csrf_token
    @app.after_request
    def after_request(response):
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 添加自定义过滤器给模板
    from info.utils.commons import index_filter
    app.add_template_filter(index_filter, 'index_filter')

    # 导入蓝图对象
    from info.modules.news import news_blue
    # 注册蓝图对象
    app.register_blueprint(news_blue)

    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    from info.modules.profile import profile_blue
    app.register_blueprint(profile_blue)

    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    return app
