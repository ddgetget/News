# author        TuringEmmy 
# createtime    18-10-8  下午8:04
# coding=utf-8
# doc           PyCharm
from . import news
from flask import session,render_template,current_app

@news.route('/')
def index():
    session['user']='turing'
    return render_template("news/index.html")

# 项目加载logo图标
@news.route('/favicon.ico')
def favico():
    """第一次一页有可能不成功"""
    # 1. 清除浏览器浏览信息和缓存
    # 2. 让浏览器车德系退出，重新启动
    # 3. 重新打开浏览器会有logo
    return current_app.send_static_file("news/favicon.ico")