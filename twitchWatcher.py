import os
from dotenv import load_dotenv
import requests

load_dotenv()

CLIENT_ID = os.getenv(key='TWITCH_CLIENT_ID')
SECRET  = os.getenv(key='TWITCH_SECRET')

# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://youtube.com")
streamerlist = ['gingersoccermom','ragdoll139','itsruddy','theleakygiraffe','midoriin4k','soundsofthewild']
game_name = 'Rocket League'
key_words = ['LESC','League of Extraordinary Soccer Cars']

streamsUrl = 'https://api.twitch.tv/helix/streams?user_login=' #login name
channelsUrl = 'https://api.twitch.tv/helix/channels?broadcaster_id=' # ID #
usersUrl = 'https://api.twitch.tv/helix/users?login=' #login_name

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
    print(autCall)
    global access_token
    access_token = AutCall.json()['access_token']
    global head
    head = {
    'Client-ID' : CLIENT_ID,
    'Authorization' :  "Bearer " + access_token
    }

def getStreamsFromTitle(phrase):
    streams = requests.get(streamsUrl + phrase, headers = head).json()['data']
    return streams
def getStreamsFromLogin(login_name):
    streams = requests.get(streamsUrl + login_name, headers = head).json()['data']
    return streams #list of matches

def getUserIDFromLogin(login_name):
    id =requests.get(usersUrl, headers = head).json()['data'][0]['id']
    return str(id) #broadcaster_id of login name

def getChannelFromUserID(user_id):
    channel_info = requests.get(channelsUrl + str(user_id), headers = head).json()['data'][0]
    return channel_info #channel info dict


if __name__ == '__main__':
    getToken()
    testgame='Rocket League'
    testTitle='rank'
