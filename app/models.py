#coding:utf-8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin

class Role(db.Model): #创建角色
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    #backref参数向User模型中添加一个role属性,从而定义反向关系,lazy='dynamic'禁止自动执行查询

    def __repr__(self): #返回可读性的字符串表示模型，__str__是面向用户的，而__repr__面向程序员
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles(): #角色的权限
        """
        insert_roles()并不直接创建新的角色对象，而是通过角色名查找现有的角色，然后在进行更新，
        只有当数据库中没有某个角色名时才会创建新的角色对象。
        这样以后更新角色列表，就可以执行更新操作。
        添加角色，更新操作，修改角色权限，修改roles数组，在运行函数即可
        """
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model): #UserMixin包含p82页的方法的默认实现
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Integer, unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)


    def __init__(self, **kwargs):
        """
        User类的构造函数首先调用基类的构造函数，如果创建基类对象后还没有定义角色，
        则根据电子邮件地址决定将其设为管理员还是默认角色
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']: #管理员由保存在设置变量FLASKY_ADMIN中的电子邮件地址识别
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()


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

    # 在请求和赋予角色这两种权限之间进行位与操作，如果角色中包含请求的所有权限位，则返回True,表示允许用户执行此操作
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

#程序不用先检查用户是否登陆，就能自由调用current_user.can()和current_user.ia_administrator
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser



"""
加载用户的回调函数接收以Unicode字符串形式表示的用户标识符。
如果能找到用户，这个函数必须返回用户对象，否则返回None
"""
@login_manager.user_loader #加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission: #操作的权限位
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80