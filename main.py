# https://www.bilibili.com/video/BV1FY411G7Z6/?spm_id_from=333.999.0.0
import datetime  # 系统包
import os
import uuid
from flask import Flask, send_from_directory  # 主包
from flask import render_template  # 重定向
from flask import request  # 表单数据返回
from flask import session  # session
from flask import url_for, redirect  # 重定向
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))
# 初始化 template_folder 定义 html 网页存储位置
app = Flask(__name__, template_folder="./templates/")
# 获取运行脚本当前目录
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


# 1.引入SQLAlchemy并绑定到app上
# 2.class name 是创建表，必须继承db.Model类
# 3.db.Column用来创建列
# 4.__init__用来创建插入的方法
# 5.__repr__用来控制输出的格式
# 模型和表
# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/models
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # 表名
    # 定义字段名，字段类型
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    password = db.Column(db.String, nullable=False, index=True)
    intime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return 'username %r userid %r' % (self.username, self.id)


class UPLOAD_LOG(UserMixin, db.Model):
    __tablename__ = 'upload_log'  # 表名
    fileid = db.Column(db.Integer, autoincrement=True, primary_key=True)
    filename = db.Column(db.String, unique=True, nullable=False, index=True)
    userid = db.Column(db.String, nullable=False, index=True)
    Uploadtime = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, userid, filename):
        self.filename = filename
        self.userid = userid

    def __repr__(self):
        return 'fileid %r filename %r' % (self.fileid, self.filename)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.login_message = u"请先登录。"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

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

        us = User.query.filter_by(username=username, password=password).first()
        if us is None:
            # flash('账号或密码错误！')
            print("账号或密码错误！")
            # return redirect(url_for('login'))
            return """ 账号或密码错误! <a href ="/login">点此返回登录</a>" """
        else:
            login_user(us)
            session['username'] = us.username
            session['password'] = us.password
            print(session)
            return redirect(url_for('home'))

    return render_template('login.html', error="账号或密码错误!")


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
    return render_template('index.html', USER=dict_A, session=session)


@app.route("/adduser", methods=["GET", "POST"])
@login_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        a = User(username=username, password=password)
        print("用户名：%s 密码： %s" % (a.username, a.password))
        db.session.add(a)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('adduser.html')


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """
    filter_by()：把等值过滤器添加到原查询上，返回一个新查询；
    filter()：把过滤器添加到原查询上，返回一个新查询。
    """
    name = request.args.get("name")
    print(name, request.args.get("name"), len(name), len(request.args.get("name")))
    a = User.query.filter_by(username=name).first()
    print(a)
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/change", methods=["GET", "POST"])
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
    return render_template('update_user.html', username=a.username, password=a.password)


# 设置文件上传保存路径
app.config['UPLOAD_FOLDER'] = './static/upload/'
# MAX_CONTENT_LENGTH设置上传文件的大小，单位字节
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def file_upload():
    if request.method == 'GET':
        tuple_A = db.session.query(UPLOAD_LOG.fileid, UPLOAD_LOG.filename, UPLOAD_LOG.Uploadtime,
                                   UPLOAD_LOG.userid).all()
        dict_h = ["fileid", "filename", "Uploadtime", "userid"]
        dict_A = []
        for tuple_i in tuple_A:
            list_s = []
            for list_i in list(tuple_i):
                if isinstance(list_i, datetime.datetime):
                    list_s.append(list_i.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    list_s.append(list_i)
            dict_A.append(dict(zip(dict_h, list_s)))
        return render_template('upload.html', filelist=dict_A)
    else:
        # file为上传表单的name属性值
        f = request.files['file']
        fname = secure_filename(f.filename)
        ext = fname.rsplit('.')[-1]
        # 生成一个uuid作为文件名
        fileName = str(uuid.uuid4()) + "." + ext

        # os.path.join拼接地址，上传地址，f.filename获取文件名
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))

        userid = session['username']
        dbi = UPLOAD_LOG(userid=userid, filename=str(fileName))
        db.session.add(dbi)
        db.session.commit()
        return 'ok'


# 下载
@app.route('/download/<filename>', methods=['GET'])
@login_required
def file_download(filename):
    if request.method == "GET":
        path = os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if path:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/del', methods=['GET'])
@login_required
def file_del():
    path = app.config['UPLOAD_FOLDER']
    name = request.args.get("name")
    print(name, path)
    a = UPLOAD_LOG.query.filter(UPLOAD_LOG.filename == name).first()
    print(a)
    db.session.delete(a)
    db.session.commit()
    os.remove(path + name)
    return name+"Delete Done."


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
def db_init():
    with app.app_context():
    #     # 删除表
        db.drop_all()
    with app.app_context():
        if os.path.exists("data.sqlite"):
            # 创建表
            # db.drop_all()
            db.create_all()
            a = User(username='101', password='1234')
            db.session.add(a)
            db.session.commit()
            print(User.query.all())
        # User.query.all()
        # User.query.filter_by(username=username).all()


if __name__ == '__main__':
    # db_init()
    app.run(debug=True, port=8000)
    # with app.app_context():
    #     name='7cca8d9c-af70-4acd-914d-76243de0ed6f.png'
    #     a = UPLOAD_LOG.query.filter(UPLOAD_LOG.filename == name).first()
    #     print(a)
