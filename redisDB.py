import redis
import os
from dotenv import load_dotenv
load_dotenv()

REDIS_URL=os.getenv('REDIS_URI')
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_PASSWORD=os.getenv('REDIS_PASSWORD')

def connect():
    # r = redis.from_url(os.environ.get(REDIS_URL))
    r = redis.StrictRedis(host=REDIS_HOST,
                        port=REDIS_PORT,
                        password=REDIS_PASSWORD)
    print(r.dbsize())
    # r.set()
    r.close()
    return None
# Delete all keys from redis database.
# Warning! This basically wipes all persistant info for poketrawler.
# Use with caution.
# def deleteAllKeys(self):
#     r = redis.StrictRedis(host=self.REDIS_HOST,
#                             port=self.REDIS_PORT,
#                             password=self.REDIS_PASSWORD,
#                             decode_responses=True)
#     return None

if __name__ == '__main__':
    connect()
