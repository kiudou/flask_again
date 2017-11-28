#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_wtf import Form
class NameForm(Form): #web表单
    # 文本字段,StringField表示属性为type="text"的<input>属性,可选参数validators指定一个由验证函数组成的列表
    # 接受用户提交数据之前验证数据，Required()确保提交的字段不为空
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit') #提交按钮,SubmitField表示属性为type="text"的<input>属性