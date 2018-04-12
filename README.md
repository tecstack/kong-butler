# Kong-butler
Author: Shawn.T
email: dai.sheng@139.com

butler是基于Kong的用户管理微服务模块，包含权限与认证、用户管理等功能，实现微服务基础架构的快速构建。



## Usage
### Environments

* 开发时使用python 2.7
```bash
$ python --version
Python 2.7.8
```

* 下载及安装一些必要的python包
```bash
$ git clone git@github.com:tecstack/kong-butler.git
$ cd kong-butler && pip install -r requirements.txt
```

* 安装一个[kong](https://github.com/Kong/kong.git)服务

## Configurations
* 配置信息在config.py，一些必须的配置如下：
```python
# 数据库地址
SQLALCHEMY_DATABASE_URI = 'mysql://name:pass@yourmysql/butler'

# 设置kong管理接口
KONGADM_URL = 'http://testurl.com'
# 配置kong管理接口认证方式（butler当前支持keyauth或http basicauth）
KONGADM_APIKEY = None
KONGADM_BASICAUTH_USERNAME = None
KONGADM_BASICAUTH_PASSWORD = None
```

* 将后文api列表注册到kong中

## Usage

```bash
$ python scripts/manager.py recreatedb
$ python scripts/manager.py import_data
$ python runserver.py
```
出现如下提示表示运行正常：

```bash
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```

正式使用可使用supervisord：
* 1. 修改样例文件env.cnf中各文件路径
* 2. 使用supervisord启动服务
```bash
$ supervisord -c env.conf/supervisord.cnf
```

## 接口列表 butler API usage

### content

#### auth API
* [auth/](/README.md#usertoken)
    * [POST: user login]
    * [POST: token refresh]

#### current user API
* [user/myself](/README.md#)
    * [GET: get current user info]
    * [PUT: modf user_info of current user]

#### user management API
* [user/user](/docs/promise-back-api.user.md#useruser)
    * [POST: add new user](/docs/promise-back-api.user.md#post-add-new-user)
    * [GET: get infos of one user/all users](/docs/promise-back-api.user.md#get-get-infos-of-one-userall-users)
    * [PUT: update user info](docs/promise-back-api.user.md#put-update-user-info)
    * [DELETE: delete one user](docs/promise-back-api.user.md#delete-delete-one-user)
* [user/role](/docs/promise-back-api.user.md#userrole)
    * [POST: add new role](/docs/promise-back-api.user.md#post-add-new-role)
    * [GET: get infos of one role/all roles](/docs/promise-back-api.user.md#get-get-infos-of-one-roleall-roles)
    * [PUT: update role info](docs/promise-back-api.user.md#put-update-role-info)
    * [DELETE: delete one role](docs/promise-back-api.user.md#delete-delete-one-role)
* [user/privilege](/docs/promise-back-api.user.md#userprivilege)
    * [GET: get infos of one privilege/all privileges](/docs/promise-back-api.user.md#get-get-infos-of-one-privilegeall-privileges)
    * [PUT: update privilege info](/docs/promise-back-api.user.md#put-update-privilege-info)
* [user/list](/docs/promise-back-api.user.md#userlist)
    * [GET: get simply info of users](/docs/promise-back-api.user.md#get-get-simply-info-of-users)


API URL format: ```http://<ip:port>/api/<api version, like v0.0>/<uri>```
All API use **restful+json** protocal. All request header should contains:
```shell
Content-Type: application/json
```

## auth

### POST: user login
* Description: use username/password to login and return access token.
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | username | body | string | user login name |
    | password | body | string | user password |

* Request example:

    ```json
    {
        "password": "jerrypass",
        "username": "jerry"
    }
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info
    refreshtoken | body | string | a refresh token can be used to ask a new access token
    token | body | string | access token with user privilege info
    user_info | body | object | a object of user infomations
    email | body | string | email info in user_info object
    last_login | body | datetime | the user last login time in **user\_info** object
    privilege | body | object array | the user privielge object in the **user\_info** object
    role | body | object array | the user roles object in the **user\_info** object
    sign\_up\_date | body | datetime | the user sign up date in the **user\_info** object
    tel | body | string | the user telephone number in the **user\_info** object
    user_id | body | string | the user id in the **user\_info** object
    username | body | string | the login username in the **user\_info** object
    become_users | body | object array | 允许在walker/scene执行的对端用户


* Response example:

    ```json
    {
      "message": "user logged in.<user:admin>",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaXNzIjoiTDdGbVlDVTZMMElOWVRGaEhPOVR0cU9DWmFTNjMyQ2EiLCJ1c2VyX2lkIjoiYTk0ODVkYTYzYzhlMTFlOGI3YjhhNDVlNjBlZDVlZDUzOTdkN2MyODA2ZDQzODJkODg1NDRhZjNmMTQzZDk0NSIsIm5iZiI6MTUyMzUwMzY4MCwiZXhwIjoxNTIzNTA3MjgwfQ.k6gLdt_lMJDKB0C_w7edmUMzFBd4R-mZiLO6DduSPkI",
      "user_info": {
        "email": "",
        "enabled": true,
        "last_login": "Thu, 12 Apr 2018 03:27:59 GMT",
        "role": [
          {
            "description": "\u8d85\u7ea7\u7528\u6237",
            "role_id": "553a07823c8e11e8abd1a45e60ed5ed51ff04c8323083f2681ffdedfd3031b85",
            "role_name": "root"
          }
        ],
        "sign_up_date": "Tue, 10 Apr 2018 15:13:26 GMT",
        "tel": "",
        "user_id": "a9485da63c8e11e8b7b8a45e60ed5ed5397d7c2806d4382d88544af3f143d945",
        "username": "admin"
      }
    }
    ```

### POST: token refresh
* Description: use token to ask a new token.
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    Name | In | Type | description
    ---- | --- | ---- | -----------
    refreshtoken | header | string | token

* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info
    token | body | string | a new access token which has a whole access token expired duration
    user_info | body | json | current user info

* Response example:

    ```json
    {
      "message": "user reflesh token.<user:admin>",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaXNzIjoiN1gzMHdJYUFFa2NGOFo4WWlVaEJNUGN6dHE3VXhIMmQiLCJ1c2VyX2lkIjoiYTk0ODVkYTYzYzhlMTFlOGI3YjhhNDVlNjBlZDVlZDUzOTdkN2MyODA2ZDQzODJkODg1NDRhZjNmMTQzZDk0NSIsIm5iZiI6MTUyMzUwMzY4MywiZXhwIjoxNTIzNTA3MjgzfQ.C1nbxzENZGCq-DZCzTLsTfM4MdOoTiTnJ8oLiyOV5A8",
      "user_info": {
        "email": "",
        "enabled": true,
        "last_login": "Thu, 12 Apr 2018 03:27:59 GMT",
        "role": [
          {
            "description": "\u8d85\u7ea7\u7528\u6237",
            "role_id": "553a07823c8e11e8abd1a45e60ed5ed51ff04c8323083f2681ffdedfd3031b85",
            "role_name": "root"
          }
        ],
        "sign_up_date": "Tue, 10 Apr 2018 15:13:26 GMT",
        "tel": "",
        "user_id": "a9485da63c8e11e8b7b8a45e60ed5ed5397d7c2806d4382d88544af3f143d945",
        "username": "admin"
      }
    }
    ```

## user/mysql

### GET: get current user info
* Description: use token to login and get user info
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    Name | In | Type | description
    ---- | --- | ---- | -----------
    token | header | string | access token

* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info
    token | body | string | access token with user privilege info
    user_info | body | object | a object of user infomations
    email | body | string | email info in user_info object
    last_login | body | datetime | the user last login time in **user\_info** object
    role | body | object array | the user roles object in the **user\_info** object
    sign\_up\_date | body | datetime | the user sign up date in the **user\_info** object
    tel | body | string | the user telephone number in the **user\_info** object
    user_id | body | string | the user id in the **user\_info** object
    username | body | string | the login username in the **user\_info** object
    enabled | body | bollean | status of user


* Response example:

    ```json
    {
      "message": "user token refresh.<username:admin>",
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaXNzIjoiTDdGbVlDVTZMMElOWVRGaEhPOVR0cU9DWmFTNjMyQ2EiLCJ1c2VyX2lkIjoiYTk0ODVkYTYzYzhlMTFlOGI3YjhhNDVlNjBlZDVlZDUzOTdkN2MyODA2ZDQzODJkODg1NDRhZjNmMTQzZDk0NSIsIm5iZiI6MTUyMzUwMzY4MCwiZXhwIjoxNTIzNTA3MjgwfQ.k6gLdt_lMJDKB0C_w7edmUMzFBd4R-mZiLO6DduSPkI",
      "user_info": {
        "email": "admin@butler.com",
        "enabled": true,
        "last_login": "Thu, 12 Apr 2018 03:27:59 GMT",
        "role": [
          {
            "description": "\u8d85\u7ea7\u7528\u6237",
            "role_id": "553a07823c8e11e8abd1a45e60ed5ed51ff04c8323083f2681ffdedfd3031b85",
            "role_name": "root"
          }
        ],
        "sign_up_date": "Tue, 10 Apr 2018 15:13:26 GMT",
        "tel": "",
        "user_id": "a9485da63c8e11e8b7b8a45e60ed5ed5397d7c2806d4382d88544af3f143d945",
        "username": "admin"
      }
    }

### PUT: modf current user_info of token owner
* Description: decode token and modf the infomation of the token owner user.
* Needed privileges: None
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

	Name | In | Type | description
    ---- | --- | ---- | -----------
	token | header | string | access token
    user_info | body | object | a object of user infomations
    username(optional) | body | string | the login username in the **user\_info** object
    password(optional) | body | string | the login password in the **user\_info** object
    email(optional) | body | string | email info in **user_info** object
    tel(optional) | body | string | the user telephone number in the **user\_info** object

* Request example:

    ```json
    {
      "tel": "13811111111"
    }
    ```

* Response format:

    Name | In | Type | description
	---- | --- | ---- | -----------
    message | body | string | response info
    user_id | body | string | the user id in the **user\_info** object

* Response example:

    ```json
    {
      "message": "current user info updated.",
      "user_id": "cfb0032e28dd11e7b0ec0242ac110006efe3a2562fb93580a7b9b6bfdcffda71"
    }
    ```

## user/user

### POST: add new user
* Description: add new user
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | username | body | string | user login name |
    | password | body | string | user password |
    | role\_ids | body | list | role id list|
    | email | body | string | |
    | tel | body | string | |

* Request example:

    ```json
    {
      "username": "Michel56",
      "password": "Michelpass",
      "role\_id_list": [
        "8176154a289211e7a56e0242ac1100061ff04c8323083f2681ffdedfd3031b85",
        "81761f9a289211e7a56e0242ac110006bb736b09af543a39b46887d2a55cf9ef"
      ]
    }
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    user_id | body | string | id of new user |


* Response example:

    ```json
    {
      "message": "user<user_id:fd57575a289211e79b990242ac110003c4b0f32903e030fda6ea86b971604317> created.",
      "user_id": "fd57575a289211e79b990242ac110003c4b0f32903e030fda6ea86b971604317"
    }
    ```


### GET: get infos of one user/all users
* Description: get infos of one user/all users
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | user_id(optional) | URL Params | string | return info of all users, if user\_id is not given|


* Request example:

    ```
    request url:
    /api/v0.0/user/user?user_id=31d023683cb311e8b628a45e60ed5ed5b0607ac140d73b9d85ad88580081131a
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    user_info | body | object | infomations of target user |


* Response example:

    ```json
    {
      "message": "user infomation.<user:paw-test-user>",
      "user_info": {
        "email": "",
        "enabled": true,
        "last_login": "",
        "role": [],
        "sign_up_date": "Tue, 10 Apr 2018 19:34:57 GMT",
        "tel": "",
        "user_id": "31d023683cb311e8b628a45e60ed5ed5b0607ac140d73b9d85ad88580081131a",
        "username": "paw-test-user"
      }
    }
    ```

### PUT: update user info
* Description: update user info
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | user_id | URL Params | string | user\_id of target user |
    | username(optional) | body | string | new login username |
    | password(optional) | body | string | new user password |
    | role\_ids(optional) | body | list | new role id list|
    | email(optional) | body | string | new email address|
    | tel(optional) | body | string | new tel numb |

* Request example:

    ```json
    {
    	"password":"paw-test-user1",
    	"username":"paw-test-user2",
    	"role_ids":[""]
    }
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    user_id | body | string | id of new user |


* Response example:

    ```json
    {
      "message": "user updated.<user:31d023683cb311e8b628a45e60ed5ed5b0607ac140d73b9d85ad88580081131a>",
      "user_id": "31d023683cb311e8b628a45e60ed5ed5b0607ac140d73b9d85ad88580081131a"
    }
    ```

## user/role

### POST: add a new role
* Description: add a new role
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | role_name | body | string | new role name |
    | description | body | string | role description |
    | privilege\_id_list | body | list | privileges to this new role|
    | user\_id_list | body | list | users to this new role |
    | become_users（可选） | body | list | 用户在walker/scene模块可用的对端主机用户 |

* Request example:

    ```json
    {
      "role_name": "paw-test-role1",
      "user_ids": [
        "31d023683cb311e8b628a45e60ed5ed5b0607ac140d73b9d85ad88580081131a"
      ],
      "api_ids": [
        "e64d40a4-59bb-43c7-a382-7cb5190558bc"
      ]
    }
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    role_id | body | string | id of new role |


* Response example:

    ```json
    {
      "message": "role created.",
      "role_id": "1e6e78823cbb11e88384a45e60ed5ed5a50bdb24974a3afc966ee4018f5c7c60"
    }
    ```

### GET: get infos of one role/all roles
* Description: get infos of one/all roles
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | role_id(optional) | URL Params | string | return info of all roles, if role\_id is not given |


* Request example:

    ```
    request url:
    /api/v0.0/user/role?role_id=1e6e78823cbb11e88384a45e60ed5ed5a50bdb24974a3afc966ee4018f5c7c60
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    role_info | body | object | infomations of target role |


* Response example:

    ```json
    {
      "message": "role infomation.<role:paw-test-role1>",
      "role_info": {
        "api": [
          {
            "created_at": 1520066613670,
            "hosts": {},
            "http_if_terminated": false,
            "https_only": false,
            "id": "c3e70c26-cb16-46d7-895d-76bb73bec2df",
            "name": "kongadm",
            "preserve_host": false,
            "retries": 5,
            "strip_uri": true,
            "upstream_connect_timeout": 60000,
            "upstream_read_timeout": 60000,
            "upstream_send_timeout": 60000,
            "upstream_url": "http://192.168.182.82:8001",
            "uris": [
              "/kongadm"
            ]
          }
        ],
        "description": "",
        "enabled": true,
        "role_id": "1e6e78823cbb11e88384a45e60ed5ed5a50bdb24974a3afc966ee4018f5c7c60",
        "role_name": "paw-test-role1",
        "user": [
          {
            "consumer_id": "9fbdaa65-7311-4517-ab4e-1ea3499fdfa3",
            "email": "",
            "hashed_password": "98e73a0a623f17f9a86ac5fc0a2a4500",
            "last_login": "",
            "sign_up_date": "Tue, 10 Apr 2018 15:13:26 GMT",
            "tel": "",
            "user_id": "a9485da63c8e11e8b7b8a45e60ed5ed5397d7c2806d4382d88544af3f143d945",
            "username": "admin"
          }
        ]
      }
    }
    ```

### PUT: update role info
* Description: update role info
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |
    | role_id | URL Params | string | id of target role |
    | role_name(optional) | body | string | new role name |
    | privilege\_id_list(optional) | body | list | new privileges to the target role |
    | user\_ids(optional) | body | list | new users to the target role |
    | become_users（可选） | body | list | 用户在walker/scene模块可用的对端主机用户 |

* Request example:

    ```json
    {
      "role_name": "role4",
      "user\_ids": [
        "81911598289211e7a56e0242ac110006f973ba0fcf783bb8ade34c7b492d9e55"
      ]
    }
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    role_id | body | string | id of updated role |


* Response example:

    ```json
    {
      "message": "role updated.<role:fef84614289211e7997b0242ac110003a3a3183ef5cd31858641c8ee1c4b67a1>",
      "role_id": "fef84614289211e7997b0242ac110003a3a3183ef5cd31858641c8ee1c4b67a1"
    }
    ```

## user/api

### GET: list all apis
* Description: get infos of all apis setted in kong
* Needed privileges: userAdmin
* Normal response code：200
* Error response code：400,401,404,405,409,500,503
* Request format：

    | Name |  In | Type | description |
    | ---- | --- | ---- | ----------- |
    | token | header | string | access token |

* Request example:

    ```
    request url:
    /api/v0.0/user/api
    ```
* Response format:

    Name | In | Type | description
    ---- | --- | ---- | -----------
    message | body | string | response info |
    privilege_info | body | object | infomations of target privilege |
    privilege_list | body | list | infomations of all privileges |


* Response example:

    ```json
    {
      "message": "privilege infomation<privilege:userAdmin>.",
      "api_list": [
        {
          "created_at": 1520066613670,
          "hosts": {},
          "http_if_terminated": false,
          "https_only": false,
          "id": "c3e70c26-cb16-46d7-895d-76bb73bec2df",
          "name": "kongadm",
          "preserve_host": false,
          "retries": 5,
          "strip_uri": true,
          "upstream_connect_timeout": 60000,
          "upstream_read_timeout": 60000,
          "upstream_send_timeout": 60000,
          "upstream_url": "http://192.168.182.82:8001",
          "uris": [
            "/kongadm"
          ]
        }
      ]
    }
    ```
