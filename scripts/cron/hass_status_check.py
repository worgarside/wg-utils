from datetime import datetime
from os import getenv, path
from subprocess import Popen, PIPE
from time import sleep, time

from dotenv import load_dotenv
from requests import get, post
from requests.exceptions import ReadTimeout

NOW = datetime.now()

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)

load_dotenv(ENV_FILE)

PB_API_KEY = getenv('PB_API_KEY')
HASS_LOCAL_IP = getenv('HASSPI_LOCAL_IP')
HASS_PORT = getenv('HASS_PORT')


def send_notification(m, log_m=True):
    post(
        'https://api.pushbullet.com/v2/pushes',
        headers={
            'Access-Token': PB_API_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'body': m,
            'title': 'Home Assistant Status Check',
            'type': 'note'
        }
    )
    if log_m:
        log(m)


def log(m='', newline=False):
    with open('{}logs/hass_status_{}-{:02d}-{:02d}.log'.format(WGUTILS_DIR, NOW.year, NOW.month, NOW.day), 'a') as f:
        if newline:
            f.write('\n')
        f.write('\n[{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}]: {}'
                .format(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second, m)
                )


if __name__ == '__main__':
    log('Running status check. http://{}:{}'.format(HASS_LOCAL_IP, HASS_PORT), newline=True)
    start_time = time()
    server_unresponsive = True

    while server_unresponsive:
        try:
            req = get('http://{}:{}'.format(HASS_LOCAL_IP, HASS_PORT), timeout=5)
            message = "Server response: {} - {}".format(req.status_code, req.reason)
            if not req.status_code == 200:
                send_notification(message)
                raise ReadTimeout
            else:
                log(message)
            server_unresponsive = False
        except Exception as e:
            log(str(e))
            send_notification("Web server currently unresponsive. Attempting service restart.")

            stdout, stderr = Popen(['sudo', 'systemctl', 'restart', 'home-assistant@homeassistant.service'],
                                   stdout=PIPE, stderr=PIPE).communicate()
            sleep(30)
            if (time() - start_time) > 240:
                send_notification("Restart attempt time elapsed > 4 minutes. Rebooting pi.")
                log('Rebooting pi')
                log()
                stdout, stderr = Popen(['sudo', 'reboot'], stdout=PIPE, stderr=PIPE).communicate()
