#!/usr/bin/env python3
# This is to import all scripts exported by the __init__.py script - DO NOT REMOVE
# noinspection PyUnresolvedReferences
from lib import *
from argparse import ArgumentParser
from math import ceil
from textwrap import wrap
from os import listdir, path, system, name, environ, getcwd

try:
    with open('{}/.env'.format(getcwd()), 'r') as env_file:
        env_vars = env_file.read().splitlines()

        for env_var in env_vars:
            if env_var.startswith('#'):
                continue
            key, value = env_var.split('=')
            environ[key] = value
except FileNotFoundError:
    pass

HELP_COL_WIDTHS = {
    'module': 45,
    'author': 32
}


def walk(top, max_depth):
    dirs, files = [], []
    for file in listdir(top):
        (dirs if path.isdir(path.join(top, file)) else files).append(file)
    yield top, dirs, files
    if max_depth > 1:
        for subdir in dirs:
            for x in walk(path.join(top, subdir), max_depth - 1):
                yield x


def get_modules():
    dirname, _ = path.split(path.abspath(__file__))
    exportable_modules = []
    current_file_loc = '/'.join(__file__.split('/')[:-1])

    lib_loc = '{}/lib'.format(current_file_loc)

    for root, dirs, _ in walk(lib_loc, 1):
        for sub_dir in dirs:
            if not sub_dir == '__pycache__':
                for _, _, files in walk(path.join(root, sub_dir), 0):
                    for file in files:
                        if file.split('.')[-1] == 'py' and not file == '__init__.py':
                            exportable_modules.append('{}.{}'.format(sub_dir, file[:-3]))

    return exportable_modules


def print_help_box(title=None, author=None, description=None):
    def cap_line(string='', length=40, color=None):
        str_len = len(string)

        rjust_space = (length - str_len) // 2
        ljust_space = int(ceil((length - str_len) / 2))

        if color:
            string = "{}{}\033[0m".format(color, string)

        return '{}{}{}'.format('|'.ljust(ljust_space), string, '|'.rjust(rjust_space))

    width = 60
    border_line = '~' * width

    print(border_line)
    print(cap_line(length=width))

    max_text_width = width - 6

    if title:
        print(cap_line(title.upper(), length=width, color='\033[1m\033[91m'))

    if author:
        print(cap_line('Author: {}'.format(author), length=width, color='\033[95m'))

    if description:
        text_split = wrap(description, max_text_width, replace_whitespace=False)
        for line in text_split:
            print(cap_line(line, length=width, color='\033[96m'))

    print(cap_line(length=width))
    print(border_line, end='\n\n')


def display_module_specific_help(module_name):
    author = description = expected_args = env_list = None
    try:
        user_help = getattr(eval(module_name), 'user_help')
        try:
            author, description, expected_args, env_list = user_help()
        except ValueError:
            exit('Not enough values returned from {}.user_help. Cannot continue.'.format(module_name))
        print_help_box(title=module_name, author=author, description=description)
        if len(expected_args) > 0:
            print('\n\33[4mAccepted arguments:\33[0m ')
            for key in expected_args:
                desc = expected_args[key]
                print(' {} {}'.format(key.ljust(12), desc))

        if len(env_list) > 0:
            print('\n\33[4mEnvironment variables:\33[0m')
            for key in env_list:
                value = env_list[key]
                print(' {}={}'.format(key, value))

            if input('\n> Output to sample env file? [Y/n] ').lower() in {'y', ''}:
                with open('{}.env'.format(module_name), 'w') as file:
                    for key in env_list:
                        value = env_list[key]
                        file.write('{}={}\n'.format(key, value))
                print("Done! See '{}.env".format(module_name))

        print()
    except AttributeError:
        print_help_box(
            title=module_name,
            author='Unknown',
            description='{}.user_help is undefined. No arguments have been provided either. '
                        'Good luck using the script!'.format(module_name)
        )
        exit()
    except NameError:
        print("Sorry, that module is not available. Here's the default help instead.")
        display_default_help()


def display_default_help():
    author = description = None
    print_help_box(
        title='wg-utils',
        author='Will Garside',
        description='Simple-ish scripts to make my life easier (mainly on my Pi). See the list below.'
    )

    print('To run: \33[1mwg-utils <module.name> [--key value]\33[0m')
    print('For more info: \33[1mwg-utils <module.name> --help\33[0m\n')

    print('{}{}{}'.format(
        '\33[4mModule\33[0m'.ljust(HELP_COL_WIDTHS['module']),
        '\33[4mAuthor\33[0m'.ljust(HELP_COL_WIDTHS['author']),
        '\33[4mDescription\33[0m'
    ))

    for module_path in get_modules():
        module = module_path.split('.')[-1]
        try:
            user_help = getattr(eval(module), 'user_help')
            try:
                author, description, _, _ = user_help()
            except ValueError:
                exit('Not enough values returned from {}.user_help. Cannot continue.'.format(module))
            print('{}{}{}'.format(
                module_path.ljust(HELP_COL_WIDTHS['module'] - 8),
                author.ljust(HELP_COL_WIDTHS['author'] - 8),
                description
            ))
        except AttributeError:
            print('{}\033[1m\033[91m{}{}\033[0m'.format(
                module_path.ljust(HELP_COL_WIDTHS['module'] - 8),
                '{}.user_help is not defined'.format(module),
                ''
            ))
    print()


def parse_args(args):
    kwarg_dict = {}
    while len(args) > 0:
        if args[0].startswith('--'):
            key = args[0][2:]
            if len(args) > 1 and not args[1].startswith('--') and not args[1].startswith('-'):
                value = args[1]
                del args[1]
            else:
                value = True
            del args[0]

            kwarg_dict[key] = value
        elif args[0].startswith('-'):
            key = args[0][1:]
            if len(args) > 1 and not args[1].startswith('--') and not args[1].startswith('-'):
                value = args[1]
                del args[1]
            else:
                value = True
            del args[0]
            kwarg_dict[key] = value
        else:
            kwarg_dict[args[0]] = args[0]
            del args[0]

    return kwarg_dict


def get_main_function(args):
    try:
        return getattr(eval(args[0]), 'main')
    except (TypeError, NameError):
        exit("'{}' is not a valid utility. Exiting.".format(args[0]))
    except IndexError:
        display_default_help()
        exit(0)


def main():
    root_parser = ArgumentParser(add_help=False)
    _, args = root_parser.parse_known_args()
    system('cls' if name == 'nt' else 'clear')

    if len(args) == 0 or len({'--help', '-h'} & set(args)) > 0:
        if len(args) > 0:
            try:
                args.remove('--help')
            except ValueError:
                args.remove('-h')
            display_module_specific_help(args[0])
        else:
            display_default_help()
        exit(0)

    func = get_main_function(args)

    del args[0]
    kwarg_dict = parse_args(args)
    func(**kwarg_dict)


if __name__ == '__main__':
    main()
