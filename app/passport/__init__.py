# author        TuringEmmy 
# createtime    18-10-8  下午10:33
# coding=utf-8
# doc           PyCharm
from flask import Blueprint
passport = Blueprint("passport",__name__)
from . import views