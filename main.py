from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__,template_folder="./templates/")

@app.route('/')
def log1():
    return render_template("login.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True,port=8000)
