from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # jsonify返回的中文正常显示

data = [
    {"id": 1, "username": "小明", "password": "123456", "role": 0, "sex": 0, "telephone": "10086", "address": "北京市海淀区"},
    {"id": 2, "username": "李华", "password": "abc", "role": 1, "sex": 0, "telephone": "10010", "address": "广州市天河区"},
    {"id": 3, "username": "大白", "password": "666666", "role": 0, "sex": 1, "telephone": "10000", "address": "深圳市南山区"}
]


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/users", methods=["GET"])
def get_all_users():
    """获取所有用户信息"""
    return jsonify({"code": "0", "data": data, "msg": "操作成功"})


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """获取某个用户信息"""
    if user_id > 0 and user_id <= len(data):
        return jsonify({"code": "0", "data": data[user_id - 1], "msg": "操作成功"})
    return jsonify({"code": "1", "msg": "用户不存在"})


@app.route("/register", methods=['POST'])
def user_register():
    username = request.json.get("username").strip()  # 用户名
    password = request.json.get("password").strip()  # 密码
    sex = request.json.get("sex", "0").strip()  # 性别，默认为0(男性)
    telephone = request.json.get("telephone", "").strip()  # 手机号，默认为空
    address = request.json.get("telphone", "").strip()  # 地址，默认为空
    if username and password and telephone:
        import re
        if username == "wintest":
            return jsonify({"code": 2002, "msg": "用户名已存在！！！"})
        elif not (sex == "0" or sex == "1"):
            return jsonify({"code": 2003, "msg": "输入的性别只能是 0(男) 或 1(女)！！！"})
        elif not (len(telephone) == 11 and re.match("^1[3,5,7,8]\d{9}$", telephone)):
            return jsonify({"code": 2004, "msg": "手机号格式不正确！！！"})
        else:
            return jsonify({"code": 0, "msg": "恭喜，注册成功！"})
    else:
        return jsonify({"code": 2001, "msg": "用户名/密码/手机号不能为空，请检查！！！"})


@app.route("/login", methods=['POST'])
def user_login():
    username = request.values.get("username")
    password = request.values.get("password")
    if username and password:
        if username == "wintest" and password == "123456":
            return jsonify({"code": 0, "msg": "恭喜，登录成功！"})
        return jsonify({"code": 1002, "msg": "用户名或密码错误！！！"})
    else:
        return jsonify({"code": 1001, "msg": "用户名或密码不能为空！！！"})


if __name__ == '__main__':
    app.run()
