from http.client import NotConnected, IncompleteRead, ImproperConnectionState, CannotSendRequest, CannotSendHeader, \
    ResponseNotReady, BadStatusLine
from os import getenv, path
from random import random
from time import sleep

from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error
from requests import post

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

SECRET_FILES_DIR = '{}secret_files/'.format(WGUTILS_DIR)
ENV_FILE = '{}.env'.format(SECRET_FILES_DIR)

load_dotenv(ENV_FILE)

MAX_RETRIES = 10

OCTOPI_HOST = getenv('OCTOPI_HOST')
OCTOPRINT_API_KEY = getenv('OCTOPRINT_API_KEY')

RETRIABLE_EXCEPTIONS = (
    HttpLib2Error, IOError, NotConnected, IncompleteRead, ImproperConnectionState, CannotSendRequest, CannotSendHeader,
    ResponseNotReady, BadStatusLine)

RETRIABLE_STATUS_CODES = (500, 502, 503, 504)


def exponential_backoff(func, max_retries=10, retriable_exceptions=RETRIABLE_EXCEPTIONS,
                        retriable_status_codes=RETRIABLE_STATUS_CODES, max_backoff=64):
    retry = 0
    response = None
    while response is None and retry < max_retries:
        try:
            status, response = func()
            return
        except HttpError as e:
            if e.resp.status in retriable_status_codes:
                error = 'A retriable HTTP error {:d} occurred:\n{}'.format(e.resp.status, e.content)
            else:
                raise
        except retriable_exceptions as e:
            error = 'Retriable Error: \n    {}'.format(e)

        if error is not None:
            print(error)
            retry += 1
            sleep_seconds = min(random() * (2 ** retry), max_backoff)
            print('Sleeping {} seconds...'.format(round(sleep_seconds, 2)))
            sleep(sleep_seconds)


def main():
    # def connect():
    #     res = post('http://{}/api/connection'.format(OCTOPI_HOST), headers={'X-Api-Key': OCTOPRINT_API_KEY},
    #                json={'command': 'connect'})
    #
    #     return res.status_code, res
    #
    # exponential_backoff(connect)
    pass


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = "Pings Octoprint API to ensure it's connected to the printer"
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
