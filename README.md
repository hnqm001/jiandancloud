#JandanCloud
======
JandanCloud·简单云
这是一个flask web项目

##安装
```
$ git clone https://github.com/hnqm001/jiandancloud.git
$ cd jiandancloud
$ pipenv install --dev
$ pipenv shell
$ flask initdb
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/
```
--------------------------------------------
本项目源码内容借鉴《Flask Web开发》与《Flask Web开发实战》二书
如果执行`pipenv install`命令安装依赖耗时太长，你可以考虑使用国内的PyPI镜像源，比如：
```
$ pipenv install --dev --pypi-mirror https://mirrors.aliyun.com/pypi/simple
```
