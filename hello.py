#coding:utf-8
from flask import Flask, render_template,session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string' #app.config字典可用于储存框架，扩展和程序本身的配置变量
manager = Manager(app)
bootstrap = Bootstrap(app) #对flask-Bootstrap的初始化
moment =  Moment(app) #初始化

#render_template 返回的页面
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data: #比较与前一次提交的名字是否一致
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data #用户会话，用于储存请求之间需要记住的值的字典
        return redirect(url_for('index'))
        # 这里重定向URL是程序的根地址，推荐使用url_for(),保证URL和路由兼容,而且修改路由名字后依然可用
        # url_for()函数的第一个且唯一必须指定的参数是端点名，即路由的内部名字，默认下，路由端点为相应视图名字
        # 这个示例中，处理根地址的视图函数是index(),所以传给url_for()的名字是index
    return render_template('index.html',form=form, name=session.get('name'))

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)

#返回响应和错误状态码
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),

class NameForm(Form): #web表单
    # 文本字段,StringField表示属性为type="text"的<input>属性,可选参数validators指定一个由验证函数组成的列表
    # 接受用户提交数据之前验证数据，Required()确保提交的字段不为空
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit') #提交按钮,SubmitField表示属性为type="text"的<input>属性


if __name__=='__main__':
	app.run(debug=True) #True为启用调试模式
	
