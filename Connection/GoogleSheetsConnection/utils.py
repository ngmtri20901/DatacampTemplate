from googleapiclient.discovery import build
import httplib2
import os
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from apiclient import discovery

"""
Setup a service connecting to the Google Sheets API via a personal API key
- gss_api_key = the personal google spreadsheets api key
"""
def setup_service_apikey(gss_api_key):
    discoveryServiceUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                            'version=v4')
    service = discovery.build(
        'sheets',
        'v4',
        http=httplib2.Http(),
        discoveryServiceUrl=discoveryServiceUrl,
        developerKey=gss_api_key)
    return service

"""
Setup a service connecting to the Google Sheets API via the Google OAuth2
- creds_file = file containing the credentials. If None, function will try to find the token.json file that is present after authenticating once
"""
def setup_service_oauth(creds_file):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
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
                creds_file, SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service
    
"""
Using the service, connect to specified range in the specified spreadsheet
- service = service connecting to the API
- spreadsheetId = the Id of the spreadsheet that the user wants to access
- rangeName = the range or sheet that the user wants to access within the spreadsheet
"""
def call_sheets_api(service, spreadsheetId, rangeName):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
                                range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        df = pd.DataFrame(values[1:], columns=values[0])
        return df

def read_spreadsheet_api_key(spreadsheetId, gss_api_key, rangeName, include_col_names = True):
    service = setup_service_apikey(gss_api_key)   
    return call_sheets_api(service, spreadsheetId, rangeName)
    
def read_spreadsheet_oauth(spreadsheetId, rangeName, creds_file = None, include_col_names = True):
    service = setup_service_oauth(creds_file)
    return call_sheets_api(service, spreadsheetId, rangeName)
    

    