#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask import abort
from flask_login import login_required, current_user
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm
from ..email import send_email
from .. import db
from ..models import User
from ..decorators import admin_required

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

#对于名为john的用户，资料页面为http://localhost:5000/user/john
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


#普通用户路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has benn updated')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


#管理员的资料编辑器路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id) #如果提供id不正确，则返回404错误
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

