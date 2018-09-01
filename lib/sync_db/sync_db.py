#!/usr/bin/env python3
import os
import sys

from .database_sync.dbSync import DatabaseSync

# Get args from command line
from .database_sync.utils.ui import box


def main(**kwargs):
    try:
        # Create a new database sync tool
        database_sync = DatabaseSync(kwargs)
        # Welcome the user
        database_sync.welcome()
        #
        database_sync.start()

    except KeyboardInterrupt:
        # Catch keyboard interrupt quitting!
        print("")
        box(
            title="So long quitter 👋",
            text="And thanks for all the bits! 🤖"
                 ""
        )
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


def user_help():
    author = 'Carl Topham'
    description = 'Copy and sync Heroku & local databases'
    expected_args = {
        '--team': 'Team to use for Heroku sync',
        '--source': 'Database database_location to sync from',
        '--dest': 'Database database_location to sync to',
        '--noinput': 'Skip all user input. This will only work if source and dest are set as flags or as ENVVARS'
    }
    env_list = {
        'TEAM':'heroku_team_name',
        'SOURCE':'database@heroku',
        'DEST':'database@localhost',
        'NOINPUT':'skip_all_user_input'
    }
    return author, description, expected_args, env_list


if __name__ == "__main__":
    main()
