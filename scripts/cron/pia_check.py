from bs4 import BeautifulSoup
from requests import get, post
from pprint import pprint
from subprocess import Popen, PIPE
from os import path, getenv
from dotenv import load_dotenv
from time import sleep

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)
BS4_PARSER = 'html.parser'
PIA_URL = 'https://www.privateinternetaccess.com/pages/whats-my-ip/'
WARNING = 'Your private information is exposed'
MAX_VPN_ATTEMPTS = 5

load_dotenv(ENV_FILE)

PIA_CONFIG = getenv('PIA_CONFIG_PATH')
PB_API_KEY = getenv('PB_API_KEY')


def notify(t='PIA Alert', m=''):
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

    return True


def restart_pia():
    stop_process_cmds = 'sudo systemctl stop openvpn_pia.service'.split()
    p = Popen(stop_process_cmds, stdout=PIPE)
    p.wait()
    start_cmds = f'sudo -b /usr/sbin/openvpn {PIA_CONFIG}'.split()

    Popen(start_cmds, stdout=PIPE, stderr=PIPE)


def check_status():
    res = get(PIA_URL)

    if not res.status_code == 200:
        # TODO: replace with Ex Backoff
        exit('Unable to connect to server')

    soup = BeautifulSoup(res.content, BS4_PARSER)
    ip_box = soup.find('div', {'class': 'ipbox-light'})

    return WARNING not in str(ip_box)


def kill_deluge():
    stop_process_cmds = 'sudo pkill deluge'.split()
    Popen(stop_process_cmds, stdout=PIPE)


def main():
    retry = 0
    notified = False
    while not check_status() and retry < MAX_VPN_ATTEMPTS:
        notified = notify(m=f'PIA not running, starting restart process') if not notified else notified

        if not path.isfile(PIA_CONFIG):
            notify(m=f'{PIA_CONFIG} is not a valid file.')
            break

        retry += 1
        restart_pia()
        sleep(30)

        if check_status():
            notify(m=f"PIA successfully restarted with {retry} attempt{'s' if retry > 1 else ''}.")
            exit()

    if not check_status():
        notify(m='Unable to restart PIA. Stopping deluge.')
        kill_deluge()


if __name__ == '__main__':
    main()
