# author        TuringEmmy 
# createtime    18-10-8  下午10:33
# coding=utf-8
# doc           PyCharm

from flask import jsonify, request, current_app, make_response, session

from app import rb, constants
from app.static.captcha.captcha import captcha
from app.static.util.response_code import RET
from . import passport
import re, random
from app.static.yuntongxun import sms

from app.models import User

from  app import db

# 在登陆的时候使用到了last_loin_time,因此需要使用datatime
from datetime import datetime

"""
generating scheme
send message
register
login
"""


# -----------------------------------图片验证码---------------------------------
@passport.route('/image_code')
def generate_image_code():
    """
    生成图片验证码
    1. 前端图片验证码
    2. 获取参数，如果不存在（postman），返回错误信息
    3. 使用captcha工具，生成图片验证码，name,text,image
    4. 根据uuid来存储图片的验证码
    :return:
    """
    # 获取参数uuid
    image_code_id = request.args.get('image_code_id')
    # print(image_code_id)
    # 判断参数师傅偶存在,
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 调用captcha工具生成图片验证码
    name, text, image = captcha.generate_captcha()
    # print(name)
    try:
        # IMAGE_CODE_REDIS_EXPIRES代表过期时间
        rb.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # print(image_code_id)

    except Exception as e:
        # 错误异常需要记录日志
        # print("test in this part ----------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='保存数据失败')
    else:
        # 如果没有发生异常，返回图片
        response = make_response(image)
        # 设置响应报文的信息
        response.headers['Content-Type'] = 'image/jpg'
        return response


# ------------------------------------发送短信----------------------------------
@passport.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    send chit message
    get parameter -->> check parameter -->> manager -->> return result
    :return:
    """
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')

    # is this data full?
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='parameter not full')
    # is this mobile pattern ok?
    if not re.match(r'1[34567879]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='is mobile pattern ok?')
    # get data from database by redis
    try:
        real_image_code = rb.get('ImageCode_' + image_code_id)
        # print(image_code_id, real_image_code)
    except Exception as e:
        # add Exception to log file
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='get data Exception')
    # real_image_code is out of date ?
    if not real_image_code:
        return jsonify(errno=RET.DATAERR, errmsg='real_image_code was out  of data')
    # delete real_image_code in redis ,because this real_image_code just use for one times
    try:
        rb.delete("ImageCode_" + real_image_code)
    except Exception as e:
        current_app.logger.error(e)
    # compare real_image_code and code
    if real_image_code != image_code:
        return jsonify(errno=RET.DATAERR, errmsg='captcha code is wrong,please try again ')
    # 判断用户是否注册，不要在手机号检查玩判断，容易使外敌攻击
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='查询数据错误')
    else:
        if user is not None:
            return jsonify(errnp=RET.DATAEXIST, errmsg="用户名已注册")

            # build a number fo
    # --------------------------------get a number like XXXXXX------------
    # In[1]:    import random
    # In[2]:    '%06d' % random.randint(0, 999999)
    # Out[2]:   '634485'
    # --------------------------------get a number like XXXXXX------------
    sms_code = "%03d" % random.randint(0, 999)
    try:
        rb.setex("SMSCode_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='save data is error')

    # transfer  yuntongxun interface to send chit message
    try:
        cpp = sms.CCP()
        # ccp.send_template_sms('15313088696', ['249865', 2], 1)
        # the last data '1' is for free user
        results = cpp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='the third package is wrong')
    # 判断发送结果
    if results == 0:
        return jsonify(errno=RET.OK, errmsg='send is ok')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='send is wrong')


# ------------------------------------注册--------------------------------------
@passport.route('/register', methods=["POST"])
def register():
    mobile = request.json.get("mobile")
    sms_code = request.json.get("sms_code")
    password = request.json.get("password")

    # 检查参数的完整性
    if not all([mobile, sms_code, passport]):
        return jsonify(errno=RET.DATAERR, errmsg='参数不完整')
    # 检查手机号码格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机格式不正确')
    # 获取redis的针织短信的验证码
    try:
        real_sms_code = rb.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="获取数据错误")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='数据以过期')
    # 比较短验证码是否一致
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR, errmsg='短信验证失败')
    # 删除redis中存储的短信
    try:
        rb.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 构造模型对象，存储用户信息
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 注意：这里不用加密的原因是。在模型类当中,使用了property,赋值的结果是加密过后的哦，很厉害的哦
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg="保存用户信息失败")
    # 这里需要缓存用户信息，保存刀片flask的seesion当中
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='ok')


# ----------------------------------------登陆----------------------------------
@passport.route('/login', methods=["POST"])
def login():
    # 注意：用户的昵称可能发生变化
    # session['nick_name']=mobile
    # session['nick_name']=user.nick_name
    # ------------------体会一下这两行代码的的异同


    mobile = request.json.get('mobile')
    password = request.json.get("password")
    print(mobile)
    print(password)

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式错误')

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='密码错误')

    # ------------------代码太low----------------------------
    # if not user:
    #     return jsonify(errno=RET.NODATA,errmsg="用户不存在")
    # # 判断密码是否正确
    # if user.check_password(password):
    #     return jsonify(errno=RET.PWDERR,errmsg='密码错误')
    # --------------------代码太low--------------------------


    if user is None or not user.check_password(password):
        return jsonify(errno=RET.NODATA, errmsg='参数输入错误')

    # 记录用户的登陆时间
    user.last_login = datetime.now()

    # 提交数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据错误")

    # 缓存用户的信息
    session['user_id'] = user.id
    session['mobile'] = mobile
    # 防止用户修改用户昵称，而缓存当中依然使用原来的nick_name
    session['nick_name'] = user.nick_name

    return jsonify(errno=RET.OK, errmsg="ok")


# -------------------------------------退出登陆-----------------------------------
@passport.route('/logout')
def logout():
    """
    退出登陆，清除redis的数据
    :return:
    """
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name')
    return jsonify(errno=RET.OK,errmsg='ok')













