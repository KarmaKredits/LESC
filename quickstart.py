from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'
testID = '1DGpfnwq57um8KmXQEGIqby3nUqfK7Q4SbvXOfsbZsdM'
testRange = 'US Table!A2:J14'
LESCsheet='1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII'
LESCranges = ['Rosters!A2:C15','Rosters!E2:G16','US Table!A2:J14','EU Table!A2:J15',
    'Week 1!B2:I14','Week 1!B18:I31','Playoff Bracket!B1:I27']

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])

    #get sheets from test LESC1
    result = sheet.values().batchGet(spreadsheetId=LESCsheet,
                                ranges=LESCranges).execute()
    ranges = result.get('valueRanges', [])

    print('{0} ranges retrieved.'.format(len(ranges)))

    if not ranges:
        print('No data found.')
    else:
        print('LESC ranges')
        for range in ranges:
            print(range.get('range'))
            for row in range.get('values',[]):
                # Print columns A and E, which correspond to indices 0 and 4.
                print(row)
    return ranges



if __name__ == '__main__':
    main()
