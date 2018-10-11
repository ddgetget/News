# author        TuringEmmy 
# createtime    18-10-11  上午12:13
# coding=utf-8
# doc           PyCharm
from flask import session, current_app, g
from app.models import User

# 自定义过滤器
def index_filter(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return


from functools import wraps
# 本质上是一个装饰器，闭包，函数嵌套
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 从redis当中获取user_id
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 使用应用上下文g,用来请求过程中来存储的临时数据
        # g对象的属性
        g.user = user
        return f(*args, **kwargs)
    # 在返回内部函数，让装饰器的函数名重新赋值给内部函数
    # wrapper.__name__=f.__name__
    return wrapper
