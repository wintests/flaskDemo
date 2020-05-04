from flask import Flask, jsonify, request
from common.mysql_operate import db
from common.redis_operate import redis_db
from common.md5_operate import get_md5
import re, time

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # jsonify返回的中文正常显示


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/users", methods=["GET"])
def get_all_users():
    """获取所有用户信息"""
    sql = "SELECT * FROM user"
    data = db.select_db(sql)
    print("获取所有用户信息 == >> {}".format(data))
    return jsonify({"code": 0, "data": data, "msg": "查询成功"})


@app.route("/users/<string:username>", methods=["GET"])
def get_user(username):
    """获取某个用户信息"""
    sql = "SELECT * FROM user WHERE username = '{}'".format(username)
    data = db.select_db(sql)
    print("获取 {} 用户信息 == >> {}".format(username, data))
    if data:
        return jsonify({"code": 0, "data": data, "msg": "查询成功"})
    return jsonify({"code": "1004", "msg": "查不到相关用户的信息"})


@app.route("/register", methods=['POST'])
def user_register():
    """注册用户"""
    username = request.json.get("username", "").strip()  # 用户名
    password = request.json.get("password", "").strip()  # 密码
    sex = request.json.get("sex", "0").strip()  # 性别，默认为0(男性)
    telephone = request.json.get("telephone", "").strip()  # 手机号
    address = request.json.get("address", "").strip()  # 地址，默认为空串
    if username and password and telephone: # 注意if条件中 "" 也是空, 按False处理
        sql1 = "SELECT username FROM user WHERE username = '{}'".format(username)
        res1 = db.select_db(sql1)
        print("查询到用户名 ==>> {}".format(res1))
        sql2 = "SELECT telephone FROM user WHERE telephone = '{}'".format(telephone)
        res2 = db.select_db(sql2)
        print("查询到手机号 ==>> {}".format(res2))
        if res1:
            return jsonify({"code": 2002, "msg": "用户名已存在，注册失败！！！"})
        elif not (sex == "0" or sex == "1"):
            return jsonify({"code": 2003, "msg": "输入的性别只能是 0(男) 或 1(女)！！！"})
        elif not (len(telephone) == 11 and re.match("^1[3,5,7,8]\d{9}$", telephone)):
            return jsonify({"code": 2004, "msg": "手机号格式不正确！！！"})
        elif res2:
            return jsonify({"code": 2005, "msg": "手机号已被注册！！！"})
        else:
            password = get_md5(username, password) # 把传入的明文密码通过MD5加密变为密文，然后再进行注册
            sql3 = "INSERT INTO user(username, password, role, sex, telephone, address) " \
                  "VALUES('{}', '{}', '1', '{}', '{}', '{}')".format(username, password, sex, telephone, address)
            db.execute_db(sql3)
            print("新增用户信息SQL ==>> {}".format(sql3))
            return jsonify({"code": 0, "msg": "恭喜，注册成功！"})
    else:
        return jsonify({"code": 2001, "msg": "用户名/密码/手机号不能为空，请检查！！！"})


@app.route("/login", methods=['POST'])
def user_login():
    """登录用户"""
    username = request.values.get("username", "").strip()
    password = request.values.get("password", "").strip()
    if username and password: # 注意if条件中空串 "" 也是空, 按False处理
        sql1 = "SELECT username FROM user WHERE username = '{}'".format(username)
        res1 = db.select_db(sql1)
        print("查询到用户名 ==>> {}".format(res1))
        if not res1:
            return jsonify({"code": 1003, "msg": "用户名不存在！！！"})
        md5_password = get_md5(username, password) # 把传入的明文密码通过MD5加密变为密文
        sql2 = "SELECT * FROM user WHERE username = '{}' and password = '{}'".format(username, md5_password)
        res2 = db.select_db(sql2)
        print("获取 {} 用户信息 == >> {}".format(username, res2))
        if res2:
            timeStamp = int(time.time()) # 获取当前时间戳
            # token = "{}{}".format(username, timeStamp)
            token = get_md5(username, str(timeStamp)) # MD5加密后得到token
            redis_db.handle_redis_token(username, token) # 把token放到redis中存储
            login_info = { # 构造一个字段，将 id/username/token/login_time 返回
                "id": res2[0]["id"],
                "username": username,
                "token": token,
                "login_time": time.strftime("%Y/%m/%d %H:%M:%S")
            }
            return jsonify({"code": 0, "login_info": login_info, "msg": "恭喜，登录成功！"})
        return jsonify({"code": 1002, "msg": "用户名或密码错误！！！"})
    else:
        return jsonify({"code": 1001, "msg": "用户名或密码不能为空！！！"})

@app.route("/update/user/<int:id>", methods=['PUT'])
def user_update(id): # id为准备修改的用户ID
    """修改用户信息"""
    admin_user = request.json.get("admin_user", "").strip() # 当前登录的管理员用户
    token = request.json.get("token", "").strip()  # token口令
    new_password = request.json.get("password", "").strip()  # 新的密码
    new_sex = request.json.get("sex", "0").strip()  # 新的性别，如果参数不传sex，那么默认为0(男性)
    new_telephone = request.json.get("telephone", "").strip()  # 新的手机号
    new_address = request.json.get("address", "").strip()  # 新的联系地址，默认为空串
    if admin_user and token and new_password and new_telephone: # 注意if条件中空串 "" 也是空, 按False处理
        if not (new_sex == "0" or new_sex == "1"):
            return jsonify({"code": 4007, "msg": "输入的性别只能是 0(男) 或 1(女)！！！"})
        elif not (len(new_telephone) == 11 and re.match("^1[3,5,7,8]\d{9}$", new_telephone)):
            return jsonify({"code": 4008, "msg": "手机号格式不正确！！！"})
        else:
            redis_token = redis_db.handle_redis_token(admin_user) # 从redis中取token
            if redis_token:
                if redis_token == token: # 如果从redis中取到的token不为空，且等于请求body中的token
                    sql1 = "SELECT role FROM user WHERE username = '{}'".format(admin_user)
                    res1 = db.select_db(sql1)
                    print("根据用户名 【 {} 】 查询到用户类型 == >> {}".format(admin_user, res1))
                    user_role = res1[0]["role"]
                    if user_role == 0: # 如果当前登录用户是管理员用户
                        sql2 = "SELECT * FROM user WHERE id = '{}'".format(id)
                        res2 = db.select_db(sql2)
                        print("根据用户ID 【 {} 】 查询到用户信息 ==>> {}".format(id, res2))
                        sql3 = "SELECT telephone FROM user WHERE telephone = '{}'".format(new_telephone)
                        res3 = db.select_db(sql3)
                        print("返回结果：{}".format(res3))
                        print("查询到手机号 ==>> {}".format(res3))
                        if not res2: # 如果要修改的用户不存在于数据库中，res2为空
                            return jsonify({"code": 4005, "msg": "修改的用户ID不存在，无法进行修改，请检查！！！"})
                        elif res3: # 如果要修改的手机号已经存在于数据库中，res3非空
                            return jsonify({"code": 4006, "msg": "手机号已被注册，无法进行修改，请检查！！！"})
                        else:
                            # 如果请求参数不传address，那么address字段不会被修改，仍为原值
                            if not new_address:
                                new_address = res2[0]["address"]
                            # 把传入的明文密码通过MD5加密变为密文
                            new_password = get_md5(res2[0]["username"], new_password)
                            sql3 = "UPDATE user SET password = '{}', sex = '{}', telephone = '{}', address = '{}' " \
                                   "WHERE id = {}".format(new_password, new_sex, new_telephone, new_address, id)
                            db.execute_db(sql3)
                            print("修改用户信息SQL ==>> {}".format(sql3))
                            return jsonify({"code": 0, "msg": "恭喜，修改用户信息成功！"})
                    else:
                        return jsonify({"code": 4004, "msg": "当前用户不是管理员用户，无法进行操作，请检查！！！"})
                else:
                    return jsonify({"code": 4003, "msg": "token口令不正确，请检查！！！"})
            else:
                return jsonify({"code": 4002, "msg": "当前用户未登录，请检查！！！"})
    else:
        return jsonify({"code": 4001, "msg": "管理员用户/token口令/密码/手机号不能为空，请检查！！！"})

@app.route("/delete/user/<string:username>", methods=['POST'])
def user_delete(username):
    admin_user = request.json.get("admin_user", "").strip()  # 当前登录的管理员用户
    token = request.json.get("token", "").strip()  # token口令
    if admin_user and token:
        redis_token = redis_db.handle_redis_token(admin_user)  # 从redis中取token
        if redis_token:
            if redis_token == token:  # 如果从redis中取到的token不为空，且等于请求body中的token
                sql1 = "SELECT role FROM user WHERE username = '{}'".format(admin_user)
                res1 = db.select_db(sql1)
                print("根据用户名 【 {} 】 查询到用户类型 == >> {}".format(admin_user, res1))
                user_role = res1[0]["role"]
                if user_role == 0:  # 如果当前登录用户是管理员用户
                    sql2 = "SELECT * FROM user WHERE username = '{}'".format(username)
                    res2 = db.select_db(sql2)
                    print(sql2)
                    print("根据用户名 【 {} 】 查询到用户信息 ==>> {}".format(username, res2))
                    if not res2:  # 如果要删除的用户不存在于数据库中，res2为空
                        return jsonify({"code": 3005, "msg": "删除的用户名不存在，无法进行删除，请检查！！！"})
                    elif res2[0]["role"] == 0: # 如果要删除的用户是管理员用户，则不允许删除
                        return jsonify({"code": 3006, "msg": "用户名：【 {} 】，该用户不允许删除！！！".format(username)})
                    else:
                        sql3 = "DELETE FROM user WHERE username = '{}'".format(username)
                        db.execute_db(sql3)
                        print("删除用户信息SQL ==>> {}".format(sql3))
                        return jsonify({"code": 0, "msg": "恭喜，删除用户信息成功！"})
                else:
                    return jsonify({"code": 3004, "msg": "当前用户不是管理员用户，无法进行操作，请检查！！！"})
            else:
                return jsonify({"code": 3003, "msg": "token口令不正确，请检查！！！"})
        else:
            return jsonify({"code": 3002, "msg": "当前用户未登录，请检查！！！"})
    else:
        return jsonify({"code": 3001, "msg": "管理员用户/token口令不能为空，请检查！！！"})