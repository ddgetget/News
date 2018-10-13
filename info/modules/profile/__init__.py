from flask import Blueprint

profile_blue = Blueprint('profile_blue', __name__, url_prefix='/user')

# RESTful风格 表现层状态转换

from . import views
