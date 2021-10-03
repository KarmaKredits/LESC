# from __future__ import print_function
import os.path
from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import json
# from bot import logErr
load_dotenv()



# credentials_string = os.getenv(key='CREDENTIALS')
# if len(credentials_string)>5:
#     CREDENTIALS=json.loads(str(os.getenv(key='CREDENTIALS')))
# else:
CREDENTIALS={"installed":{"client_id":os.getenv(key='CRED_CLIENT_ID'),
    "project_id":"tester-322319",
    "auth_uri":"https://accounts.google.com/o/oauth2/auth",
    "token_uri":"https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
    "client_secret":os.getenv(key='CRED_SECRET'),
    "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}

# token_string = os.getenv(key='GOOGLE_TOKEN')
# if len(token_string)>5:
#     TOKEN=json.loads(str(os.getenv(key='GOOGLE_TOKEN')))
# else:
TOKEN={"token": os.getenv(key='GOOGLE_TOKEN_TOKEN'),
    "refresh_token": os.getenv(key='GOOGLE_TOKEN_REFRESH'),
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": os.getenv(key='CRED_CLIENT_ID'),
    "client_secret": os.getenv(key='CRED_SECRET'),
    "scopes": ["https://www.googleapis.com/auth/spreadsheets.readonly"],
    "expiry": "2021-08-12T02:07:28.887607Z"}

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
testID = '1DGpfnwq57um8KmXQEGIqby3nUqfK7Q4SbvXOfsbZsdM'
testRange = 'US Table!A2:J14'
LESCsheet='1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII'
LESCranges = ['Rosters!A2:C15','Rosters!E2:G16','US Table!A2:J14','EU Table!A2:J15',
    'Week 1!B2:I14','Week 1!B18:I31','Week 2!A2:H14','Week 2!A18:H28','Week 3!A2:I13',
    'Week 3!A22:I37','Week 4!A2:I17', 'Week 4!A18:I31','Playoff Bracket!B1:I27','Prizepool!B2:G13']

table_names={
    'us_roster':'Rosters!A2:C15',
    'eu_roster':'Rosters!E2:G16',
    'us_standings':"'US Table'!A2:J14",
    'eu_standings':"'EU Table'!A2:J15",
    'us_week1':"'Week 1'!B2:I14",
    'eu_week1':"'Week 1'!B18:I31",
    'us_week2':"'Week 2'!A2:H14",
    'eu_week2':"'Week 2'!A18:H28",
    'us_week3':"'Week 3'!A2:I13",
    'eu_week3':"'Week 3'!A22:I37",
    'us_week4':"'Week 4'!A2:I17",
    'eu_week4':"'Week 4'!A18:I31",
    'playoff':"'Playoff Bracket'!B1:I27",
    'awards':"Prizepool!B2:G13"
}


def getDataFromGoogleSheets():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # creds = None
    creds = Credentials(TOKEN['token'],refresh_token=TOKEN['refresh_token'],token_uri=TOKEN['token_uri'],client_id=TOKEN['client_id'],client_secret=TOKEN['client_secret'],scopes=TOKEN['scopes'])


    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    ranges= []
    try:

    #get sheets from test LESC1
        result = sheet.values().batchGet(spreadsheetId=LESCsheet, ranges=LESCranges).execute()

        ranges = result.get('valueRanges', [])
        # print('{0} ranges retrieved.'.format(len(ranges)))

    except Exception as err:
        errArray = [type(err).__class__.__name__]
        print('++ ', type(err))
        for arg in err.args:
            print('++++' ,arg)
            errArray.append(json.dumps(arg))
            # logErr('\n'.join(errArray))
            return None


    if not ranges:
         print('No data found.')
    else:
        # print('LESC ranges')
        for range in ranges:
            # print(range.get('range'))
            # print(range['range'])
            for row in range.get('values',[]):
                # Print columns A and E, which correspond to indices 0 and 4.
                # print(row)
                None
    return ranges

def formatRosters(ranges):
    us = ranges[0].get('values',[])
    eu = ranges[1].get('values',[])
    header = us[0]
    roster=[]
    for row in range(2,len(us)):
        entry = {'division':'US'}
        for col in range(len(us[row])):
            entry[header[col].lower()]=us[row][col].strip()
        roster.append(entry)
    for row in range(2,len(eu)):
        entry = {'division':'EU'}
        for col in range(len(eu[row])):
            entry[header[col].lower()]=eu[row][col].strip()
        roster.append(entry)
    return roster

def formatStandings(ranges):
    us = ranges[2].get('values',[])
    eu = ranges[3].get('values',[])
    us[0][0]='Rank' #currently null cell
    eu[0][0]='Rank' #currently null cell
    standings = {}
    standings['US']=us
    standings['EU']=eu
    return standings

def generateProfiles(roster,playoff,awardTable):
    player_db={}
    for season in roster:
        for team in roster[season]:
            if not (team['captain'] in player_db):
                player_db[team['captain']] = {'player':team['captain'],
                    'season':[],'teams':[],'teammates':[],'awards':[]}
            if not (team['teammate'] in player_db):
                player_db[team['teammate']] = {'player':team['teammate'],
                    'season':[],'teams':[],'teammates':[],'awards':[]}
            player_db[team['captain']]['season'].append('S' + season[-1] + ' ' + team['division'] + ' Division')
            player_db[team['captain']]['teams'].append(team['team'])
            player_db[team['captain']]['teammates'].append(team['teammate'])
            player_db[team['captain']]['awards'].append('S' + season[-1] + ' OG Participant')
            player_db[team['teammate']]['season'].append('S' + season[-1] + ' ' + team['division'] + ' Division')
            player_db[team['teammate']]['teams'].append(team['team'])
            player_db[team['teammate']]['teammates'].append(team['captain'])
            player_db[team['teammate']]['awards'].append('S' + season[-1] + ' OG Participant')
            if team['team'].lower() in playoff:
                player_db[team['captain']]['awards'].insert(0,'S' + season[-1] + ' Playoff Contender')
                player_db[team['teammate']]['awards'].insert(0,'S' + season[-1] + ' Playoff Contender')
            for row in awardTable:
                if (team['captain'] in row) or (team['teammate'] in row):
                    player_db[team['captain']]['awards'].insert(0,'S' + season[-1] + ' ' + row[0])
                    player_db[team['teammate']]['awards'].insert(0,'S' + season[-1] + ' ' + row[0])

    return player_db

def teamsInPlayoffs(ranges):
    inPlayoffs = False
    list = []
    playoffs = ranges[12].get('values',[])
    # print(playoffs)
    for col in [0,-1]:
        for row in [7,13,14,19,20,25,26]:
            team = playoffs[row][col]
            index = team.find('(')
            team = team[:index].strip().lower()
            list.append(team)
    return list

def getAwards(ranges):
    awardList=[]
    awards = ranges[13].get('values',[])
    for row in awards:
        if len(row)>1:
            try:
                awardList.append([row[0],row[2],row[3]])
            except:pass
    return awardList

def getMatches(ranges):
    matches = {'us': [], 'eu': []}
    temp = ranges[4].get('values',[])
    for week in [4,6,8,10]:
        print(week)
        for row in ranges[week].get('values',[]):
            if len(row) == 8:
                homeTeam, vs, awayTeam, day, date, time, commentating, result = row
                matches['us'].append({
                    'home': homeTeam,
                    'away': awayTeam,
                    'day': day,
                    'date': date,
                    'time': time,
                    'commentators': commentating,
                    'result': result
                    })
    for week in [5,7,9,11]:
        print(week)
        for row in ranges[week].get('values',[]):
            if len(row) == 8:
                homeTeam, vs, awayTeam, day, date, time, commentating, result = row
                matches['eu'].append({
                    'home': homeTeam,
                    'away': awayTeam,
                    'day': day,
                    'date': date,
                    'time': time,
                    'commentators': commentating,
                    'result': result
                    })
    # print(matches)
    return matches
    # ['Home Team', '', 'Away Team', 'Day', 'Date', 'Time', 'Commentating ', 'Result']
    # ['Nked Dommer-nuts', 'v', 'JustZees League ', 'Mon', '6/28', '9:30 am', '', '0-3']


if __name__ == '__main__':
    db=getDataFromGoogleSheets()
    if db:
        print('PASS')
    # roster = {}
    # roster['LESC1']=formatRosters(db)
    # awards={}
    # awards['LESC1']=formatAwards(db)
    # standings={}
    # standings['LESC1']=formatStandings(db)
    # playoffList=teamsInPlayoffs(db)
    # awardsTable = getAwards(db)
    # players=generateProfiles(roster,playoffList,awardsTable)
    # print(db[4])
    print(getMatches(db))
