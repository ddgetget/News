# author        TuringEmmy 
# createtime    18-10-8  下午7:58
# coding=utf-8
# doc           PyCharm
from flask import Blueprint

news = Blueprint("news",__name__)


# 把使用蓝图的对象的文件导入到创建蓝图对象的下面
from . import views