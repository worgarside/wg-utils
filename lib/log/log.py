#!/usr/bin/env python3
import sys
from subprocess import Popen, PIPE, STDOUT
import re
from pathlib import Path
import argparse


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def main(**kwargs):
    usr_cmd = ["git", "config", "user.name"]
    po = Popen(usr_cmd, stdout=PIPE, stderr=PIPE)
    user_op, err = po.communicate()
    user_op_str = user_op.decode("utf-8").rstrip()


    try:
        day_val = kwargs['days']
        sys.argv.extend(['-d', day_val])
    except KeyError:
        pass


    parser = argparse.ArgumentParser(description='Generate log of git commits from all repos in specified dir')

    parser.add_argument('-d', '--days',
                        default=7,
                        type=int,
                        help='Number of days to retrieve. Default 7 days')

    parser.add_argument('-u', '--user',
                        default=user_op_str,
                        type=str,
                        help='User to lookup. Defaults to user set in global git config')

    parser.add_argument('-f', '--folder',
                        default="Sites",
                        type=str,
                        help='User folder to search in (e.g "Sites/repos"). Note: Uses home folder as a base ')

    parser.add_argument('-p', '--path',
                        default=None,
                        type=str,
                        help='Specify a full path for the repos location eg (/usr/joebloggs/repos/)')



    program_name = sys.argv[0]
    arguments = sys.argv[1:]
    arguments.remove('log')
    args = parser.parse_args(arguments)


    newargs = Namespace(
        days=kwargs.get('days', args.days),
        user=kwargs.get('user', args.user),
        folder=kwargs.get('folder', args.folder),
        path=kwargs.get('path', args.path)
    )

    args = newargs

    if args.path:
        search_folder = args.path
    else:
        search_folder = str(Path.home()) + "/" + args.folder


    addons_cmd = ["find", search_folder, "-maxdepth", "3", "-name", ".git", "-type", "d", "-prune"]
    p = Popen(addons_cmd, stdout=PIPE)
    addon_output = p.communicate()[0]
    addon_output_string = addon_output.decode("utf-8")

    cleaned_folders = []
    for line in addon_output_string.splitlines():
        if re.match(r'^\s*$', line):
            pass
        else:
            cleaned_folders.append(line)


    full_logs = []

    for f in cleaned_folders:
        logs_cmd = ["git", "--git-dir", f, "log", "--since={}.days".format(args.days), "--oneline", "--author={}".format(args.user), "--all"]
        pl = Popen(logs_cmd, stdout=PIPE, stderr=PIPE)
        logs_output, logs_err = pl.communicate()
        logs_output_string = logs_output.decode("utf-8").splitlines()

        repo_commits = []

        for s in logs_output_string:
            regex = r"(?P<hash>\w*)\s(?P<message>\w.*)$"
            matched = re.match(regex, s)
            if matched:

                hash = matched.group('hash')
                message = matched.group('message')

                merge_msg = re.match('^Merge branch .*$', message) # Merge branch 'x' with 'y'

                version_msg = re.match('^(v\w.*)$', message) # v3.2.3

                if not merge_msg and not version_msg:
                    repo_commits.append(message)
            else:
                pass

        if len(repo_commits) > 0:

            repo = dict()
            repo['name'] = f.rstrip('/.git').rsplit('/', 1)[1] # Strip .git and preceding dir path from dir path
            repo['commits'] = repo_commits
            full_logs.append(repo)

    for repo in full_logs:

        print("\033[1m{}\033[0m".format(repo['name']))
        for commit in repo['commits']:
            print(commit)


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Carl Topham'
    description = 'Generate log of the last N days of git commits in a folder'
    expected_args = {
        '--days': 'Number of days to retrieve. Default 7 days',
        '--user': 'Git username to search for commits. Defaults to user set in global git config',
        '--folder': 'User folder to search in (e.g "Sites/repos"). Note: Uses home folder as a base',
        '--path': 'Specify a full path for the repos location eg (/usr/joebloggs/repos/)'
    }
    env_list = {
    }

    return author, description, expected_args, env_list


if __name__ == '__main__':
    """ Ideally don't add anything to this top-level function, as it is skipped by the main.py entry script """
    main()
