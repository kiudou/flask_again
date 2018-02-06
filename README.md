# 登陆账号 #
克隆该项目到本地后，因为该项目里已包含虚拟环境和数据库，所以进入虚拟环境，直接运行manager.py文件，登陆账号即可，该账号为管理员账号

账号：1@1.com

密码：1

----------

# 运行 #
打开终端，在当前文件夹下，进入虚拟环境，执行

	venv\Scripts\activate #windows
	source venv/bin/activate #max or linux

运行manager.py文件,执行
	
	python manager,py

打开浏览器，输入127.0.0.1:5000即可进入

----------


# 程序结构 #


![结构](http://r.photo.store.qq.com/psb?/V13zmFZT2vlTI6/71FqoA7WZHHsvxboxXCLv8YdZcPc78TCYasNvmpqGaw!/r/dD8BAAAAAAAA)
	
http://r.photo.store.qq.com/psb?/V13zmFZT2vlTI6/71FqoA7WZHHsvxboxXCLv8YdZcPc78TCYasNvmpqGaw!/r/dD8BAAAAAAAA

----------

# 1.虚拟环境#

requirements.txt  用于记录所有依赖包及其精确的版本号

用以下命令将虚拟环境生成文件

	(venv) $ pip freeze > requirements.txt

创建新的虚拟环境，用以下命令

	(venv) $ pip install -r requirements.txt



# 2.数据库的迁移 #

	(venv) $ python hello.py db init
	(venv) $ python hello.py db migrate -m "initial migration"
	(venv) $ python hello.py db upgrade

命令含义：

init表示初始化迁移，创建migration文件夹

migrate根据model.py的结构变化更新迁移

upgrade会迁移最新版本的结构应用到数据库

### 如果之前已经创建过migrations，则只要使用后两步就行 ###

----------
