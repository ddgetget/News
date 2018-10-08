# author        TuringEmmy 
# createtime    18-10-8  下午5:36
# coding=utf-8
# doc           PyCharm

from redis import StrictRedis

class Config(object):
    """project config information"""
    DEBUG = True
    # 设置密钥
    SECRET_KEY='legeyungriueingemmyturingemmyturingemmy'

    # ----------------------------------mysql的数据库的配置信息------------------------------------
    SQLALCHEMY_DATABASE_URI='mysql://root：mysql@localhost/news'
    SQLALCHEMY_TRACK_MODIFICATIONS=True

    # 配置状态保持当中的session信息存储的位置redis
    SESSION_TYPE='redis'
    SESSION_REDIS=StrictRedis(host='127.0.0.1',port=6379)
    SESSION_USE_SINGER=True
    PERMANENT_SESSION_LIFETIME=86400