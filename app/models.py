#coding:utf-8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Role(db.Model):
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    #backref参数向User模型中添加一个role属性,从而定义反向关系,lazy='dynamic'禁止自动执行查询

    def __repr__(self): #返回可读性的字符串表示模型，__str__是面向用户的，而__repr__面向程序员
        return '<Role %r>' % self.name

class User(UserMixin, db.Model): #UserMixin包含p82页的方法的默认实现
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Integer, unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)


    """
    计算密码散列值的函数通过名为password的只写属性实现。
    如果试图读取password属性的值，会返回错误，
    因为生成散列值后就无法还原成原来的密码了
    """
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    #https://stackoverflow.com/questions/47967921/after-use-generate-password-hashpassword-password-sequencethe-is-not-in-datab/47968258?noredirect=1#comment82907531_47968258
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<user %r>' % self.username

    def generate_confirmation_token(self, expiration=3600): #生成一个令牌，有效期为一个小时
        s = Serializer(current_app.config['SECRET_KEY'],expiration) #生成具有过期时间的JSON Web签名
        return s.dumps({'confirm': self.id})

    def confirm(self, token): #检验令牌，若检验通过，把新添加的confirmed的属性设为True
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


"""
加载用户的回调函数接收以Unicode字符串形式表示的用户标识符。
如果能找到用户，这个函数必须返回用户对象，否则返回None
"""
@login_manager.user_loader #加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))