import time
from pathlib import Path
import datetime
import os

from .tools import Heroku, Psql, is_tool


class DatabaseEndpoint(object):
    """
    Manages the endpoint for a database for sync and backup
    """

    database_location = None

    database_name = None

    dump_location = None

    dump_file_name = None

    timestamp = None

    def create_dump_paths(self):
        time.strftime('%Y%m%d')
        home = str(Path.home())

        self.dump_location = os.path.join(home, "db_backups/{}".format(self.database_location))

        params = {
            "database": self.database_name,
            "date": self.timestamp.strftime('%Y%m%d'),
            "time": self.timestamp.strftime("%H%M")
        }

        self.dump_file_name = "{database}_{date}_{time}.dump".format(**params)

        if not os.path.exists(self.dump_location):
            os.makedirs(self.dump_location)

    def __init__(self):
        self.timestamp = datetime.datetime.today()


class DatabaseManager():
    """
    Controls the database management, caching and interaction with the cmd line tools
    """
    heroku_team = None
    heroku_available = False
    heroku_dbs = None

    psql_available = False
    psql_dbs = None
    psql = Psql()


    def list_heroku_db(self):
        if self.heroku_available:
            if self.heroku_dbs is None:
                # get list and update manager
                self.heroku_dbs = self.heroku.list_databases()
            else:
                # use cached list
                pass
            return self.heroku_dbs

    def list_psql_db(self):
        if self.psql_available:
            if self.psql_dbs is None:
                self.psql_dbs = self.psql.list_databases()
            else:
                pass
                # use cached list
            return self.psql_dbs

    def __init__(self, heroku_team=None):
        self.heroku_team = heroku_team
        self.heroku_available = is_tool('heroku')
        self.psql_available = is_tool('psql')

        self.heroku = Heroku(team=heroku_team)
