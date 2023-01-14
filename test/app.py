# encoding=utf8
from flask import Flask, jsonify
from gevent import pywsgi
from flask_cors import CORS
from models import User
from dbs import mysql

app = Flask(__name__)
app.debug = True
app.config['JSON_AS_ASCII'] = False

# 这里连接串的意思是使用pymysql去连接mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3316/mytest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True

CORS(app, supports_credentials=True)
# init_app就是为了解决循环引用的
mysql.init_app(app)


@app.route("/")
def index():
    return success()

@app.route("/users")
def users():
    users = User.query.all()
    res = []
    for user in users:
        _res = {
            "id":user.id,
            "name":user.user_name
        }
        res.append(_res)
    return success(res)


def success(data=None):
    return response(0, "success", data)


def fail(msg):
    return response(-1, msg)


def response(code, msg, data=''):
    return jsonify({'code': code, 'msg': msg, 'data': data})


if __name__ == "__main__":
    print("开始启动web服务器...")
    server = pywsgi.WSGIServer(('0.0.0.0', 8088), app)
    server.serve_forever()