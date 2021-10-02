import redis
import os
from dotenv import load_dotenv
load_dotenv()
import json

class redisDB():
    # def __init__(self):

    # REDIS_URL=os.getenv('REDIS_URI')
    REDIS_HOST=os.getenv('REDIS_HOST')
    REDIS_PORT=int(os.getenv('REDIS_PORT'))
    REDIS_PASSWORD=os.getenv('REDIS_PASSWORD')

    def printKeys(self):
        # r = redis.from_url(os.environ.get(REDIS_URL))
        r = redis.StrictRedis(host=self.REDIS_HOST,
        port=self.REDIS_PORT,
        # port=12345,
        password=self.REDIS_PASSWORD,
        ssl=True,
        ssl_cert_reqs=None,
        socket_timeout=10)

        print(str(r.dbsize()))

        keys = r.keys()
        print(keys)
        r.close()
        return keys

    def getValue(self,key):
        # connect to db
        r = redis.StrictRedis(host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            ssl=True, ssl_cert_reqs=None)
        # check if key exists
        value = ''
        if (r.exists(key)):
            # get stored value
            value = json.loads(r.get(key))
            print('Retrieved value of ' + str(key))
        else:
            print(str(key) + ' not found in db')
        r.close()
        return value



    def setValue(self,key,value):
        # connect to db
        r = redis.StrictRedis(host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            password=self.REDIS_PASSWORD,
            ssl=True, ssl_cert_reqs=None)
        # get stored value
        valueString = json.dumps(value)
        r.set(key,valueString)
        r.close()
        print('Value of ' + str(key) + ' has been set')
        return None

if __name__ == '__main__':
    rc=redisDB()
    db_keys = rc.printKeys()
    # for k in db_keys:
    #     rc.getValue(key=k)
    # print(rc.getValue('lesc_db'))
