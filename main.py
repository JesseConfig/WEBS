# https://www.bilibili.com/video/BV1FY411G7Z6/?spm_id_from=333.999.0.0

from flask import Flask                     # 主包
from flask import render_template           # 重定向
from flask import session                   # session
from flask import request                   # 表单数据返回
from flask import url_for, redirect         # 重定向
from flask_sqlalchemy import SQLAlchemy     # 数据库引擎
import os,datetime                          # 系统包

from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user

# 初始化 template_folder 定义 html 网页存储位置
app = Flask(__name__, template_folder="./templates/")
# 获取运行脚本当前目录
basedir = os.path.abspath(os.path.dirname(__file__))

# 设置连接数据库的URL
# 不同的数据库采用不同的引擎连接语句：
# MySQL             mysql://username:password@hostname/database
# Postgres          postgresql://username:password@hostname/database
# SQLite（Unix）     sqlite:////absolute/path/to/database
# SQLite（Windows）  sqlite:///c:/absolute/path/to/database

# http://www.pythondoc.com/flask-sqlalchemy/config.html
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# 设置每次请求结束后会自动提交数据库的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 追踪对象的修改并且发送信号
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时显示原始SQL语句
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'hard to guess string'

# 初始化
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.login_message = u"请先登录。"


# 模型和表
# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/models/

class User(UserMixin,db.Model):
    __tablename__ = 'users'  # 表名
    # 定义字段名，字段类型
    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password = db.Column(db.String(64), nullable=False, index=True)
    intime = db.Column(db.DateTime, default=datetime.datetime.now())
    # def __repr__(self):
    #     return 'username %r password %r' % (self.username,self.password)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
        return date.strftime(fmt)

@app.route('/')
def index():
    # 自动跳转登录地址
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print("用户名：%s 密码： %s" % (username, password))

        # 使用User.query.get(唯一的id编号)
        # 使用User.query.filter_by(id=查询的条件).first()，通过条件进行查询操作

        us = User.query.filter_by(username=username,password=password).first()
        if us is None:
            # flash('账号或密码错误！')
            print("账号或密码错误！")
            return redirect(url_for('login'))
        else:
            login_user(us)
            session['username'] = us.username
            session['password'] = us.password
            print(session)
            return redirect(url_for('home'))

    return render_template('login.html',error="账号或密码错误!")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/index")
@login_required
def home():
    tuple_A = db.session.query(User.id, User.username, User.password, User.intime).all()
    dict_h = ["id", "username", "password", "initime"]
    dict_A = []
    for tuple_i in tuple_A:
        list_s = []
        for list_i in list(tuple_i):
            # print(list_i)
            if isinstance(list_i, datetime.datetime):
                # list_i=list_i.strftime('%Y-%m-%d %H:%M:%S')
                # list_s.append(datetime.datetime.strptime(list_i,'%Y-%m-%d %H:%M:%S'))
                list_s.append(list_i.strftime('%Y-%m-%d %H:%M:%S'))

            else:
                list_s.append(list_i)
            # print(list_s)
        dict_A.append(dict(zip(dict_h, list_s)))
    return render_template('index.html',USER=dict_A,session=session)

@app.route("/adduser" , methods=["GET", "POST"])
@login_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        a=User()
        a.username = username
        a.password = password
        print("用户名：%s 密码： %s" % (username, password))
        db.session.add(a)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('adduser.html')

@app.route("/delete" , methods=["GET", "POST"])
@login_required
def delete():
    """
    filter_by()：把等值过滤器添加到原查询上，返回一个新查询；
    filter()：把过滤器添加到原查询上，返回一个新查询。
    """
    name=request.args.get("name")
    print(name,request.args.get("name"),len(name),len(request.args.get("name")))
    a=User.query.filter_by(username=name).first()
    print(a)
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/change" , methods=["GET", "POST"])
@login_required
def change():
    # 获取name
    name = request.args.get("name")

    a = User.query.filter_by(username=name).first()

    if request.method == "POST":
    # 获取 post 提交信息
        username = request.form.get("username")
        password = request.form.get("password")

        # 修改 表单数据
        a.username = username
        a.password = password

        db.session.add(a)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update_user.html',username=a.username,password=a.password)



# @app.route('/user/<id>')
# def user_info(id):
#     user = User.query.filter_by(id=id).first()
#     return render_template('user-info.html', user=user, name=session.get('name'))

# @app.route('/change_password', methods=['GET', 'POST'])
# def change_password():
#     if form.password2.data != form.password.data:
#         flash(u'两次密码不一致！')
#     if form.validate_on_submit():
#         if current_user.verify_password(form.old_password.data):
#             current_user.password = form.password.data
#             db.session.add(current_user)
#             db.session.commit()
#             flash(u'已成功修改密码！')
#             return redirect(url_for('index'))
#         else:
#             flash(u'原密码输入错误，修改失败！')
#     return render_template("change-password.html", form=form)


if __name__ == '__main__':
    # with app.app_context():
        # # 删除表
        # db.drop_all()
        # #创建表
        # db.create_all()
        # a=User()
        # a.username='101'
        # a.password='1234'
        # db.session.add(a)
        # db.session.commit()

        # print(User.query.all())
        # User.query.all()
        # User.query.filter_by(username=username).all()
    app.run(debug=True, port=8000)
