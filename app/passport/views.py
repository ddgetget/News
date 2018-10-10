# author        TuringEmmy 
# createtime    18-10-8  下午10:33
# coding=utf-8
# doc           PyCharm

from flask import jsonify, request, current_app, make_response

from app import rb, constants
from app.static.captcha.captcha import captcha
from app.static.util.response_code import RET
from . import passport
import re, random
from app.static.yuntongxun import sms

"""
generating scheme
send message
register
login
"""


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
        rb.setex('Imagecode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        print(image_code_id)

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


@passport.route('/sms_code', methods=['POST'])
def send_smd_code():
    """
    send chit message
    get parameter -->> check parameter -->> manager -->> return result
    :return:
    """
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')

    # is this data full?
    if not all(mobile, image_code, image_code_id):
        return jsonify(errno=RET.DATAERR, errmsg='parameter not full')
    # is this mobile pattern ok?
    if not re.match(r'1[34567879]\d{9}$', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='is mobile pattern ok?')
    # get data from database by redis
    try:
        real_image_code = rb.get('ImageCode_' + image_code_id)
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

    # build a number fo
    # --------------------------------get a number like XXXXXX------------
    # In[1]:    import random
    # In[2]:    '%06d' % random.randint(0, 999999)
    # Out[2]:   '634485'
    # --------------------------------get a number like XXXXXX------------
    sms_code = "%06d" % random.randint(0, 999999)
    try:
        rb.setex("SMSCode_"+mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='save data is error')

    # transfer  yuntongxun interface to send chit message
    try:
        cpp=sms.CCP()
        # ccp.send_template_sms('15313088696', ['249865', 2], 1)
        # the last data '1' is for free user
        cpp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='the third package is wrong')
    pass
