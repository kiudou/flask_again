#coding:utf-8
from flask import Flask
from flask import render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app) #对flask-Bootstrap的初始化
moment =  Moment(app) #初始化
#render_template 返回的页面
@app.route('/')
def index():
    return render_template('index.html',current_time = datetime.utcnow()) #返回时间

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 #返回响应和错误状态码

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),




if __name__=='__main__':
	app.run(debug=True) #True为启用调试模式
	
