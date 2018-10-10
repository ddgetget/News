# author        TuringEmmy 
# createtime    18-10-8  下午8:04
# coding=utf-8
# doc           PyCharm
from . import news
from flask import session, render_template, current_app,jsonify
from app.models import User,Category

from app.static.util.response_code import RET

@news.route('/')
def index():
    """
    项目首页：首页哟右上角的用户的信心展示
    :return:
    """
    user_id = session.get('user_id')
    # 如果user_id存在，查询数据哭
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 创建分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA,errmsg='擦讯查询分类数据失败')

    category_list=[]
    if not categories:
        return jsonify(erron=RET.NODATA,errmsg='无新闻分类数据')

    # 遍历查询结果
    for category in categories:
        category_list.append(category.to_dict())


    # 定义字典数据，返回模板
    data = {
        'user_info': user.to_dict() if user else None
    }
    return render_template("news/index.html", data=data)


# 项目加载logo图标
@news.route('/favicon.ico')
def favico():
    """第一次一页有可能不成功"""
    # 1. 清除浏览器浏览信息和缓存
    # 2. 让浏览器车德系退出，重新启动
    # 3. 重新打开浏览器会有logo
    return current_app.send_static_file("news/favicon.ico")


