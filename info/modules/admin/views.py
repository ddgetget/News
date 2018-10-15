# author        TuringEmmy 
# createtime    18-10-12  下午3:27
# coding=utf-8
# doc           PyCharm
import time

from datetime import datetime, timedelta
from flask import current_app, jsonify
from flask import g
from flask import render_template, request
from flask import session
from flask import redirect
from flask import url_for

from info import constants
from info import db
from info.modules.admin import admin_blue
from info.utils.image_storage import storage

9
from info.models import User, News, Category
from info.utils.response_code import RET

from info.utils.commons import login_required


# ---------------------------------管理员登陆-------------------------------------------------
@admin_blue.route('/login', methods=["POST", "GET"])
def admin_login():
    if request.method == 'GET':
        # 获取session当中指定的值
        user_id = session.get("user_id", None)
        is_admin = session.get('is_admin', False)

        # 校验参数的完整性
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    # 获取登陆的参数
    username = request.form.get('username')
    password = request.form.get('password')

    # 校验3参数的完整性
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数不完整')

    # 查询数据库
    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    # 验证数据库查询结果的完整性
    if not user:
        return render_template('admin/login.html', errmsg='用户不存在')

    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='密码错误')

    # 检查是否是管理员，只需要验证is_admin参数的1还是0
    if not user.is_admin:
        return render_template('admin/login.html', errmsg='用户权限错误')

    # 一定要记得保存登陆后的用户信息到session
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['is_admin'] = user.is_admin

    # 跳转到后台管理主页
    return redirect(url_for('admin.admin_index'))


# ----------------------------------用户统计模块--------------------------------------------------
@admin_blue.route('/user_count')
def user_count():
    """
    用户统计
    1、总人数
    2、月新增人数
    3、日新增人数
    4、活跃时间
    5、活跃人数
    :return:
    """
    # 总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询总人数失败')

    # tm_year=2018, tm_mon=10, tm_mday=12
    # 2018-10-12---2018-10-01
    # 月新增人数：统计每月1日的0时0分0秒比较到当前日期(用户的注册时间)
    mon_count = 0
    t = time.localtime()
    # 每月开始日期的字符串:2018-10-01
    mon_begin_date_str = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 用户注册时间为datetime对象，要把日期字符串转成日期对象
    mon_begin_date = datetime.strptime(mon_begin_date_str, '%Y-%m-%d')
    # 查询数据库，获取月新增人数
    try:
        # 用户注册时间大于每月1日
        mon_count = User.query.filter(User.is_admin == False, User.create_time > mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询月新增人数失败')

    # 日新增人数
    day_count = 0
    # 获取每天的开始时间字符串
    day_begin_date_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 把日期字符串转成日期对象
    day_begin_date = datetime.strptime(day_begin_date_str, '%Y-%m-%d')
    # 查询数据库，获取日新增人数
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询日新增人数失败')

    # 用户活跃度统计
    active_count = []
    active_time = []
    # 获取当前日期字符串
    today_begin_data_str = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 转换日期对象
    today_begin_date = datetime.strptime(today_begin_data_str, '%Y-%m-%d')

    # 从当前往前推31天，获取每天的开始时间、结束时间
    for d in range(0, 31):
        begin_date = today_begin_date - timedelta(days=d)  # 每天的开始时间
        end_date = today_begin_date - timedelta(days=(d - 1))  # 每天的结束时间
        # 根据每天的日期来查询mysql数据库，比较用户的登录时间
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询用户活跃数据失败')
        # 添加查询结果到列表中
        active_count.append(count)
        # 把时间对象转成时间字符串
        begin_date_str = datetime.strftime(begin_date, '%Y-%m-%d')
        active_time.append(begin_date_str)

    active_time.reverse()
    active_count.reverse()

    # 定义字典
    data = {
        'total_count': total_count,
        'mon_count': mon_count,
        'day_count': day_count,
        'active_count': active_count,
        'active_time': active_time
    }
    return render_template('admin/user_count.html', data=data)


# ------------------------------------------后台管理主页--------------------------------------
@admin_blue.route('/index', methods=['GET', 'POST'])
@login_required
def admin_index():
    # 使用flask内置的g对象，=取出值
    user = g.user

    return render_template('admin/index.html', user=user.to_dict())


# -------------------------------用户列表-------------------------------------------------------

@admin_blue.route('/user_list')
@login_required
def user_list():
    """
    获取用户列表
    :return:
    """
    # 获取参数

    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 设置默认值
    users = []
    current_page = 1
    total_page = 1

    # 查询数据
    try:
        paginate = User.query.filter(
            User.is_admin == False
        ).order_by(
            User.last_login.desc()
        ).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        # print(e)
        # print('sadas')
        return jsonify(errno=RET.NODATA, errmsg='data is error')
    # 将模型列表转化成走字典列表

    users_list = []
    for user in users:
        users_list.append(user.to_admin_dict())

    context = {
        'total_page': total_page,
        "current_page": current_page,
        'users': users_list
    }

    return render_template('admin/user_list.html', context=context)




# --------------------------------新闻审核-------------------------------------------------------
@admin_blue.route('/news_review')
def news_review():
    """
    返回待审核新闻列表
    :return:
    """

    page = request.args.get('p', 1)

    # 关键词搜索
    keywords = request.args.get('keywords', "")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        paginate = News.query.filter(
            News.status != 0
        ).order_by(
            News.create_time.desc()
        ).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        filters = [News.status != 0]
        if keywords:
            # 添加关键词到检索选项
            filters.append(News.title.contains(keywords))

            # 查询
            paginate = News.query.filter(
                *filters
            ).order_by(
                News.create_time.desc()
            ).paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据查询失败')

    data = {
        'total_page': total_page,
        "current_page": current_page,
        "news_list": news_list
    }

    return render_template('admin/news_review.html', data=data)





# ----------------------------------新闻审核详情------------------------------------------------------
@admin_blue.route('/news_review_detail', methods=['POST', "GET"])
def news_review_detail():
    """
    新闻审核
    :return:
    """
    # if request.method =="GET":
    #     # 获取新闻分类数据
    #     categories = Category.query.all()
    #     # 定义列表保存分类数据
    #     categories_dicts = []
    #
    #     for category in enumerate(categories):
    #         # 拼接内容
    #         categories_dicts.append(category.to_dict())
    #
    #     return render_template('admin/news_review_detail.html', data=categories)

    news_id = request.json.get('news_id')
    action = request.json.get('action')

    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    # if not news_id:
    #     return render_template('admin/news_review_detail.html', data={
    #         'srrmsg': "未查询到次新闻"
    #     })

    # 通过新闻的id查询新闻
    news = None

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    if not news:
        return render_template('admin/news_review_detail.html', data={
            'errmsg': "未查询到此新闻"
        })

    if action == 'accept':
        news.status = 0
    else:
        # 拒绝通过,需要获取原因
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        news.reason = reason

        news.status = -1

    # 保存数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    # 返回数据
    data = {
        'news': news.to_dict()
    }

    return render_template('admin/news_review_detail.html', data=data)





# ---------------------------------------新闻板式编辑---------------------------------------------
@admin_blue.route('/news_edit')
def news_edit():
    """返回新闻列表"""

    page = request.args.get("p", 1)
    keywords = request.args.get("keywords", "")
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        filters = []
        # 如果有关键词
        if keywords:
            # 添加关键词的检索选项
            filters.append(News.title.contains(keywords))

        # 查询
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {"total_page": total_page, "current_page": current_page, "news_list": news_dict_list}

    return render_template('admin/news_edit.html', data=context)






# ------------------------------------------新闻编辑详情也--------------------------------------------
@admin_blue.route('/news_edit_detail', methods=["GET", "POST"])
def news_edit_detail():
    """新闻编辑详情"""
    if request.method == "GET":
        # 获取参数
        news_id = request.args.get("news_id")

        if not news_id:
            return render_template('admin/news_edit_detail.html', data={"errmsg": "未查询到此新闻"})

        # 查询新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_edit_detail.html', data={"errmsg": "未查询到此新闻"})
        # 查询分类的数据
        categories = Category.query.all()
        categories_li = []
        for category in categories:
            c_dict = category.to_dict()
            c_dict["is_selected"] = False
            if category.id == news.category_id:
                c_dict["is_selected"] = True
            categories_li.append(c_dict)
        # 移除`最新`分类
        categories_li.pop(0)

        data = {"news": news.to_dict(), "categories": categories_li}
        return render_template('admin/news_edit_detail.html', data=data)

    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, digest, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误1")

    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 1.2 尝试读取图片
    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误2")

        # 2. 将标题图片上传到七牛
        try:
            key = storage(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    # 3. 设置相关数据
    news.title = title
    news.digest = digest
    news.content = content
    news.category_id = category_id

    # 4. 保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno=RET.OK, errmsg="编辑成功")

