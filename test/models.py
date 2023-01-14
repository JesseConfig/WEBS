from dbs import mysql

class User(mysql.Model):
    __tablename__ = 'user'
    id = mysql.Column(mysql.Integer, primary_key=True)
    user_name = mysql.Column(mysql.String(255))