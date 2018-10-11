# author        TuringEmmy 
# createtime    18-10-11  下午7:43
# coding=utf-8
# doc           PyCharm

from . import profile
# 导入登陆装饰器

from app.static.util.comments import login_required
from flask import redirect, g, request, render_template, jsonify, current_app

from app.static.util.response_code import RET

from  app import db


@profile.route('/info', methods=['POST', 'GET'])
@login_required
def user_info():
    """
    个人中心基本页面展示
    :return:
    """
    user = g.user
    # 用户昵称，性别，名称
    if not user:
        return redirect('/')

    data = {
        'user': user.to_dict()
    }

    return render_template('news/user.html', data=data)


@profile.route('/base_info', methods=['POST', 'GET'])
@login_required
def base_info():
    user = g.user
    # 用户昵称，性别，昵称
    if request.method == "GET":
        data = {
            'user': user.to_dict()
        }

        return render_template('news/user_base_info.html', data=data)

    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')

    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.DBERR, errmsg='参数不完整')

    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式不正确')

    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存错误")
    
    return jsonify(errno=RET.OK, errmsg='ok')
