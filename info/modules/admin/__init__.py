# author        TuringEmmy 
# createtime    18-10-12  下午3:26
# coding=utf-8
# doc           PyCharm
from flask import Blueprint

admin_blue = Blueprint("admin_blue", __name__,url_prefix='/admin')

# 吧使用蓝图的对象文件导入到常见蓝图对象的下面
from . import views
