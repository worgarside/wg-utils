from websocket import WebSocket
from time import sleep
from json import loads
from pprint import pprint
from requests import post, get
from datetime import datetime
from urllib.request import urlopen, Request
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
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



def main():
    ws = WebSocket()
    ws.connect('wss://stream.pushbullet.com/websocket/PB_API_KEY')

    # _send_notification('Print job finished', 'Arm_Piece_0.2mm_PLA_MK3.gcode finished printing in 2h 27min')

    while True:
        if loads(ws.recv())['type'] == 'tickle':
            now = datetime.now().timestamp() - 5

            res = get('https://api.pushbullet.com/v2/pushes?modified_after={}'.format(now), headers={
                'Access-Token': ''
            })

            valid_pushes = [push for push in res.json()['pushes'] if
                            'title' in push and 'print' in push['title'].lower()]

            if not len(valid_pushes) == 1:
                raise ValueError('Unexpected amount of valid pushes: {}'.format(len(valid_pushes)))

            # sleep(60)

            res = get('http://{}/api/timelapse'.format(OCTOPI_IP), headers={'X-Api-Key': ''})
            files = res.json()['files']
            newest_timelapse = sorted(files, key=lambda kv: kv['date'])[-1]

            url = 'http://{}{}'.format(OCTOPI_IP, newest_timelapse['url'])

            # tmp_file_path = ''
            request = Request(url)
            request.add_header('X-Api-Key', '')
            # with urlopen(request) as response, open(tmp_file_path, 'wb') as tmp_file:
            with urlopen(request) as response, NamedTemporaryFile(delete=False) as tmp_file:
                copyfileobj(response, tmp_file)


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
