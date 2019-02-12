from json import dumps
from os import popen, path, getenv, getloadavg

from dotenv import load_dotenv
from paho.mqtt.client import Client
from psutil import disk_usage, virtual_memory, cpu_percent

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)

load_dotenv(ENV_FILE)

MQTT_BROKER_HOST = getenv('MQTT_BROKER_HOST')
MQTT_TOPIC = getenv('RASPI_STATS_MQTT_TOPIC')


def get_cpu_temp():
    temp = popen('vcgencmd measure_temp').readline().replace('temp=', '').replace("'C", '')
    return float(temp)


def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)


def setup_mqtt():
    temp_client = Client()
    temp_client.on_connect = on_connect
    temp_client.connect(MQTT_BROKER_HOST, 1883, 60)
    return temp_client


def get_disk_free():
    return round(disk_usage('/home').free / 1024 ** 3, 1)


def get_memory_usage():
    return virtual_memory().percent


def get_cpu_usage():
    return round(cpu_percent(interval=None))


def get_load_15m():
    return getloadavg()[2]


def main():
    mqtt_client = setup_mqtt()

    stats = {
        'temperature': get_cpu_temp(),
        'disk_free': get_disk_free(),
        'memory_usage': get_memory_usage(),
        'cpu_usage': get_cpu_usage(),
        'load_15m': get_load_15m()
    }

    mqtt_client.publish(MQTT_TOPIC, payload=dumps(stats))


if __name__ == '__main__':
    main()
