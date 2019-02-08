from requests import get, post
from requests.exceptions import ReadTimeout
from subprocess import Popen, PIPE
from time import sleep, time
from datetime import datetime
from dotenv import load_dotenv
from os import getenv

NOW = datetime.now()

load_dotenv()

PB_API_KEY = getenv('PB_API_KEY')


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
    with open('/home/pi/Projects/wg-utils/logs/hass_status_{}-{:02d}-{:02d}.log'.format(NOW.year, NOW.month, NOW.day),
              'a') as f:
        if newline:
            f.write('\n')
        f.write('\n[{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}]: {}'
                .format(NOW.year, NOW.month, NOW.day, NOW.hour, NOW.minute, NOW.second, m)
                )


if __name__ == '__main__':
    log('Running status check.', newline=True)
    start_time = time()
    server_unresponsive = True
    while server_unresponsive:
        try:
            req = get('http://192.168.1.2:8123', timeout=5)
            message = 'Server response: {} - {}'.format(req.status_code, req.reason)
            if not req.status_code == 200:
                send_notification(message)
                raise ReadTimeout
            else:
                log(message)
            server_unresponsive = False
        except Exception as e:
            log(str(e))
            send_notification('Web server currently unresponsive. Attempting service restart.')

            stdout, stderr = Popen(['sudo', 'systemctl', 'restart', 'home-assistant@homeassistant.service'],
                                   stdout=PIPE, stderr=PIPE).communicate()
            sleep(30)
            if (time() - start_time) > 240:
                send_notification('Restart attempt time elapsed > 4 minutes. Rebooting pi.')
                log('Rebooting pi')
                log()
                stdout, stderr = Popen(['sudo', 'reboot'], stdout=PIPE, stderr=PIPE).communicate()
                exit()
