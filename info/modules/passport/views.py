from flask import request, jsonify,current_app,make_response,session

from . import passport_blue
# 导入图片验证码工具
from info.utils.captcha.captcha import captcha
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入redis实例
from info import redis_store,constants,db
# 导入云通讯扩展
from info.libs.yuntongxun import sms
# 导入模型类
from info.models import User
# 导入正则,随机数
import re,random
# 导入日期模块
from datetime import datetime


"""
1、生成图片验证码
2、发送短信
3、注册
4、登录

"""
@passport_blue.route('/image_code')
def generate_image_code():
    """
    生成图片验证码
    1、前端传入uuid给后端，用来实现图片验证码的存储
    2、获取参数uuid，如果参数不存在，返回错误信息
    3、使用captcha工具，生成图片验证码，name,text,image
    4、根据uuid来存储图片验证码，存储在redis中text，
    5、返回图片
    :return:
    """
    # 获取参数uuid
    image_code_id = request.args.get('image_code_id')
    # 判断参数是否存在，返回的自定义的状态码，用来实现前后端的数据交互
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 调用captcha工具生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 把图片验证码的text存储到redis数据库中
    try:
        redis_store.setex('ImageCode_' + image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    else:
        # 如果没有发生异常，返回图片
        response = make_response(image)
        # 设置响应的报文信息，响应的类型为图片
        response.headers['Content-Type'] = 'image/jpg'
        return response

@passport_blue.route("/sms_code",methods=['POST'])
def send_sms_code():
    """
    发送短信：写接口、调接口
    获取参数-----检查参数-----业务处理-----返回结果
    1、获取参数mobile，image_code,image_code_id
    2、检查参数的完整性
    3、检查手机号的格式，正则
    4、尝试从redis数据库中获取真实的图片验证码
    5、判断获取结果是否存在，图片验证码有可能过期
    6、删除图片验证码
    7、比较图片验证码是否一致
    8、构造短信随机码，6位数
    9、调用云通讯发送短信方法
    10、判断发送结果是否成功
    11、返回结果

    :return:
    """
    # 获取参数
    mobile = request.json.get("mobile")
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")
    # 检查参数的完整性
    # if mobile and image_code and image_code_id:
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 检查手机号的格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    # 获取redis数据库中存储的真实图片验证码
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取数据异常')
    # 判断数据是否过期
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsmg='数据已过期')
    # 删除redis数据库中存储的图片验证码，因为图片验证码只能比较一次，本质是只能读取redis数据库一次
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证码是否一致，忽略大小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')
    # 判断用户是否已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST,errmsg='用户已存在')

    # 构造短信随机数,保存到redis数据库中
    sms_code = '%06d' % random.randint(0, 999999)
    print(sms_code)
    try:
        redis_store.setex('SMSCode_' + mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='存储数据异常')
    # 调用云通讯接口，发送短信
    try:
        ccp = sms.CCP()
        results = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
    # 判断发送结果
    if results == 0:
        return jsonify(errno=RET.OK,errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR,errmsg='发送失败')


@passport_blue.route("/register",methods=['POST'])
def register():
    """
    用户注册
    1、获取参数
    2、检查参数的完整性
    3、检查手机号格式
    4、尝试从redis中获取真实的短信验证码
    5、判断获取结果
    6、先比较短信验证码是否一致，因为短信验证码可以比较多次
    7、删除redis中存储的短信验证码
    8、构造模型类对象，存储用户信息
    9、缓存用户信息，redis中的session信息
    10、返回结果

    :return:
    """
    # 获取参数
    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    password = request.json.get('password')
    # 检查参数的完整性
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 检查手机号的格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 获取redis中存储的真实的短信验证码
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取数据失败')
    # 判断获取结果
    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg='数据已过期')
    # 比较短信验证码是否一致
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR,errmsg='短信验证码错误')
    # 删除redis中存储的短信
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 构造模型类对象，存储用户信息
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 实际上调用了模型类中的密码加密函数，generate_password_hash
    user.password = password
    # 提交数据到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存用户信息失败')
    # 缓存用户信息到redis数据库中
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')


@passport_blue.route('/login',methods=['POST'])
def login():
    """
    用户登录
    获取参数-----检查参数-----业务处理-----返回结果
    1、获取参数，mobile，password
    2、检查参数的完整性
    3、检查手机号格式
    4、根据手机号查询mysql确认用户已注册
    5、判断查询结果
    6、如果用户已注册，密码正确，运行登录
    7、缓存用户信息
    session['nick_name'] = mobile
    session['nick_name'] = user.nick_name
    8、返回结果

    :return:
    """
    # 获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 检查参数的完整性
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 检查手机号格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 查询MySQL数据库，确认用户已注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')
    # 提示信息比较准确，判断查询结果
    # if not user:
    #     return jsonify(errno=RET.NODATA,errmsg='用户不存在')
    # # 判断密码是否正确
    # if user.check_password(password):
    #     return jsonify(errno=RET.PWDERR,errmsg='密码错误')

    # 用户名和密码一起判断，check_password是模型类中的密码检查方法
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR,errmsg='用户名或密码错误')
    # 记录用户的登录时间
    user.last_login = datetime.now()
    # 提交数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 缓存用户信息
    session['user_id'] = user.id
    session['mobile'] = mobile
    # 因为登录可以执行多次，用户有可能修改昵称，所以缓存中需要修改
    session['nick_name'] = user.nick_name
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')

@passport_blue.route('/logout')
def logout():
    """退出登录"""
    # 从redis中清除缓存的用户信息
    session.pop('user_id',None)
    session.pop('mobile',None)
    session.pop('nick_name',None)
    return jsonify(errno=RET.OK,errmsg='OK')











    pass