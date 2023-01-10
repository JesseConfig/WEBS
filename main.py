from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import url_for, redirect

from flask_sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__, template_folder="./templates/")
basedir = os.path.abspath(os.path.dirname(__file__))

# 设置连接数据库的URL
# 不同的数据库采用不同的引擎连接语句：
# MySQL             mysql://username:password@hostname/database
# Postgres          postgresql://username:password@hostname/database
# SQLite（Unix）     sqlite:////absolute/path/to/database
# SQLite（Windows）  sqlite:///c:/absolute/path/to/database

# http://www.pythondoc.com/flask-sqlalchemy/config.html
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite.db')
app.config['SECRET_KEY'] = 'hard to guess string'

# 设置每次请求结束后会自动提交数据库的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 追踪对象的修改并且发送信号
# 查询时显示原始SQL语句
app.config['SQLALCHEMY_ECHO'] = False

db = SQLAlchemy(app)


# 模型和表
# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/models/

class User(db.Model):
    __tablename__ = 'users'  # 表名
    # 定义字段名，字段类型
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password = db.Column(db.String(64), nullable=False, index=True)
    intime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return 'username %r password %r' % (self.username,self.password)

@app.route('/')
def index():
    # url_for第一个参数就是endpoint
    return redirect(url_for('login'))  # 自动跳转到另一个URL所在的地址

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        print(username, password)

        da = User.query.filter_by(username=username).first()
        print(da)

        if not da :
            return 'Invalid username'

    # return render_template("login.html")
    return render_template("login.html")

# UserID1


if __name__ == '__main__':
    # with app.app_context():
        # # 删除表
        # db.drop_all()
        # 创建表
        # db.create_all()
        # user_john = User(id=1,username='UserID1',password='1234')
        # print(user_john)
        # db.session.add(user_john)
        # db.session.commit()
        # print(User.query.all())

    app.run(debug=True, port=8000)
