from datetime import datetime
from http.client import NotConnected, IncompleteRead, ImproperConnectionState, CannotSendRequest, CannotSendHeader, \
    ResponseNotReady, BadStatusLine
from json import dump, load, loads
from os import getenv, path
from random import random
from re import compile
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from time import sleep, strptime, strftime
from urllib.request import urlopen, Request

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from httplib2 import HttpLib2Error
from requests import get, post
from websocket import WebSocket

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

SECRET_FILES_DIR = '{}secret_files/'.format(WGUTILS_DIR)
CLIENT_SECRETS_FILE = '{}google_client_secrets.json'.format(SECRET_FILES_DIR)
CREDENTIALS_FILE = '{}google_credentials.json'.format(SECRET_FILES_DIR)
ENV_FILE = '{}.env'.format(SECRET_FILES_DIR)

load_dotenv(ENV_FILE)

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

PB_API_KEY = getenv('PB_API_KEY')
OCTOPI_HOST = getenv('OCTOPI_HOST')
OCTOPRINT_API_KEY = getenv('OCTOPRINT_API_KEY')

LAYER_HEIGHT_REGEX = compile(r"(?:100(?:\.00?)?|\d?\d(?:\.\d\d?)?mm)")


def _send_notification(t, m):
    post(
        'https://api.pushbullet.com/v2/pushes',
        headers={
            'Access-Token': PB_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'body': m,
            'title': t,
            'type': 'note'
        }
    )


def wait_for_pb_notif(ws):
    ws.connect('wss://stream.pushbullet.com/websocket/{}'.format(PB_API_KEY))

    valid_pushes = []

    while not len(valid_pushes):
        if loads(ws.recv())['type'] == 'tickle':
            notif_time = datetime.now().timestamp() - 10

            res = get('https://api.pushbullet.com/v2/pushes?modified_after={}'.format(notif_time), headers={
                'Access-Token': PB_API_KEY
            })

            valid_pushes = [push for push in res.json()['pushes'] if
                            'title' in push and 'print' in push['title'].lower()]

            if len(valid_pushes) > 1:
                raise ValueError('Unexpected amount of valid pushes: {}'.format(len(valid_pushes)))
        sleep(30)

    sleep(60)  # Make sure Octolapse has rendered properly


def get_timelapse_file():
    res = get('http://{}/api/timelapse'.format(OCTOPI_HOST), headers={'X-Api-Key': OCTOPRINT_API_KEY})

    if not res.status_code == 200:
        raise ConnectionError('Request to Octoprint failed.')

    files = res.json()['files']
    newest_timelapse = sorted(files, key=lambda kv: kv['date'])[-1]

    url = 'http://{}{}'.format(OCTOPI_HOST, newest_timelapse['url'])

    request = Request(url)
    request.add_header('X-Api-Key', OCTOPRINT_API_KEY)

    with urlopen(request) as response, NamedTemporaryFile(delete=False) as tmp_file:
        copyfileobj(response, tmp_file)

    return tmp_file, newest_timelapse


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


def initialize_upload(yt_client, video_file, metadata):
    body = {
        'snippet': {
            'title': metadata['format_title'],
            'description': metadata['description'],
        },
        'status': {
            'privacyStatus': metadata['privacy_status']
        }
    }

    insert_request = yt_client.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_file.name, chunksize=-1, resumable=True)
    )

    def upload_video():
        status, response = insert_request.next_chunk()

        if 'id' in response:
            _send_notification('Octolapse uploaded',
                               "Octolapse '{}' successfully uploaded: https://youtu.be/{}"
                               .format(metadata['format_title'], response['id']))
        else:
            exit('The upload failed with an unexpected response: {}'.format(response))

        return status, response

    exponential_backoff(upload_video)


def main():
    while True:
        wait_for_pb_notif(WebSocket())
        tmp_file, metadata = get_timelapse_file()
        file_name = '.'.join(metadata['name'].split('.')[:-1]).replace('_MK3_', '')
        date = strptime(metadata['date'], '%Y-%m-%d %H:%M')
        title = file_name[:-14].replace('_', ' ')
        pipe_pos = [m.start() for m in LAYER_HEIGHT_REGEX.finditer(title)][0]

        metadata['format_title'] = '{}| {} on Prusa Mk3 | {}'.format(title[:pipe_pos], title[pipe_pos:],
                                                                     strftime('%H:%M %d/%m/%Y', date))
        metadata['description'] = 'Filmed with Octolapse on a Pi Camera v2. ' \
                                  'Automatically uploaded post-render through custom scripts.'
        metadata['privacy_status'] = 'unlisted'

        initialize_upload(_get_client(), tmp_file, metadata)
        sleep(1800)


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = "Uploads a timelapse to YouTube when it's completed by Octoprint"
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
