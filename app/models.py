#coding:utf-8
from . import db

class Role(db.Model):
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    #backref参数向User模型中添加一个role属性,从而定义反向关系,lazy='dynamic'禁止自动执行查询

    def __repr__(self): #返回可读性的字符串表示模型，__str__是面向用户的，而__repr__面向程序员
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<user %r>' % self.username