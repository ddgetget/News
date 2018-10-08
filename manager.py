# author        TuringEmmy 
# createtime    18-10-8  下午12:17
# coding=utf-8
# doc           PyCharm

from flask import Flask

app = Flask(__name__)


@app.route('/index')
def index():
    return "index"


if __name__ == '__main__':
    app.run()
