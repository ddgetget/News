# author        TuringEmmy 
# createtime    18-10-12  下午5:15
# coding=utf-8
# doc           PyCharm
import datetime
import random

from info import db
from info.models import User
from manage import app


def add_text_users():
    users = []
    now = datetime.datetime.now()

    for num in range(0, 100000):
        try:
            user = User()

            user.nick_name = '%011d' % num
            user.mobile = '%011d' % num
            user.password_hash = 'asgdhjasgdhjdghjasgdhjgwqyuretuywqtgeyuwqtyutwyuet'

            user.last_login = now - datetime.timedelta(seconds=random.randint(0, 2678400))

            users.append(user)
            print(user.mobile)

        except Exception as e:
            print(e)

    with app.app_context():
        db.session.add_all(users)
        db.session.commit()

    print('OK')

if __name__ == '__main__':
    add_text_users()
