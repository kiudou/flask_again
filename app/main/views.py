#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for

from . import main
from .forms import NameForm
from ..email import send_email
from .. import db
from ..models import User

@main.route('/',methods=['GET', 'POST'])
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
        return redirect(url_for('.index'))
        # 这里重定向URL是程序的根地址，推荐使用url_for(),保证URL和路由兼容,而且修改路由名字后依然可用
        # url_for()函数的第一个且唯一必须指定的参数是端点名，即路由的内部名字，默认下，路由端点为相应视图名字
        # 这个示例中，处理根地址的视图函数是index(),所以传给url_for()的名字是index
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known',False), current_time=datetime.utcnow())