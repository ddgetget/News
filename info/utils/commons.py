# 自定义过滤器
from flask import session, current_app, g

from info.models import User


def index_filter(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return ''


import functools


# 装饰器：本质是闭包，函数嵌套，作用：不改变原有代码的前提下，添加新的功能。
def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 从redis中获取user_id
        user_id = session.get('user_id')
        # 如果user_id存在,查询mysql
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 使用应用上下文对象g，用来在请求过程中来存储临时数据。
        g.user = user
        return f(*args, **kwargs)

    # 在返回内部函数前，让被装饰器装饰的函数名重新赋值给内部函数。
    # wrapper.__name__ = f.__name__
    return wrapper
