# 程序结构 #

	

# 1.虚拟环境#

requirements.txt  用于记录所有依赖包及其精确的版本号

用以下命令将虚拟环境生成文件

	(venv) $ pip freeze >requirements.txt

创建新的虚拟环境，用以下命令

	(venv) $ pip install -r requirements.txt


----------
# 2.flash #

flash() 请求完成后，有时需要让用户知道状态发生了变化，使用确实，警告或者错误提醒

----------

# 3.数据库的迁移 #

	(venv) $ python hello.py db init
	(venv) $ python hello.py db migrate -m "initial migration"
	(venv) $ python hello.py db upgrade

命令含义：

init表示初始化迁移，创建migration文件夹

migrate根据model.py的结构变化更新迁移

upgrade会迁移最新版本的结构应用到数据库

----------
