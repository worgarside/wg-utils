from os import makedirs
from subprocess import Popen, PIPE

from git import Repo

HASS_DIR = '/home/hass/.homeassistant/'
SOURCE_DIR = '/home/pi/hass_config_src/'
CORE_FILES_LIST = '.core_files'
INDENT = '    '


def _compare_files(file1, file2):
    try:
        with open(file1) as f1:
            with open(file2) as f2:
                return f1.read() == f2.read()
    except FileNotFoundError:
        return False


def main():
    repo = Repo(SOURCE_DIR)
    print('Pulling from Git...')
    repo.remotes.origin.pull()

    with open(f'{HASS_DIR}{CORE_FILES_LIST}', 'r') as f:
        core_files = [x.rstrip('\n\r') for x in f.readlines()]

    with open(f'{HASS_DIR}.gitignore') as f:
        gitignore_files = set([x.rstrip('\n\r') for x in f.readlines()])

    files_to_copy = [(f'{SOURCE_DIR}{f}', f'{HASS_DIR}{f}') for f in core_files
                     if not _compare_files(f'{SOURCE_DIR}{f}', f'{HASS_DIR}{f}')
                     and f not in gitignore_files]
    print(f'{len(files_to_copy)} files to copy\n')

    for source, dest in files_to_copy:
        print(dest.replace(HASS_DIR, ''))
        p = Popen(['cp', source, dest], stdout=PIPE, stderr=PIPE)
        p.wait()
        output, error = p.communicate()
        while error:
            print(INDENT + error.decode('utf-8').rstrip('\n'))
            if 'no such file or directory' in error.decode('utf-8').lower():
                directory = '/'.join(error.decode('utf-8').split("'")[1].split('/')[:-1])
                print(f'{INDENT}Creating directory {directory}')
                makedirs(directory)
                p = Popen(['cp', source, dest], stdout=PIPE, stderr=PIPE)
                p.wait()
                output, error = p.communicate()
            else:
                break

    if input('Files copied. Restart home-assistant@homeassistant.service? (Y/n) ').lower() in {'y', ''}:
        Popen(['sudo', 'systemctl', 'restart', 'home-assistant@homeassistant.service'], stdout=PIPE, stderr=PIPE)\
            .communicate()


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Updates core files in homeassistant/.homeassistant'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
