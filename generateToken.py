import os
# from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def generateCreds():
    creds=None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        print('token file exists')
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print('creds bad')
        # if creds and creds.expired and creds.refresh_token:
        #     print('refresh creds')
        #     creds.refresh(Request())
        # else:
        print('flow')
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        # flow = Flow(oauth2session, client_type, client_config, redirect_uri=None, code_verifier=None, autogenerate_code_verifier=False)

        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            print('write token')
            token.write(creds.to_json())
    # creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # creds = flow.run_local_server(port=0)


if __name__ == '__main__':
    generateCreds()
