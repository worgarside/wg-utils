from json import dump, load
from os import path
from ssl import SSLEOFError
from time import sleep
from http.client import NotConnected, IncompleteRead, ImproperConnectionState, CannotSendRequest, CannotSendHeader, \
    ResponseNotReady, BadStatusLine
from httplib2 import HttpLib2Error
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from random import random
from requests import get

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'
SECRET_FILES_DIR = '{}secret_files/'.format(WGUTILS_DIR)

CLIENT_SECRETS_FILE = '{}google_client_secrets.json'.format(SECRET_FILES_DIR)
CREDENTIALS_FILE = '{}google_credentials.json'.format(SECRET_FILES_DIR)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

USER_ID = 'me'
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (HttpLib2Error, IOError, NotConnected,
                        IncompleteRead, ImproperConnectionState,
                        CannotSendRequest, CannotSendHeader,
                        ResponseNotReady, BadStatusLine)

RETRIABLE_STATUS_CODES = (500, 502, 503, 504)


def exponential_backoff(func, max_retries=10, retriable_exceptions=RETRIABLE_EXCEPTIONS,
                        retriable_status_codes=RETRIABLE_STATUS_CODES, max_backoff=64):
    retry = 0
    response = None
    error = None
    while response is None and retry < max_retries:
        try:
            status, response = func()
        except HttpError as e:
            if e.resp.status in retriable_status_codes:
                error = 'A retriable HTTP error {:d} occurred:\n{}'.format(e.resp.status, e.content)
            else:
                raise
        except retriable_exceptions as e:
            error = 'A retriable error occurred: {}'.format(e)

        if error is not None:
            print(error)
            retry += 1
            sleep_seconds = min(random() * (2 ** retry), max_backoff)
            print('Sleeping {:f} seconds and then retrying...'.format(sleep_seconds))
            sleep(sleep_seconds)


def _get_client():
    with open(CREDENTIALS_FILE, 'r') as f:
        credentials_dict = load(f)

    updated_credentials = Credentials(
        credentials_dict['token'],
        credentials_dict['refresh_token'],
        '',
        credentials_dict['token_uri'],
        credentials_dict['client_id'],
        credentials_dict['client_secret'],
        credentials_dict['scopes']
    )

    with open(CREDENTIALS_FILE, 'w') as f:
        dump({'token': updated_credentials.token,
              'refresh_token': updated_credentials.refresh_token,
              'token_uri': updated_credentials.token_uri,
              'client_id': updated_credentials.client_id,
              'client_secret': updated_credentials.client_secret,
              'scopes': updated_credentials.scopes}, f)

    return build(API_SERVICE_NAME, API_VERSION, credentials=updated_credentials, cache_discovery=False)


def initialize_upload(yt_client, video_file):
    body = {
        'snippet': {
            'title': 'options.title',
            'description': 'Automatically uploaded from OctoPi on date',
        },
        'status': {
            'privacyStatus': 'unlisted'
        }
    }

    insert_request = yt_client.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_file,
                                   chunksize=-1, resumable=True)
    )

    def func():
        status, response = insert_request.next_chunk()
        if 'id' in response:
            print('Video ID \'{}\' was successfully uploaded.'.format(response['id']))
        else:
            exit('The upload failed with an unexpected response: {}'.format(response))

        return status, response

    exponential_backoff(func)


def main():
    initialize_upload(_get_client())
