import redis
from config.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWD, EXPIRE_TIME


class RedisDb():

    def __init__(self, host, port, passwd):
        # 建立数据库连接
        self.r = redis.Redis(
            host=host,
            port=port,
            password=passwd,
            decode_responses=True # get() 得到字符串类型的数据
        )

    def handle_redis_token(self, key, value=None):
        if value: # 如果value非空，那么就设置key和value，EXPIRE_TIME为过期时间
            self.r.set(key, value, ex=EXPIRE_TIME)
        else: # 如果value为空，那么直接通过key从redis中取值
            redis_token = self.r.get(key)
            return redis_token


redis_db = RedisDb(REDIS_HOST, REDIS_PORT, REDIS_PASSWD)