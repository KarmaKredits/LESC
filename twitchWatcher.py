import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import json

# now = datetime.now()

load_dotenv()
# "redis://:(...+)@(...+):(\d+)"gm
CLIENT_ID = os.getenv(key='TWITCH_CLIENT_ID')
SECRET  = os.getenv(key='TWITCH_SECRET')


streamDiscordId = {
    'gingersoccermom': 644839166324244489,'ragdoll139': 328997596242903040,
    'ruddybuddy': '218166348235276290','theleakygiraffe': '362175989205172226',
    'midoriin4k': '197506166874570752','soundsofthewild':273594567385939970,
    'skrupstar':'249263220026638347','enjib':'187618513911808000',
    'skilltwister': 300638405618958338, 'elekidp06': 300725739114987523,
    'shwa_zee': 169641021519560707, 'kylure': 182367682811658240,
    'karmakredits': 174714475113480192, 'og_grips': 346715426241380362,
    'csmith_games': 492497679570436117, 'xxvhpxx': 335887314159140866,
    'qs3v3n': 192007340927614976, 'altihex3': 505797270164340788,
    'kedsypoo': 408671999439667202, 'shakeyjake_': 228109622551117824,
    'arturek1666': 124875390014586880, 'iota2002': 283336058085703683,
    'lit_nyte': 638948229634850826, 'theschizzz95': 572854738413158400
    }
# streamDiscordId= {'karmakredits': '174714475113480192'} #test with my id
# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://youtube.com")
streamerlist = ['gingersoccermom','ragdoll139','ruddybuddy','midoriin4k',
                'soundsofthewild','benny07','csmith_games','theschizzz95',
                'xxvhpxx','dannyofthepaul','r4lplays','kylure',
                'shakeyjake_','skrupstar','enjib','elekidp06',
                'skilltwister', 'karmakredits', 'og_grips', 'qs3v3n',
                'altihex3','kedsypoo', 'rlgamermom','iota2002','lit_nyte']

game_name = 'Rocket League'
key_words = ['LESC','League of Extraordinary Soccer Cars']

streamsUrl = 'https://api.twitch.tv/helix/streams?user_login=' #login name
channelsUrl = 'https://api.twitch.tv/helix/channels?broadcaster_id=' # ID #
usersUrl = 'https://api.twitch.tv/helix/users?login=' #login_name
scheduleUrl = 'https://api.twitch.tv/helix/schedule?first=1&broadcaster_id='

authURL = 'https://id.twitch.tv/oauth2/token'
AutParams = {'client_id': CLIENT_ID,
             'client_secret': SECRET,
             'grant_type': 'client_credentials'
             }
access_token = None
head = None

# HTTP Code	Meaning
# 200	Channel/Stream returned successfully
# 400	Missing Query Parameter
# 500	Internal Server Error; Failed to get channel information


def getToken():
    AutCall = requests.post(url=authURL, params=AutParams)
    # print(AutCall.json())
    global access_token
    access_token = AutCall.json()['access_token']
    global head
    head = {
    'Client-ID' : CLIENT_ID,
    'Authorization' :  "Bearer " + access_token
    }
    return str(AutCall)

def getStreamsFromTitle(phrase):
    streams = requests.get(streamsUrl + phrase, headers = head).json()['data']
    return streams
def getStreamsFromLogin(login_name):
    streams = requests.get(streamsUrl + login_name, headers = head).json()['data']
    return streams #list of matches

def getUserIDFromLogin(login_name):
    id =requests.get(usersUrl + login_name, headers = head).json()['data']#[0]['id']
    return id #broadcaster_id of login name

def getChannelFromUserID(user_id):
    channel_info = requests.get(channelsUrl + str(user_id), headers = head).json()#['data']#[0]
    return channel_info #channel info dict

def getScheduleFromUserID(user_id):
    schedule_info = requests.get(scheduleUrl + str(user_id), headers = head).json()
    # print(schedule_info)
    # print('data' in schedule_info)
    if 'data' in schedule_info:
        # print()
        return schedule_info['data']['segments'] #channel info dict
    else:
        return []


if __name__ == '__main__':
    print(len(getToken()))
    testgame='Rocket League'
    testTitle='rank'

    # sched = getScheduleFromUserID('150659658')
    # first = None
    # for item in sched:
    #     print(item)
    #     if first == None:
    #         if item['is_recurring'] == True:
    #             first = item
    #     elif first['title'] == item['title']:
    #         print('duplicate')
    #         break



    user_list = getUserIDFromLogin('&login='.join(streamerlist))
    # user_list = getUserIDFromLogin('gingersoccermom')
    # print(user_list)
    # now = datetime.utcnow()
    # for user in user_list:
    #     # print(user['id'], '\n')
    #     sched = getScheduleFromUserID(user['id'])
    #     # print(sched)
    #     print(user['display_name'])
    #     if len(sched)>0:
    #         print(sched[0]['title'])
    #         if sched[0]['category'] != None: print(sched[0]['category']['name'])
    #         print(sched[0]['start_time'])
    #         dt_start = datetime.strptime(sched[0]['start_time'], '%Y-%m-%dT%H:%M:%SZ')
    #         delta = dt_start - now
    #         print(delta.total_seconds())
    #     else:
    #         print('No Schedule')
    #     print('')

    # time = 0
    # print('&user_login='.join(streamerlist))
    # print(getStreamsFromLogin('&user_login='.join(streamerlist)))
    searchTerm = 'AY'
    for streamer in streamerlist:
        stream = getStreamsFromLogin(streamer)
        print(streamer, stream)

        if len(stream) > 0:
            id = str(stream[0]['id'])
            # print(id)
            # channel = getChannelFromUserID(id)
            # print(channel)
            # print(streamer, 'on')
            # print(stream[0]['title'])
            if searchTerm in stream[0]['title']:
                # print('found')
                timeStr = stream[0]['started_at']
                time = datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
                print(time)
                print(datetime.utcnow())
                print(datetime.utcnow()-time)
