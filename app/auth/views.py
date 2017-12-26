from flask import render_template, redirect, request, url_for, flash
from . import auth
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..email import send_email
from flask_login import current_user


#蓝本中的路由和视图函数
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    请求类型是GET时，视图函数会直接渲染模板，显示表。
    当为POST时，Flask-WTK中的validate_on_submit()函数会验证表单数据，然后登陆用户
    用户访问未授权的URL时会显示登陆表单，Flask-Login会把原地址保存在查询字符串的next参数中
    这个参数可从request.args字典中读取，如果查询字符串没有next参数，则重定向到首页
    如果密码或电子邮箱不对，程序设定一个flash消息，再次渲染表单，让用户重试登陆
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password,')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    用Flask-Login中的logout_user()函数，删除并重设用户会话
    然后显示flash，确认这次操作，在重定向回到首页
    """
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data) #一定用password，不用password_hash
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm',user=user, token=token)
        flash('A confirmation email has been sent to you by email')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required #该修饰器会保护路由
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account, Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#针对程序全局请求的钩子
@auth.before_app_request
def before_request():
    """
    满足下列三个条件，before_app_request处理程序会拦截请求
    1 用户已登陆
    2 用户账户还没有确认
    3 请求的端点不在认证蓝本中，访问认证路由要获取权限，\
        因为这些路由的作用是让用户确认账户或执行其他账户管理操作
    """
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


#current_user为已登陆用户或者目标用户
#该路由为current_user重做了一遍注册路由中的操作
@auth.route('/confirm')
@login_required #保护路由，确保访问时程序知道请求再次发送邮件的是哪个用户
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.mail, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))

