from flask import session, render_template, current_app, jsonify, request, g

from info import constants, db
from info.models import User, Category, News
from info.utils.response_code import RET
from . import news_blue
from info.utils.commons import login_required

# 使用模板加载项目首页
@news_blue.route('/')
@login_required
def index():
    """
    项目首页：
        首页右上角用户信息展示(检查用户登录状态)
        1、从redis中获取user_id,根据user_id查询mysql，获取用户信息

    :return:
    """
    # g.user = user
    user = g.user
    # 从redis中获取user_id
    # user_id = session.get('user_id')
    # # 如果user_id存在,查询mysql
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 新闻分类数据
    # 查询mysql中的新闻分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询分类数据失败')
    # 判断查询结果
    if not categories:
        return jsonify(errno=RET.NODATA,errmsg='无新闻分类数据')
    category_list = []
    # 遍历查询结果
    for category in categories:
        category_list.append(category.to_dict())

    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻排行数据失败')
    # 判断查询结果
    if not news_list:
        return jsonify(errno=RET.DBERR,errmsg='无新闻排行数据')
    # 定义容器，用来存储新闻点击排行的数据
    news_click_list = []
    # 遍历新闻数据
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 定义字典数据，返回模板
    data = {
        'user_info':user.to_dict() if user else None,
        'category_list':category_list,
        'news_click_list':news_click_list
    }

    return render_template('news/index.html',data=data)


@news_blue.route("/news_list")
def get_news_list():
    """
    首页新闻列表
    1、获取参数，cid新闻分类，page页数，per_page每页数据条数
    2、检查参数，把参数统一转换数据类型
    3、查询新闻数据，根据不同的新闻分类，查询不同的新闻数据
    paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
    4、判断查询结果
    5、获取分页后的新闻数据，新闻列表、总页数、当前页数
    6、返回数据

    :return:
    """
    # 获取参数
    cid = request.args.get('cid','1')
    page = request.args.get('page','1')
    per_page = request.args.get('per_page','10')
    # 检查参数的数据类型
    try:
        cid,page,per_page = int(cid),int(page),int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数类型错误')
    # 定义过滤条件
    filters = []
    # 如果新闻分类id不是最新
    if cid > 1:
        # 添加查询过滤条件，新闻分类和新闻相等
        filters.append(News.category_id == cid)

    # 根据新闻分类查询数据
    try:
        # 如果有分类：News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
        # 最新：News.query.filter().order_by(News.create_time.desc()).paginate(page,per_page,False)
        # *filters是python语法中拆包，返回的数据不是True和False，是sqlalchemy对象。
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻列表数据失败')
    # 使用分页对象获取分页后的新闻数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    # 遍历新闻列表，调用模型类中的to_dict方法，获取详细的新闻数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 返回数据
    data = {
        'news_dict_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    return jsonify(errno=RET.OK,errmsg='OK',data=data)

@news_blue.route('/<int:news_id>')
@login_required
def get_news_detail(news_id):
    """
    新闻详情数据
    :return:
    """
    user = g.user
    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
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
        return jsonify(errno=RET.DBERR,errmsg='查询新闻详情数据失败')
    # 判断查询结果,如果没有新闻数据直接结束程序运行
    if not news:
        return jsonify(errno=RET.NODATA,errmsg='无新闻详情数据')
    # 定义标记，用来前端判断用户是否收藏
    is_collected = False
    if user and news in user.collection_news:
        is_collected = True

    # 定义字典数据，返回模板
    data = {
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list,
        'news_detail':news.to_dict(),
        'is_collected':is_collected
    }

    return render_template('news/detail.html',data=data)


@news_blue.route('/news_collect',methods=['POST'])
@login_required
def news_collect():
    """
    新闻收藏和取消收藏
    1、获取参数，news_id,action[collect,cancel_collect]
    2、检查参数的完整性
    3、转换数据类型，可选
    4、检查action参数的范围
    5、查询数据库，确认新闻的存在
    6、判断查询结果
    7、如果新闻存在，如果用户选择收藏，之前是否收藏过
    user.collection_news.append(news)
    8、如果用户选择取消收藏
    user.colleciton_news.remove(news)
    9、返回结果

    :return:
    """
    # 从登录验证装饰器中获取用户信息
    user = g.user
    # 如果用户未登录
    if not user:
        return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')

    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 检查参数的完整性
    if not all([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 转换数据类型
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数类型错误')
    # 检查action参数必须为收藏或取消收藏
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=RET.PARAMERR,errmsg='参数格式错误')
    # 根据news_id查询mysql数据库，确认新闻的存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻数据失败')
    # 判断查询结果
    if not news:
        return jsonify(errno=RET.NODATA,errmsg='无新闻数据')
    # 如果用户选择收藏
    if action == 'collect':
        # 该新闻用户没有收藏过
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    # 把数据提交到mysql数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')

    return jsonify(errno=RET.OK,errmsg='OK')
























# 项目logo图标加载
@news_blue.route('/favicon.ico')
def favicon():
    """
    浏览器不是每次请求都加载logo图标，实现代码后，
    1、清除浏览器的浏览信息和缓存。
    2、让浏览器彻底退出重新启动。
    3、重新打开浏览器会有logo图标。
    :return:
    """
    # 通过current_app调用Flask框架内部的发送静态文件给浏览器的函数send_static_file
    return current_app.send_static_file('news/favicon.ico')
