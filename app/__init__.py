#coding:utf-8
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

def create_app(config_name):
	'''
	配置类在config.py中定义，其中保存的配置可以使用Flask app.config配置对象提供的from_object()方法直接导入程序。
	配置对象则可以通过名字从config字典中选择
	'''
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)


	return app