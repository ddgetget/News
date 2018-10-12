from flask import Blueprint

news_blue = Blueprint('news_blue',__name__)

# 把使用蓝图对象的文件，导入到创建蓝图对象的下面
from . import views
