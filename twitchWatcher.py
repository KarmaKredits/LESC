from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
# chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

from dotenv import load_dotenv

load_dotenv()
PATH = os.getenv(key='PATHWEBDRIVER')


# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://youtube.com")
import requests

URL = 'https://api.twitch.tv/helix/streams?user_login=shwa_zee'
chan = 'https://api.twitch.tv/helix/channels?broadcaster_id='
stream = 'https://api.twitch.tv/helix/streams?'
user = 'https://api.twitch.tv/helix/users?login=shwa_zee'
authURL = 'https://id.twitch.tv/oauth2/token'
Client_ID = os.getenv(key='TWITCH_CLIENT_ID')
Secret  = os.getenv(key='TWITCH_SECRET')

AutParams = {'client_id': Client_ID,
             'client_secret': Secret,
             'grant_type': 'client_credentials'
             }


def Check():
    AutCall = requests.post(url=authURL, params=AutParams)
    access_token = AutCall.json()['access_token']
    print(AutCall)
    head = {
    'Client-ID' : Client_ID,
    'Authorization' :  "Bearer " + access_token
    }

    r = requests.get(URL, headers = head).json()['data']
    id =requests.get(user, headers = head).json()['data'][0]['id']

    r2 = requests.get(chan + str(id), headers = head).json()['data'][0]['title']
    print(r2)

    if r:
        r = r[0]
        if r['type'] == 'live':
            return True
        else:
            return False
    else:
        return False

# import twitch
# client = twitch.TwitchHelix(client_id=Client_ID, client_secret=Secret, scopes=[twitch.constants.OAUTH_SCOPE_ANALYTICS_READ_EXTENSIONS])
# client.get_oauth()
# client.get_streams()
print(Check())
