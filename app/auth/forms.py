from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    """
    PasswordField类表示属性为type="password"的<input>元素
    BooleanField类表示复选框
    """
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    """
    Regexp验证函数，确保username字段只包含字母，数字，下划线和句点
    EqualTo该验证函数要附属到两个密码字段中的一个上，另一个字段作为参数传入
    """
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                     'usernames must have only letters,'
                                                                                     'number, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field): #验证邮箱是否存在
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field): #验证名字是否存在
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')


