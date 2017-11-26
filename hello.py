#coding:utf-8
from flask import Flask, render_template,session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Shell
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite') #数据库URL保存
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True #True代表每次请求结束后都会自动提交数据库的变动
app.config['SECRET_KEY'] = 'hard to guess string' #app.config字典可用于储存框架，扩展和程序本身的配置变量
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 配置Flask-Mail 使用Gmail和集成发
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN') #邮件的收件人管理员
#集成发送电子邮件功能
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' #邮件主题的前缀
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>' #发件人的地址


mail = Mail(app)
bootstrap = Bootstrap(app) #对flask-Bootstrap的初始化
moment =  Moment(app) #初始化
db = SQLAlchemy(app) #db是SQLAlchemy的实例表示程序使用的数据库，还获得Flask-SQLAlchemy提供的所有功能
migrate = Migrate(app,db)
manager.add_command('db', MigrateCommand)


#把对象添加到导入列表中，为shell函数注册一个回调函数
def make_shell_context(): #注册了程序，数据库实例以及模型
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg) #使用current_app,所以必须激活程序上下文

#函数参数为收件人的地址，主题，渲染邮件正文的模板，关键字参数列表，异步发送邮件
def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

#render_template 返回的页面
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data  # 用户会话，用于储存请求之间需要记住的值的字典
        form.name.data = ''
        return redirect(url_for('index'))
        # 这里重定向URL是程序的根地址，推荐使用url_for(),保证URL和路由兼容,而且修改路由名字后依然可用
        # url_for()函数的第一个且唯一必须指定的参数是端点名，即路由的内部名字，默认下，路由端点为相应视图名字
        # 这个示例中，处理根地址的视图函数是index(),所以传给url_for()的名字是index
    return render_template('index.html',form=form, name=session.get('name'), known=session.get('known',False))

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

class Role(db.Model):
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    #backref参数向User模型中添加一个role属性,从而定义反向关系,lazy='dynamic'禁止自动执行查询

    def __repr__(self): #返回可读性的字符串表示模型，__str__是面向用户的，而__repr__面向程序员
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<user %r>' % self.username


if __name__ == '__main__':
    #app.run(debug=True) #True为启用调试模式
	manager.run()