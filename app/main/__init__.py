#coding:utf-8
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors

'''
构造函数有两个必须指定的参数：蓝本的名字和蓝本所在的包或模块，大多数情况下第二个参数使用Python的__name__变量即可
views 和 errors模块咋脚本的末尾导入，是为了避免循环导入依赖。因为在views.py和errors.py中还要导入蓝本main
'''