import redis
import os
from dotenv import load_dotenv
load_dotenv()
import json
from urllib.parse import urlparse

class redisDB():
    # def __init__(self):

    url = urlparse(os.getenv('REDIS_TLS_URL'))

    def printKeys(self):
        r = redis.Redis(host=self.url.hostname, port=self.url.port, username=self.url.username, password=self.url.password, ssl=True, ssl_cert_reqs=None)

        print(str(r.dbsize()))

        keys = r.keys()
        print(keys)
        r.close()
        return keys

    def getValue(self,key):
        # connect to db
        r = redis.Redis(host=self.url.hostname, port=self.url.port, username=self.url.username, password=self.url.password, ssl=True, ssl_cert_reqs=None)

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
        r = redis.Redis(host=self.url.hostname, port=self.url.port, username=self.url.username, password=self.url.password, ssl=True, ssl_cert_reqs=None)

        # get stored value
        valueString = json.dumps(value)
        r.set(key,valueString)
        r.close()
        print('Value of ' + str(key) + ' has been set')
        return None

if __name__ == '__main__':
    rc=redisDB()
    db_keys = rc.printKeys()
    # player_db = rc.getValue('participants')
    # for k in db_keys:
    #     rc.getValue(key=k)
    # print(rc.getValue('lesc_db'))
    # with open("player_db.txt", "w") as file1:
        # file1.write(json.dumps(player_db))
