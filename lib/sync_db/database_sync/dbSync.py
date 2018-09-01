from .utils.ui import *
from .utils.db import DatabaseEndpoint, DatabaseManager

from .constants import *


class DatabaseSync(object):
    args = None

    # tools
    heroku_team = None


    # transfer type
    sync_type = None

    # databases
    source = DatabaseEndpoint()
    dest = DatabaseEndpoint()

    # Overrides
    no_input = False

    def __init__(self, args):
        self.args = args

        if 'team' in args:
            self.heroku_team = args['team']
        else:
            # Try for env variables
            self.heroku_team = os.getenv('HEROKU_TEAM', None)

        self.database_manager = DatabaseManager(heroku_team=self.heroku_team)

        # if args['source']:
        if 'source' in args:
            # self.source = args['source']
            self.source.database_location = args['source']
        else:
            # Try for env variables
            source = os.getenv('SOURCE', None)
            if source:
                self.source.database_name, self.source.database_location = source.split("@")

        # if args['dest']:
        if 'dest' in args:
            self.dest.database_location = args['dest']
        else:
            # Try for env variables
            dest = os.getenv('DEST', None)
            if dest:
                self.dest.database_name, self.dest.database_location = dest.split("@")

        # if args['noinput']:
        if 'noinput' in args:
            self.no_input = True
        else:
            self.no_input = os.getenv('NO_INPUT', False)

        filter_group = [
            self.source.database_location,
            self.source.database_name,
            self.dest.database_location,
            self.dest.database_name,
        ]

        if self.no_input and not all(filter_group):
            exit("Using no input without source and destination set. This can't happen!")


    def __str__(self):
        return "App state"

    def create_backups(self, db):
        if db.database_location == LOCALHOST:
            self.database_manager.psql.dump_database(db)
        elif db.database_location == HEROKU:
            self.database_manager.heroku.dump_database(db)
        else:
            print("Unknown database")
            exit(0)

    def sync_to_heroku(self):
        print("Syncing Heroku to Heroku")

        # Download back up to home folder
        self.source.create_dump_paths()

        # Create and download Heroku backup to home folder
        self.create_backups(self.source)

        # Enter maintenance
        self.database_manager.heroku.maintenance(self.dest.database_name, True)

        # Copy the source DB to the Dest
        self.database_manager.heroku.copy_db(self.source.database_name, self.dest.database_name)

        # Exit maintenance
        self.database_manager.heroku.maintenance(self.dest.database_name, False)

        return True

    def sync_to_local(self):

        # Create new DB or drop old DB
        if self.dest.database_name == NEW_DATABASE:
            # Pick database_location for new DB
            self.dest.database_name = prompt_name("Name of new database?")
            self.dest.create_dump_paths()
        else:
            # Backup existing database to homefolder
            self.dest.create_dump_paths()
            self.create_backups(self.dest)

            # Drop existing Database
            self.database_manager.psql.drop_database(self.dest.database_name)

        print("Syncing {} to localhost".format(self.source.database_location))

        # Download backup to home folder
        self.source.create_dump_paths()

        # Create and download Heroku backup to home folder
        self.create_backups(self.source)

        # Create new database
        self.database_manager.psql.create_database(self.dest.database_name)

        # Restore downloaded Database to local
        self.database_manager.psql.restore_database(self.source, self.dest)

        # Return success
        return True

    def backup_all_heroku(self, heroku_dbs):
        print("Sync all Heroku instances")

        # Set the source to be heroku
        self.source.database_location = HEROKU
        # Set dest to be localhost
        self.dest.database_location = LOCALHOST

        for h_db in heroku_dbs:
            # Setup backup location for source
            self.source.database_name = h_db
            self.dest.database_name = h_db
            self.source.create_dump_paths()
            self.dest.create_dump_paths()
            self.create_backups(self.source)

            # Drop existing LOCAL Database
            if self.database_manager.psql.check_existing_database(self.dest.database_name):
                self.database_manager.psql.drop_database(self.dest.database_name)

            # Create new database
            self.database_manager.psql.create_database(self.dest.database_name)

            # Restore downloaded Database to local
            self.database_manager.psql.restore_database(self.source, self.dest)


        return True

    def begin_sync(self):
        if self.source.database_location == HEROKU and self.dest.database_location == HEROKU:
            success = self.sync_to_heroku()
        elif self.source.database_location == HEROKU and self.dest.database_location == LOCALHOST:
            success = self.sync_to_local()
        elif self.source.database_location == LOCALHOST and self.dest.database_location == LOCALHOST:
            success = self.sync_to_local()
        else:
            print("Something went wrong with the sync process!")

        return success

    def request_sync_type(self):
        transfer_opts = list()
        mapped_opts = None
        if self.database_manager.heroku_available:
            transfer_opts.append(HEROKU_HEROKU)
            if self.database_manager.psql_available:
                transfer_opts.append(HEROKU_LOCAL)

            mapped_opts = {
                'H': HEROKU_BACKUP_ALL
            }

            if BACKUP:
                transfer_opts.append(HEROKU_BACKUP)

        if self.database_manager.psql.available :
            transfer_opts.append(LOCAL_LOCAL)
            if BACKUP:
                transfer_opts.append(LOCAL_BACKUP)
                transfer_opts.append(FILE_LOCALHOST)

        self.sync_type = pick_database(transfer_opts, mapped_opts=mapped_opts, title="TYPE OF SYNC", text="What type of sync do you want to be done?")

        if self.sync_type == HEROKU_HEROKU:
            self.source.database_location = HEROKU
            self.dest.database_location = HEROKU
        elif self.sync_type == HEROKU_LOCAL:
            self.source.database_location = HEROKU
            self.dest.database_location = LOCALHOST
        elif self.sync_type == LOCAL_LOCAL:
            self.source.database_location = LOCALHOST
            self.dest.database_location = LOCALHOST


    def setup_source(self):
        if self.source.database_location == HEROKU:
            self.source.database_name = pick_database(self.database_manager.list_heroku_db(), title="SOURCE", text="Heroku ->", clear=True)
        elif self.source.database_location == LOCALHOST:
            self.source.database_name = pick_database(self.database_manager.list_psql_db(), title="SOURCE", text="Localhost (Postgres) ->", clear=True)

    def setup_dest(self):
        if self.dest.database_location == HEROKU:
            self.dest.database_name = pick_database(self.database_manager.list_heroku_db(), title="DESTINATION", text="-> Heroku", clear=True)
        elif self.dest.database_location == LOCALHOST:
            mapped_opts = {
                "N": NEW_DATABASE
            }
            self.dest.database_name = pick_database(self.database_manager.list_psql_db(), mapped_opts=mapped_opts, title="SOURCE", text="Localhost (Postgres) ->", clear=True)

    def setup_sync(self):

        self.request_sync_type()

        if self.sync_type == HEROKU_BACKUP_ALL:
            heroku_dbs = self.database_manager.list_heroku_db()
            success = self.backup_all_heroku(heroku_dbs)
        else:
            if not self.source.database_name:
                self.setup_source()

            if not self.dest.database_name:
                self.setup_dest()

            # Catch copy to self
            if self.source.database_location == self.dest.database_location and self.source.database_name == self.dest.database_name:
                box(
                    title="ERROR! CHOOSE AGAIN!",
                    text="Can't copy from/to the same database 🙈️",
                    vpad=1,
                    border="⚠︎",
                    clear=True
                )
                self.source.database_location = None
                self.source.database_name = None
                self.dest.database_location = None
                self.dest.database_name = None

                self.sync_type = None

                self.start()

            self.confirm_sync()

            success = self.begin_sync()

        if success:
            transaction = "{} @ {} => {} @ {}".format(
                self.source.database_name,
                self.source.database_location,
                self.dest.database_name,
                self.dest.database_location
            )

            box(
                title="SUCCESS 🚀",
                text= "{}. Have a nice day! 😬".format(transaction)
            )

            exit(0)

    def confirm_sync(self):
        # Disable the confirm dialog if noinput flag has been set
        if not self.no_input:
            # Confirm transaction
            confirm_copy_message = "Copy from \033[1m{} @ {}\033[0m to \033[1m{} @ {}\033[0m. Are you sure?".format(
                self.source.database_name,
                self.source.database_location,
                self.dest.database_name,
                self.dest.database_location,
            )

            # Add extra warnig about droping database if localhost and not NEW_DATABASE option
            if self.dest.database_location == LOCALHOST and self.dest.database_name == NEW_DATABASE:
                pass
            else:
                confirm_copy_message += "\n\033[93mWARNING: This will DROP/WIPE all data on {} @ {}\033[0m".format(
                    self.dest.database_name,
                    self.dest.database_location,
                )

            if confirm_dialog(confirm_copy_message) == 'n':
                box(title="Cancelled", text="Bye! 👋️", vpad=1)
                exit()

    def start(self):
        if self.source.database_name and self.dest.database_name:
            print("\033[1mSource and destination already database_name...\033[0m")

            self.confirm_sync()

            self.begin_sync()
        else:
            self.setup_sync()

    def welcome(self):
        box(
            title="Database sync tool",
            text="Sync Heroku, localhost and backup databases in a quick and simple way. "
                 "Note: This does require Heroku command line tools and/or psql for "
                 "all features to work!",
            clear=True
        )
