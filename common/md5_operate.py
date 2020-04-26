import hashlib
from config.setting import MD5_SALT


def get_md5(username, str):
    """MD5加密处理"""
    str = username + str + MD5_SALT  # 把用户名也作为str加密的一部分
    md5 = hashlib.md5()  # 创建md5对象
    md5.update(str.encode("utf-8"))  # Python3中需要先转换为 bytes 类型，才能加密
    return md5.hexdigest()  # 返回密文