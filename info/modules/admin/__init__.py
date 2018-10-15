# author        TuringEmmy 
# createtime    18-10-12  下午3:26
# coding=utf-8
# doc           PyCharm
from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import url_for

admin_blue = Blueprint("admin", __name__,url_prefix='/admin')

# 吧使用蓝图的对象文件导入到常见蓝图对象的下面
from . import views


# 除了登陆页面，后台的其他页面都要判断是否具有管理员权限
@admin_blue.before_request
def before_request():
    # 判断如果不是登陆页面的请求
    if not request.url.endswith(url_for('admin.admin_login')):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin',False)

        # 校验参数的完整性,如果有任何不完整的，从定向新闻首页
        if not user_id or not is_admin:
            return redirect('/')