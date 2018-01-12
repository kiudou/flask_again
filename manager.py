import os
from app import create_app, db
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
"""
若已经定义环境变量FLASK_CONFIG，则从中读取配置名，否则使用，默认配置.
然后初始化Flask-Script,Flask-Migrate和为Python shell定义的上下文
"""
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# 把对象添加到导入列表中，为shell函数注册一个回调函数
@app.shell_context_processor
def make_shell_context(): #注册了程序，数据库实例以及模型
    return dict(db=db, User=User, Role=Role)
#manager.add_command("shell", Shell(make_context=make_shell_context))
#manager.add_command('db', MigrateCommand)

@app.cli.command()
def test():
    # Run the unit tests
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
 
if __name__ == '__main__':
    app.run(debug=True)
    #manager.run()
