#!/usr/bin/env python3


def main(**kwargs):
    """
    The entry point of your utility script.
    This is the function which will be globally accessible from the cfl-utils package
    :param kwargs: a dictionary of kwargs in the form { key: value | True }
    """
    pass


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Guido van Rossum'
    description = 'Short description of what the script does'
    expected_args = {
        '--key': 'Description of what the argument does'
    }
    env_list = {
        'VARIABLE': 'value',
        'FILE': 'sample'
    }

    return author, description, expected_args, env_list


if __name__ == '__main__':
    """ Ideally don't add anything to this top-level function, as it is skipped by the main.py entry script """
    main()
