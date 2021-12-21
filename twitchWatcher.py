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
    'itsruddyy': '218166348235276290','theleakygiraffe': '',
    'midoriin4k': '197506166874570752','soundsofthewild':273594567385939970,
    'skrupstar':'249263220026638347','enjib':'187618513911808000'}
# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://youtube.com")
streamerlist = ['gingersoccermom','ragdoll139','itsruddyy','theleakygiraffe','midoriin4k',
                'soundsofthewild','Shwa_zee','chillcatdad','benny07','csmith_games',
                'itsjeffguy','arkwav','xxvhpxx','dannyofthepaul','bigfootmcgroot',
                'r4lplays','tuffavocado','kylure','laggittarius','skrupstar',
                'enjib', 'skilltwister']
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
            print(id)
            # channel = getChannelFromUserID(id)
            # print(channel)
            print(streamer, 'on')
            print(stream[0]['title'])
            if searchTerm in stream[0]['title']:
                print('found')
                timeStr = stream[0]['started_at']
                time = datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
                print(time)
                print(datetime.utcnow())
                print(datetime.utcnow()-time)
