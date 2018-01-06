#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_wtf import Form
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from flask_pagedown.fields import PageDownField

class NameForm(Form): #web登陆表单
    # 文本字段,StringField表示属性为type="text"的<input>属性,可选参数validators指定一个由验证函数组成的列表
    # 接受用户提交数据之前验证数据，Required()确保提交的字段不为空
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit') #提交按钮,SubmitField表示属性为type="text"的<input>属性

#用户表单
class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('about me')
    submit = SubmitField('Submit')


#管理员表单
class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form): #博客文章表单
    body = PageDownField("what's on your mind?", validators=[Required()])
    submit = SubmitField('submit')


