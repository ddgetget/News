# author        TuringEmmy 
# createtime    18-10-11  下午7:43
# coding=utf-8
# doc           PyCharm

from flask import redirect, g, request, render_template, jsonify, current_app,session

from  app import db, constants
from app.static.util.comments import login_required
from app.static.util.response_code import RET
from . import profile


from app.static.util.image_storage import storage

# -----------------------------------个人信息--------------------------
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



# -------------------------------修改信息----------------------------
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

    session['nick_name'] = nick_name

    # 需要修改redis数据库
    return jsonify(errno=RET.OK, errmsg='ok')



# -----------------------------图片--------------------------------
@profile.route('/pic_info',methods=["POST","GET"])
@login_required
def save_avater():
    user = g.user

    if request.method=="GET":
        data={
            'user':user.to_dict()
        }
    return render_template('news/user_pic_info.html',data=data)

    # 获取参数
    avatar =request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')

    try:
        image_data = avatar.read()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 调用骑牛云
    try:
        image_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    # 保存用户图像名称
    user.avatar_url = image_name

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    avatar_url = constants.QINIU_DOMIN_PREFIX+image_name

    # 返回结果
    data={
        'avatar_url':avatar_url
    }
    return jsonify(errno=RET.OK,errmsg='ok')
