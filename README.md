# flaskDemo

本接口项目的技术选型：Python+Flask+MySQL+Redis，通过 Python+Falsk 来开发接口，使用 MySQL 来存储用户信息，使用 Redis 用于存储token，目前为纯后端接口，暂无前端界面，可通过 Postman、Jmeter、Fiddler 等工具访问请求接口。

## 项目部署

首先，下载项目源码后，在根目录下找到 requirements.txt 文件，然后通过 pip 工具安装 requirements.txt 依赖，执行命令：

```
pip3 install -r requirements.txt
```

接着，将项目部署起来，在本项目中其实就是利用 Python 执行 app.py 文件，以下为我在Linux上的部署命令。

```
# /root/flaskDemo/app.py表示项目根路径下的app.py启动入口文件路径
# /root/flaskDemo/flaskDemo.log表示输出的日志文件路径
nohup python3 /root/flaskDemo/app.py >/root/flaskDemo/flaskDemo.log 2>&1 &
```

## 数据库设计

数据库建表语句如下：

```
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` tinyint(1) NOT NULL,
  `sex` tinyint(1) DEFAULT NULL,
  `telephone` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `telephone` (`telephone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

user表中各字段对应含义如下：

```
id：用户id号，自增长
username：用户名
password：密码
role：用户角色，0表示管理员用户，1表示普通用户
sex：性别，0表示男性，1表示女性，允许为空
telephone：手机号
address：联系地址，允许为空
```

## 接口请求示例

- 获取所有用户接口请求示例（可直接在浏览器输入栏请求）：

```
请求方式：GET
请求地址：http://127.0.0.1:9999/users
```

- 获取wintest用户接口请求示例（可直接在浏览器输入栏请求）：

```
请求方式：GET
请求地址：http://127.0.0.1:9999/users/wintest
```

- 用户注册接口请求示例：

```
请求方式：POST
请求地址：http://127.0.0.1:9999/register
请求头：
Content-Type: application/json

Body：{"username": "wintest5", "password": "123456", "sex": "1", "telephone":"13500010005", "address": "上海市黄浦区"}
```

- 用户登录接口请求示例：

```
请求方式：POST
请求地址：http://127.0.0.1:9999/login
请求头：
Content-Type: application/x-www-form-urlencoded

Body：username=wintest&password=123456
```

- 修改用户接口请求示例（ token 可以从用户登录成功后的接口返回数据中获取）：

```
请求方式：PUT
请求地址：http://127.0.0.1:9999/update/user/3
请求头：
Content-Type: application/json

Body：{"admin_user": "wintest", "token": "f54f9d6ebba2c75d45ba00a8832cb593", "sex": "1", "address": "广州市天河区", "password": "12345678", "telephone": "13500010003"}
```

- 删除用户接口请求示例（ token 可以从用户登录成功后的接口返回数据中获取）：：

```
请求方式：POST
请求地址：http://127.0.0.1:9999/delete/user/test
请求头：
Content-Type: application/json

Body：{"admin_user": "wintest", "token": "wintest1587830406"}
```
