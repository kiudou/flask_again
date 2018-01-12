#coding:utf-8
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash,current_app, request, make_response
from flask import abort
from flask_login import login_required, current_user
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm, PostForm, CommentForm
from ..email import send_email
from .. import db
from ..models import User, Permission, Post, Comment
from ..decorators import admin_required, permission_required


@main.route('/',methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int) #默认为第一页，type=int参数表示无法转换成整数时，返回默认值
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate( #为了显示某页中的记录，用paginate
        page, per_page=20,error_out=False) #False页数超出范围返回空列表,True页数超出范围，返回404错误
    posts = pagination.items #当前页面中的记录
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination)

#对于名为john的用户，资料页面为http://localhost:5000/user/john
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=20,error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts, pagination=pagination)


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

@main.route('/post/<int:id>', methods=['GET', 'POST']) #博客文章的URL由插入数据库时分配的唯一id构建
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object()) #current_user是上下文代理对象，得用_get方法
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has benen published')
        return redirect(url_for('.post', id=post.id, page= -1)) #-1表示最后一页
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count()-1) // 21
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=20,error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id): #作者编辑文章
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER): #其他人无法编辑，除了作者和管理员
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been update!')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username): #关注用户
    """
     该视图函数先加载请求的用户，确保当前用户存在且当前登陆用户还没有关注这个用户，
     然后调用User模型中定义的辅助方法follow()
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this year')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' %username)
    return redirect(url_for('.user', username= username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username): #取注用户
    """
     该视图函数先加载请求的用户，确保当前用户存在且当前登陆用户还没有关注这个用户，
     然后调用User模型中定义的辅助方法follow()
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s.' %username)
    return redirect(url_for('.user', username= username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, tpye=int)
    pagination = user.followers.paginate(
        page, per_page=20, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='.followers', pagination=pagination, follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=20, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60) #前俩参数是cookie的名和值，最后一个是过期时间
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp