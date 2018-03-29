# Promise-butler
[![Build Status](http://192.168.181.1:8080/jenkins/buildStatus/icon?job=promise-butler/dev)](http://192.168.181.1:8080/jenkins/job/promise-butler/job/dev/)

butler是promise的系统管理模块，包含权限与认证、用户管理、用户代办三个主要功能模块

## 接口列表

user模块：
* [user模块API]() 


## 模块索引
* [模块索引](http://192.168.182.52:8081/butler/)

## Prerequests

* python 2.7
* git
* easy_install && pip
* pyenv && pyenv-virtualenv
* 提供一个本地数据库用于执行本地单元测试，默认连接为“mysql://root@127.0.0.1:3306/test”

## Usage

### 基本用法

```bash
$ git clone git@192.168.182.51:promise/butler.git
$ git branch dev
$ cd butler
$ pip install -r requirements.txt
*(OSX10.10上PIL安装失败，需执行
 ln -s /usr/local/include/freetype2 /usr/local/include/freetype；   xcode-select --install)
*(centos7安装mysql-python失败，执行yum install python-devel mysql-devel)
$ python scripts/manager.py recreatedb
$ python runserver.py
```
出现如下提示表示运行正常：

```
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```

* 打开浏览器，访问："http://localhost:5000"
