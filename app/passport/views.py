# author        TuringEmmy 
# createtime    18-10-8  下午10:33
# coding=utf-8
# doc           PyCharm

from flask import jsonify, request, current_app, make_response

from app import rb, constants
from app.static.captcha.captcha import captcha
from app.static.util.response_code import RET
from . import passport


"""
生成图片验证码
发送短信
注册
登陆
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
        print("ersdghjasgdhjgajshk")
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg='保存数据失败')
    else:
        # 如果没有发生异常，返回图片
        response = make_response(image)
        response.headers['Content-Type'] = 'image/jpg'
        return response

