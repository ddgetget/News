from redis import StrictRedis

class Config:
    DEBUG = None
    # 设置密钥
    SECRET_KEY = 'HZ3b61ERsB6Qi8MfH4lgoBNPz4PQyomwvMKmN5yPQp8J4peIC8RZLZI2Rss9LFNV07w='

    # mysql数据库的配置链接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/news'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 定义redis连接配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 配置状态保持中的session信息存储的位置redis
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 86400

# 开发模式下的配置
class DevelopmentConfig(Config):
    DEBUG = True


# 生产模式下的配置
class ProductionConfig(Config):
    DEBUG = False

# 定义字典，实现配置对象的映射
config_dict = {
    'development':DevelopmentConfig,
    'production':ProductionConfig
}
