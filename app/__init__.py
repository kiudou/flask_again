#coding:utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown =PageDown()

login_manager = LoginManager()
#提供None,basic,strong设置不同安全等级防止用户会话遭篡改
#当为strong时，Flask-Login会记录客户端IP地址和浏览器的用户代理信息，如果发现异动就登出
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    """
    配置类在config.py中定义，其中保存的配置可以使用Flask app.config配置对象提供的from_object()方法直接导入程序。
    配置对象则可以通过名字从config字典中选择
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint #auth蓝本要在create_app()工厂函数中附加到程序上
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    """
    使用url_prefix,注册蓝本中定义的所有路由都会加上指定的前缀
    例如该例子/login路由会注册成/auth/login，web中完整路径为http://localhost:5000/auth/login
    """

    login_manager.init_app(app)
    return app


