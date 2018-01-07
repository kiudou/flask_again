#coding:utf-8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
import hashlib
from flask import request
from markdown import markdown
import bleach

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model): #文章模型
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    # @staticmethod
    # def generate_fake(count=100):
    #     from random import seed, randint
    #     import forgery_py
    #
    #     seed()
    #     user_count = User.query.count()
    #     for i in range(count):
    #         u = User.query.offset(randint(0, user_count -1)).first() #该过滤器会跳过参数中制定的记录数量，设定偏移值，获得一个不同的随机用户
    #         p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
    #                  timestamp=forgery_py.date.date(True),
    #                  author=u)
    #         db.session.add(p)
    #         db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
                        'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)

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


    name = db.Column(db.String(64)) #真是姓名
    location = db.Column(db.String(64)) #所在地
    about_me = db.Column(db.Text()) #自我介绍，string和text的区别是后者不需要指定最大长度
    member_since = db.Column(db.DateTime(), default=datetime.utcnow) #注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow) #最后访问时间
    avatar_hash = db.Column(db.String(32)) #使用缓存的MD5散列值生成Gravatar URL
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'), #回引Follow模型
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed',lazy='joined'), #joined，立即从联结查询中加载相关对象
                               lazy='dynamic',
                               cascade='all, delete-orphan')

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
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

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
        print(self.role)
        return True
        return self.role is not None and (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    #刷新用户的最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'): #构建gravatar URL,用于生成头像
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'https://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    # @staticmethod #生成虚拟用户和博客文章
    # def generate_fake(count=100):
    #     from sqlalchemy.exc import IntegrityError
    #     from random import seed
    #     import forgery_py
    #
    #     seed() #seed() 方法改变随机数生成器的种子，可以在调用其他随机模块函数之前调用此函数
    #     for i in range(count): #信息随机生成
    #         u = User(email=forgery_py.internet.email_address(),
    #                  username=forgery_py.internet.user_name(),
    #                  password=forgery_py.lorem_ipsum.word(),
    #                  confirmed=True,
    #                  name=forgery_py.name.full_name(),
    #                  location=forgery_py.address.city(),
    #                  about_me=forgery_py.lorem_ipsum.sentence(),
    #                  member_since=forgery_py.date.date(True))
    #         db.session.add(u)
    #         try:
    #             db.session.commit()
    #         except IntegrityError:
    #             db.session.rollback() #如果信息有重复的，则进行回滚，不写入数据库

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property #已定义为属性，所以调用时不添加()
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)


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



