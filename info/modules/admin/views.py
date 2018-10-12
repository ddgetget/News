# author        TuringEmmy 
# createtime    18-10-12  下午3:27
# coding=utf-8
# doc           PyCharm
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
        user_id =session.get("user_id",None)
        is_admin = session.get('is_admin',False)

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


# ------------------------------------------后台管理主页--------------------------------------
@admin_blue.route('/index', methods = ['GET','POST'])
@login_required
def admin_index():
    # 使用flask内置的g对象，=取出值
    user = g.user

    return render_template('admin/index.html', user=user.to_dict())
