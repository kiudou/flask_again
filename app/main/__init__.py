#coding:utf-8
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    """
    模板需要检查权限。为了避免每次调用render_template()时都多添加一个模板参数，
    使用上下文处理器，能让变量在所有模板中进行全局访问
    """
    return dict(Permission=Permission)

"""
构造函数有两个必须指定的参数：蓝本的名字和蓝本所在的包或模块，大多数情况下第二个参数使用Python的__name__变量即可
views 和 errors模块咋脚本的末尾导入，是为了避免循环导入依赖。因为在views.py和errors.py中还要导入蓝本main
"""