from importlib.util import spec_from_file_location, module_from_spec
from os import getenv
from os import path

from dotenv import load_dotenv
from paho.mqtt.client import Client
from pigpio import pi
from json import dumps

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)

load_dotenv(ENV_FILE)

MQTT_BROKER_HOST = getenv('MQTT_BROKER_HOST')
DHT22_GPIO = getenv('DHT22_GPIO')
MQTT_TOPIC = getenv('DHT22_MQTT_TOPIC')

spec = spec_from_file_location('dht22', '{}utilities/dht22.py'.format(WGUTILS_DIR))
DHT22 = module_from_spec(spec)
spec.loader.exec_module(DHT22)


def on_connect(client, userdata, flags, rc):
    client.subscribe(MQTT_TOPIC)
    if not rc == 0:
        print('wtf')


def setup_mqtt():
    temp_client = Client()
    temp_client.on_connect = on_connect
    temp_client.connect('192.168.1.2', 1883, 60)
    return temp_client


def main():
    mqtt_client = setup_mqtt()
    s = DHT22.Sensor(pi(), 16)
    s.trigger()
    mqtt_client.publish(MQTT_TOPIC, payload=dumps({'temperature': s.temperature(), 'humidity': s.humidity()}))


if __name__ == '__main__':
    main()
