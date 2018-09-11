#!/usr/bin/env python3
from pyautogui import typewrite
from time import sleep
from sys import stdout


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                typewrite(line)

    except FileNotFoundError:
        print("Unable to find file '{}'".format(file_path))
    except IsADirectoryError:
        print("'{}' is a directory. Please provide a file.".format(file_path))


def main(**kwargs):
    if 'file' in kwargs:
        print('Typing in ', end='')
        for i in range(5, 0, -1):
            print('{}...'.format(i), end=' ')
            stdout.flush()
            sleep(1)
        print()

        read_file(kwargs['file'])


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Automatically type provided content to simulate human input'
    expected_args = {
        '--file': 'Path to source file to be re-typed'
    }
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    """ Ideally don't add anything to this top-level function, as it is skipped by the main.py entry script """
    main()
