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

from info import db
from info.modules.admin import admin_blue

from info.models import User
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
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询总人数失败')

    # tm_year=2018, tm_mon=10, tm_mday=12
    # 2018-10-12---2018-10-01
    # 月新增人数：统计每月1日的0时0分0秒比较到当前日期(用户的注册时间)
    mon_count = 0
    t = time.localtime()
    # 每月开始日期的字符串:2018-10-01
    mon_begin_date_str = '%d-%02d-01' % (t.tm_year,t.tm_mon)
    # 用户注册时间为datetime对象，要把日期字符串转成日期对象
    mon_begin_date = datetime.strptime(mon_begin_date_str,'%Y-%m-%d')
    # 查询数据库，获取月新增人数
    try:
        # 用户注册时间大于每月1日
        mon_count = User.query.filter(User.is_admin==False,User.create_time>mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询月新增人数失败')

    # 日新增人数
    day_count = 0
    # 获取每天的开始时间字符串
    day_begin_date_str = '%d-%02d-%02d' % (t.tm_year,t.tm_mon,t.tm_mday)
    # 把日期字符串转成日期对象
    day_begin_date = datetime.strptime(day_begin_date_str,'%Y-%m-%d')
    # 查询数据库，获取日新增人数
    try:
        day_count = User.query.filter(User.is_admin==False,User.create_time>day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询日新增人数失败')

    # 用户活跃度统计
    active_count = []
    active_time = []
    # 获取当前日期字符串
    today_begin_data_str = '%d-%02d-%02d' % (t.tm_year,t.tm_mon,t.tm_mday)
    # 转换日期对象
    today_begin_date = datetime.strptime(today_begin_data_str,'%Y-%m-%d')

    # 从当前往前推31天，获取每天的开始时间、结束时间
    for d in range(0,31):
        begin_date = today_begin_date - timedelta(days=d) # 每天的开始时间
        end_date = today_begin_date - timedelta(days=(d-1)) # 每天的结束时间
        # 根据每天的日期来查询mysql数据库，比较用户的登录时间
        try:
            count = User.query.filter(User.is_admin==False,User.last_login>=begin_date,User.last_login<end_date).count()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='查询用户活跃数据失败')
        # 添加查询结果到列表中
        active_count.append(count)
        # 把时间对象转成时间字符串
        begin_date_str = datetime.strftime(begin_date,'%Y-%m-%d')
        active_time.append(begin_date_str)

    active_time.reverse()
    active_count.reverse()

    # 定义字典
    data = {
        'total_count':total_count,
        'mon_count':mon_count,
        'day_count':day_count,
        'active_count':active_count,
        'active_time':active_time
    }
    return render_template('admin/user_count.html',data=data)


# ------------------------------------------后台管理主页--------------------------------------
@admin_blue.route('/index', methods=['GET', 'POST'])
@login_required
def admin_index():
    # 使用flask内置的g对象，=取出值
    user = g.user

    return render_template('admin/index.html', user=user.to_dict())


# --------------------------用户统计-------------------------------------------
# @admin_blue.route('/user_count')
# def user_count():
#     # 查询总人数
#     total_count = 0
#     try:
#         total_count = User.query.filter(User.is_admin == False).count()
#     except Exception as e:
#         current_app.logger.error(e)
#         db.session.rollback()
#
#     # 查询约新增人人数
#     mon_count = 0
#     try:
#         now = time.localtime()
#         mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
#         mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
#         mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
#     except Exception as e:
#         current_app.logger.error(e)
#
#         # 查询日新增人数
#     day_count = 0
#     try:
#         day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
#         day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
#         day_count = User.query.filter(User.is_admin == False, User.create_time >= day_begin_date).count()
#     except Exception as e:
#         current_app.logger.error(e)
#         db.session.rollback()
#         return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
#
#     now_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
#
#     active_time = []
#     active_count = []
#
#     for i in range(0, 31):
#         begin_date = now_date - timedelta(days=i)
#         end_date = now_date - timedelta(days=(i - 1))
#
#         active_time.append((begin_date.strftime('%Y-%m-%d')))
#         count = 0
#         try:
#             count = User.query.filter(User.is_admin == False, User.last_login >= day_begin,
#                                       User.last_login < end_date).count()
#         except Exception as e:
#             current_app.logger.error(e)
#             db.session.rollback()
#             return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
#
#         active_count.append(count)
#         begin_date_str = datetime.strftime(begin_date,'%Y-%m-%d')
#         active_count.append(begin_date_str)
#
#
#     active_time.reverse()
#     active_count.reverse()
#
#     data = {
#         'total_count': total_count,
#         'mon_count': mon_count,
#         'day_count': day_count,
#         'active_time': active_time,
#         'active_count': active_count
#     }
#
#     return render_template('admin/user_count.html', data=data)
