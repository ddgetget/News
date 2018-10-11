# author        TuringEmmy 
# createtime    18-10-8  下午8:04
# coding=utf-8
# doc           PyCharm
from . import news
from flask import session, render_template, current_app, jsonify, request
from app.models import User, Category, News

from app.static.util.response_code import RET

from app.constants import *


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
        return jsonify(errno=RET.NODATA, errmsg='擦讯查询分类数据失败')

    category_list = []
    if not categories:
        return jsonify(erron=RET.NODATA, errmsg='无新闻分类数据')

    # 遍历查询结果
    for category in categories:
        category_list.append(category.to_dict())

    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻点击排行数据失败')

    # 定义容器
    news_click_list = []
    for news in news_list:
        news_click_list.append(news)

    # 判断数据查询结果
    if not news:
        return jsonify(errno=RET.DBERR, errmsg='无新闻排行')

    # 定义字典数据，返回模板
    data = {
        'user_info': user.to_dict() if user else None,
        'category_list': category_list,
        'news_click_list': news_click_list
    }
    return render_template("news/index.html", data=data)



# 首页新文列表
@news.route('/news_list')
def get_news_list():
    cid = request.args.get('cid', "1")
    page = request.args.get('page', "1")
    per_page = request.args.get('per_page', "10")

    # 检查参数的数据类型
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR, errmsg='参数类型错误')

    # 根据类型查询数据
    filters = []
    if cid > 1:
        filters.append(News.category_id == cid)

    # 根据新闻分类查询
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻列表数据失败')

    # 对分页对象获取分页后的数据
    new_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    # 遍历新闻列表
    news_dict_list = []
    for news in new_list:
        news_dict_list.append(news.to_dict())

    # 返回数据
    data = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    return jsonify(errno=RET.OK, errmsg='OK', data=data)


# 项目加载logo图标
@news.route('/favicon.ico')
def favico():
    """第一次一页有可能不成功"""
    # 1. 清除浏览器浏览信息和缓存
    # 2. 让浏览器车德系退出，重新启动
    # 3. 重新打开浏览器会有logo
    return current_app.send_static_file("news/favicon.ico")
