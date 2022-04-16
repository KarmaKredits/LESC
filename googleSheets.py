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

TOKEN=json.loads(os.getenv(key='GOOGLE_TOKEN'))


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
testID = '1DGpfnwq57um8KmXQEGIqby3nUqfK7Q4SbvXOfsbZsdM'
testRange = 'US Table!A2:J14'
LESCsheet='1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII'
LESCranges = [
    'Rosters!A2:C15','Rosters!E2:G16',
    'US Table!A2:J14','EU Table!A2:J15',
    'Week 1!B2:I14','Week 1!B18:I31',
    'Week 2!A2:H14','Week 2!A18:H28',
    'Week 3!A2:I13','Week 3!A22:I37',
    'Week 4!A2:I17', 'Week 4!A18:I31',
    'Playoff Bracket!B1:I27','Prizepool!B2:G13'
    ]
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
LESCsheet2 = '1DdgY8i-pKK8WoszvfrKUYEoy4I9f3qzUxaLumOo7Ptw'
LESCranges2 = ['upper_roster','lower_roster','upper_standings','lower_standings',
    'upper_week1','lower_week1','upper_week2','lower_week2','upper_week3','lower_week3',
    'upper_week4','lower_week4','playoff', 'awards']

LESC3sheetNAUpper = '1SrSeVJHxd7uODeV2uC6AsMXd_RgfCgqotChIN0AvAyg'
LESC3sheetNALower = '1HF-krfg69EZ5xK2BWx81_ryafQuYPOEu-acUEGQQlPo'
LESC3sheetEUUpper = '1TC5uFyegzNsRrTMqHiuiedA8Te-SpN-WOsUck_NL15c'
LESC3sheetEULower = '1XTRqwOyUKjD3X1PEpi7lTmd9wDpChI82N78wFPUHq6Y'
LESC3ranges = ['rosters','standings','matches']

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
        # result = sheet.values().batchGet(spreadsheetId=LESCsheet2, ranges=LESCranges2).execute()
        # result2 = sheet.values().batchGet(spreadsheetId=LESCsheet, ranges=LESCranges).execute()
        result1 = sheet.values().batchGet(spreadsheetId=LESC3sheetNAUpper, ranges=LESC3ranges).execute()
        result2 = sheet.values().batchGet(spreadsheetId=LESC3sheetNALower, ranges=LESC3ranges).execute()
        result3 = sheet.values().batchGet(spreadsheetId=LESC3sheetEUUpper, ranges=LESC3ranges).execute()
        result4 = sheet.values().batchGet(spreadsheetId=LESC3sheetEULower, ranges=LESC3ranges).execute()

        # ranges = result.get('valueRanges', [])
        # ranges2 = result2.get('valueRanges', [])
        ranges = {}
        ranges[1] = result1.get('valueRanges', [])
        ranges[2] = result2.get('valueRanges', [])
        ranges[3] = result3.get('valueRanges', [])
        ranges[4] = result4.get('valueRanges', [])

        print('{0} ranges retrieved.'.format(len(ranges)))

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
    # else:
    #     # print('LESC ranges')
    #     # print(ranges)
    #     for range in ranges:
    #         # print(range.get('range'))
    #         # print(range['range'])
    #         # print(range)
    #         for row in range.get('values',[]):
    #             # Print columns A and E, which correspond to indices 0 and 4.
    #             # print(row)
    #             None
    return ranges #, ranges2

def formatRosters(ranges):
    d1 = ranges[0].get('values',[])
    d2 = ranges[1].get('values',[])
    # print(d2)
    header = d1[0]
    roster=[]
    for row in range(2,len(d1)):
        # entry = {'division':'US'}
        entry = {'division':1}
        for col in range(len(d1[row])):
            entry[header[col].lower()]=d1[row][col].strip()
        if len(d1[row])==3:
            roster.append(entry)
    for row in range(2,len(d2)):
        # entry = {'division':'EU'}
        # print(row)
        # print(len(d2[row]))
        entry = {'division':2}
        for col in range(len(d2[row])):
            # print(col)
            entry[header[col].lower()]=d2[row][col].strip()
            # print(d2[row][col].strip())
            # print(len(d2[row][col].strip()))
        if len(d2[row])==3:
            roster.append(entry)
    return roster

def formatStandings(ranges):
    d1 = ranges[2].get('values',[])
    d2 = ranges[3].get('values',[])
    d1[0][0]='Rank' #currently null cell
    d2[0][0]='Rank' #currently null cell
    standings = {}
    standings[1]=d1
    standings[2]=d2
    return standings

def generateProfiles(season_db,playoff,awardTable):
    player_db={}
    argDiv = {'us': 1, 'eu' : 2, 'upper': 1, 'lower': 2}
    seaDiv = { 1: {1:'US',2:'EU'}, 2: {1:'Upper',2:'Lower'} }
    for season in season_db:
        for team in season_db[season]:
            captain = team['captain'].lower()
            teammate = team['teammate'].lower()
            if not (captain in player_db):
                player_db[captain] = {'player':team['captain'],
                    'season':[],'teams':[],'teammates':[],'awards':[]}
            if not (teammate in player_db):
                player_db[teammate] = {'player':team['teammate'],
                    'season':[],'teams':[],'teammates':[],'awards':[]}
            player_db[captain]['season'].append('S' + season[-1] + ' ' + seaDiv[int(season[-1])][team['division']] + ' Division')
            player_db[captain]['teams'].append(team['team'])
            player_db[captain]['teammates'].append(team['teammate'])
            player_db[captain]['awards'].append('S' + season[-1] + ' OG Participant')
            player_db[teammate]['season'].append('S' + season[-1] + ' ' + seaDiv[int(season[-1])][team['division']] + ' Division')
            player_db[teammate]['teams'].append(team['team'])
            player_db[teammate]['teammates'].append(team['captain'])
            player_db[teammate]['awards'].append('S' + season[-1] + ' OG Participant')
            if team['team'].lower() in playoff[season]:
                player_db[captain]['awards'].insert(0,'S' + season[-1] + ' Playoff Contender')
                player_db[teammate]['awards'].insert(0,'S' + season[-1] + ' Playoff Contender')
            # print(awardTable[season])
            for row in awardTable[season]:
                if (team['captain'] in row) or (team['teammate'] in row):
                    player_db[captain]['awards'].insert(0,'S' + season[-1] + ' ' + row[0])
                    player_db[teammate]['awards'].insert(0,'S' + season[-1] + ' ' + row[0])
    # print(player_db['SassyBrenda'])
    return player_db

def teamsInPlayoffs(ranges):
    inPlayoffs = False
    list = []
    playoffs = ranges[12].get('values',[])
    # print(playoffs)
    # print(len(playoffs))
    rows = [7,13,14,19,20,25]
    # print(rows)
    if len(playoffs)>26:
        rows.append(26)
        # print(rows)
    # print(rows - 6)
    # print('here')
    for col in [0,-1]:
        for row in rows:
            team = playoffs[row][col]
            index = team.find('(')
            team = team[:index].strip().lower()
            list.append(team)
    # print(list)
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
    print('getMatches')
    # print(ranges)
    matches = {1:[], 2:[]}
    temp = ranges[4].get('values',[])
    # print('===========\nweek')
    # print('upper')
    for week in [4,6,8,10]:
        values = ranges[week].get('values',[])
        for i in range(len(values)):
            # print(i,' - ', len(values[i]), ' - ', values[i])
            if len(values[i]) >=6 and not ('Home' in values[i][0]):
                home, vs, away, *others = values[i]
                day, date, time, commentators, result = 'TBD','TBD','TBD','','-'
                if len(others) == 1:
                    day = others
                elif len(others) == 2:
                    day, date = others
                elif len(others) == 3:
                    day, date, time = others
                elif len(others) == 4:
                    day, date, time, commentators = others
                elif len(others) == 5:
                    day, date, time, commentators, result = others

                tempM = {}
                # print(range(len(values[i])))

                matches[1].append({
                    'home': home,
                    'away': away,
                    'day': day,
                    'date': date,
                    'time': time,
                    'commentators': commentators,
                    'result': result
                    })
    # print('lower')
    for week in [5,7,9,11]:
        values = ranges[week].get('values',[])
        for i in range(len(values)):
            # print(i,' - ', len(values[i]), ' - ', values[i])
            if len(values[i]) >= 6 and not ('Home' in values[i][0]):
                # homeTeam, vs, awayTeam, day, date, time, commentating, result = values[i]
                # print(values[i])
                home, vs, away, *others = values[i]
                day, date, time, commentators, result = 'TBD','TBD','TBD','-','-'
                if len(others) == 1:
                    day = others
                elif len(others) == 2:
                    day, date = others
                elif len(others) == 3:
                    day, date, time = others
                elif len(others) == 4:
                    day, date, time, commentators = others
                elif len(others) == 5:
                    day, date, time, commentators, result = others

                # matches['eu'].append({
                matches[2].append({
                    'home': home,
                    'away': away,
                    'day': day,
                    'date': date,
                    'time': time,
                    'commentators': commentators,
                    'result': result
                    })
    # print(matches)
    return matches
    # ['Home Team', '', 'Away Team', 'Day', 'Date', 'Time', 'Commentating ', 'Result']
    # ['Nked Dommer-nuts', 'v', 'JustZees League ', 'Mon', '6/28', '9:30 am', '', '0-3']


if __name__ == '__main__':
    db =getDataFromGoogleSheets()
    # db, db2 =getDataFromGoogleSheets()
    if db:
        print('PASS')
    matchesDB = getMatches(db)
    # print(matchesDB)
    roster = {}
    roster['LESC1']=formatRosters(db)
    # roster['LESC2']=formatRosters(db)
    # print(roster)
    # standings={}
    # standings['LESC2']=formatStandings(db)
    # print(standings)
    playoffList = {}
    playoffList['LESC1']=teamsInPlayoffs(db)
    awardsTable ={}
    awardsTable['LESC1'] = getAwards(db)
    players=generateProfiles(roster,playoffList,awardsTable)
    # print(players)
    # print(db[4])
    # print(getMatches(db))
