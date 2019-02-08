from os import path
from subprocess import Popen, PIPE
from sys import stdout
from time import sleep


def start_vpn():
    print('Starting VPN...', end=' ')
    stdout.flush()
    cmd = ['sudo']
    config_path = '{}/config/config.ovpn'.format(path.dirname(path.abspath(__file__)))
    login_path = '{}/config/login.txt'.format(path.dirname(path.abspath(__file__)))
    arg_list = ['-b', 'openvpn', '--config', config_path, '--auth-user-pass', login_path]
    Popen(cmd + arg_list, stdout=PIPE)
    sleep(10)


def disable_vpn():
    print('Attempting to disable VPN...', end=' ')
    stdout.flush()
    cmd = ['sudo']
    arg_list = ['killall', 'openvpn']
    p = Popen(cmd + arg_list, stdout=PIPE)
    p.wait()
    output, _ = p.communicate()


def get_ip():
    cmd = ['wget']
    arg_list = ['http://ipinfo.io/ip', '-qO', '-']

    p = Popen(cmd + arg_list, stdout=PIPE)
    p.wait()
    output, _ = p.communicate()
    return output.decode('utf-8')


def main():
    initial_ip = get_ip()
    disable_vpn()
    disabled_ip = get_ip()

    if initial_ip == disabled_ip:
        print("IP unchanged, VPN wasn't running.")
    else:
        print('Done.')

    start_vpn()
    new_ip = get_ip()

    if initial_ip == new_ip:
        print('Success.\nVPN was already running. IP is {}'.format(new_ip))
    elif disabled_ip == new_ip:
        print('Failure.\nVPN unable to start. IP is {}'.format(new_ip))
    else:
        print('Success.\nVPN started. IP is {}'.format(new_ip))


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Start OPENVPN // PIA'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
