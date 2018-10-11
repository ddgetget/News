# author        TuringEmmy 
# createtime    18-10-8  下午8:04
# coding=utf-8
# doc           PyCharm
from . import news
from flask import session, render_template, current_app, jsonify, request, g
from app.models import User, Category, News

from app.static.util.response_code import RET
from app.static.util.comments import login_required

from app.constants import *


from app import db

@news.route('/')
@login_required
def index():
    """
    项目首页：首页哟右上角的用户的信心展示
    :return:
    """
    # user_id = session.get('user_id')
    # # 如果user_id存在，查询数据哭
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # ----------------------使用g的装饰器----------------
    user = g.user
    # -------------------------使用g的装饰器-------------

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


# 新闻详情页面
@news.route('/<int:news_id>')
@login_required
def get_news_detail(news_id):
    """
    新闻详情页面
    :param news_id:
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

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻排行数据失败')
        # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.DBERR, errmsg='无新闻排行数据')
        # 定义容器，用来存储新闻点击排行的数据
    news_click_list = []
    # 遍历新闻数据
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 新闻详情数据展示
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻详情数据失败')
    # 判断查询结果,如果没有新闻数据直接结束程序运行
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='无新闻详情数据')

    # 关于收藏按钮的
    is_collected = False
    if user and not user.collection_news:
        is_collected = True

    # 定义字典数据，返回模板
    data = {
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'news_detail': news.to_dict(),
        'is_collected': is_collected
    }

    return render_template('news/detail.html', data=data)


# 新闻收藏和取消收藏
@news.route('/news_collect', methods=["POST"])
@login_required
def news_collect():
    user = g.user

    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 数据转化
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 检查是否收藏
    if action not in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 根据new_id来查询mysql数据库,确认新闻得打存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="查询新闻收据失败")

    # 如果没有新闻
    if not news:
        return jsonify(errno=RET.NODATA, errmsg='无新闻数据')

    if action == 'collect':
        # 该新闻没有用户收藏过
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    # 保存到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")

    return jsonify(errno=RET.OK, errmsg='ok')


# 项目加载logo图标
@news.route('/favicon.ico')
def favico():
    """第一次一页有可能不成功"""
    # 1. 清除浏览器浏览信息和缓存
    # 2. 让浏览器车德系退出，重新启动
    # 3. 重新打开浏览器会有logo
    return current_app.send_static_file("news/favicon.ico")
