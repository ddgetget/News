# author        TuringEmmy 
# createtime    18-10-11  下午7:43
# coding=utf-8
# doc           PyCharm

from flask import Blueprint

profile=Blueprint("profile",__name__,url_prefix='/user')

from . import views

