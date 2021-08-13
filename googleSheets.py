from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import json
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
    "client_secret":os.getenv(key=CRED_SECRET),
    "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}

# token_string = os.getenv(key='GOOGLE_TOKEN')
# if len(token_string)>5:
#     TOKEN=json.loads(str(os.getenv(key='GOOGLE_TOKEN')))
# else:
GOOGLE_TOKEN={"token": GOOGLE_TOKEN_TOKEN,
    "refresh_token": GOOGLE_TOKEN_REFRESH,
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": os.getenv(key=CRED_CLIENT_ID),
    "client_secret": os.getenv(key=CRED_SECRET),
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

def generateCreds():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow = Flow(oauth2session, client_type, client_config, redirect_uri=None, code_verifier=None, autogenerate_code_verifier=False)

            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    creds = flow.run_local_server(port=0)

def getDataFromGoogleSheets():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # creds = None
    creds = Credentials(TOKEN['token'],refresh_token=TOKEN['refresh_token'],token_uri=TOKEN['token_uri'],client_id=TOKEN['client_id'],client_secret=TOKEN['client_secret'],scopes=TOKEN['scopes'])

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    #get sheets from test LESC1
    result = sheet.values().batchGet(spreadsheetId=LESCsheet,
                                ranges=LESCranges).execute()
    ranges = result.get('valueRanges', [])
    print('{0} ranges retrieved.'.format(len(ranges)))

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
            entry[header[col].lower()]=us[row][col]
        roster.append(entry)
    for row in range(2,len(eu)):
        entry = {'division':'EU'}
        for col in range(len(eu[row])):
            entry[header[col].lower()]=eu[row][col]
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

if __name__ == '__main__':
    db=getDataFromGoogleSheets()
    if db:
        print('PASS')
    roster = {}
    roster['LESC1']=formatRosters(db)
    awards={}
    # awards['LESC1']=formatAwards(db)
    standings={}
    standings['LESC1']=formatStandings(db)
