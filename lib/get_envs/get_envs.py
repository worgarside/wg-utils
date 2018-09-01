#!/usr/bin/env python3
from subprocess import Popen, PIPE
import time

VARIABLE_BLACKLIST = ['HEROKU_SLUG_COMMIT', 'HEROKU_APP_NAME', 'TERM', 'LIBRARY_PATH', 'GUNICORN_CMD_ARGS',
                      'HEROKU_RELEASE_CREATED_AT', 'TINFOILSECURITY_SCAN_SCHEDULE', 'LD_LIBRARY_PATH', 'DYNO',
                      'PYTHONHASHSEED', 'PATH', 'WEB_CONCURRENCY', '_', 'HEROKU_APP_ID', 'DYNO_RAM', 'HEROKU_DYNO_ID',
                      'PS1', 'SHLVL', 'HOME', 'FORWARDED_ALLOW_IPS', 'PYTHONPATH', 'DATABASE_URL', 'PORT', 'DEBUG',
                      'PYTHONHOME', 'HEROKU_RELEASE_VERSION', 'STAGING_DATABASE_URL', 'PWD', 'HEROKU_SLUG_DESCRIPTION',
                      'AUTH0_DOMAIN', 'ERROR_PAGE_URL', 'SECURE_SSL_REDIRECT', 'ENV', 'MAINTENANCE_PAGE_URL',
                      'AUTH0_REDIRECT_URL', 'PAPERTRAIL_API_TOKEN', 'SECRET_KEY', 'AUTH0_PUBLIC_KEY', 'LANG']


def download_envs(app_name):
    cmd = ['heroku', 'run', 'printenv', '--app', app_name]

    p = Popen(cmd, stdout=PIPE)
    output, _ = p.communicate()

    var_list = output.splitlines()

    if len(output) == 0:
        exit("Unable to find app '{}'".format(app_name))

    return var_list


def create_envfile(app_name, env_list):
    file_name = '{}-{}.env'.format(app_name, time.strftime('%Y%M%d%H%M%S'))
    with open(file_name, 'a') as outfile:
        for var in env_list:
            kv_pair = var.decode('utf-8').split()[0]
            key = kv_pair.split('=')[0]
            if key not in VARIABLE_BLACKLIST:
                outfile.write('{}\n'.format(kv_pair))

        outfile.write('DATABASE_URL=postgres://username:password@localhost:5432/db_name\n')
        outfile.write('DEBUG=True\n')
        outfile.write('SECURE_SSL_REDIRECT=False\n')
        outfile.write('ENV=dev')


def main(**kwargs):
    if 'app-name' not in kwargs:
        kwargs['app-name'] = input('Please provide an app name: ')

    env_list = download_envs(kwargs['app-name'])
    create_envfile(kwargs['app-name'], env_list)


def user_help():
    author = 'Will Garside'
    description = 'Pull env vars from a Heroku app and save to current working directory'
    expected_args = {
        '--app-name': 'The Heroku app to grab env vars from'
    }
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
