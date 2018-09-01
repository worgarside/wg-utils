import json
import os
from subprocess import Popen, PIPE, STDOUT
import re


def is_tool(name):
    """Check whether `database_location` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None


class Tool(object):

    name = None

    available = False

    def __init__(self, name=None):
        if not name:
            raise RuntimeError('A database_location needs to be supplied to this Tool')
        self.name = name
        self.available = is_tool(self.name)


class Heroku(Tool):

    team = None

    def list_databases(self):

        print("Loading data for Heroku...")

        cmd = ["heroku", "list", "--json"]
        if self.team:
            cmd.append("-t")
            cmd.append(self.team)

        p = Popen(cmd, stdout=PIPE)
        output = p.communicate()[0]
        output_string = output.decode("utf-8")
        json_decoded = json.loads(output_string)

        # file_list = output.splitlines()
        db_list = list()

        for row in json_decoded:
            addons_cmd = ["heroku", "addons", "--json", "--app", row['name']]
            p = Popen(addons_cmd, stdout=PIPE)
            addon_output = p.communicate()[0]
            addon_output_string = addon_output.decode("utf-8")
            addon_json_decoded = json.loads(addon_output_string)

            for x in addon_json_decoded:
                for var in x['config_vars']:
                    if var == "DATABASE_URL":
                        db_list.append(row['name'])

        return db_list

    def dump_database(self, db):
        try:
            cmd = ["heroku", "pg:backups:capture", "--app", db.database_name]
            p = Popen(cmd, stdout=PIPE)
            p.wait()
            output_path = os.path.join(db.dump_location, db.dump_file_name)
            download_cmd = ["heroku","pg:backups:download", "--app", db.database_name, '-o', output_path]
            p = Popen(download_cmd, stdout=PIPE)
            p.wait()
        except TypeError:
            pass

    @staticmethod
    def maintenance(app, on=True):

        if on:
            state = "on"
        else:
            state = "off"

        cmd = ["heroku", "maintenance:{}".format(state), "--app", app]

        p = Popen(cmd, stdout=PIPE)
        p.wait()


    @staticmethod
    def copy_db(source_name, dest_name):
        cmd = ["heroku", "pg:copy", "{}::DATABASE_URL".format(source_name), "DATABASE_URL", "--app", dest_name]
        p = Popen(cmd, stdout=PIPE)
        p.wait()


    def __init__(self, team=None):
        super().__init__(name="heroku")
        self.team = team


class Psql(Tool):

    def restore_database(self, db_src, db_dest):
        restore_path = os.path.join(db_src.dump_location, db_src.dump_file_name)
        restore_path_log = os.path.join(db_dest.dump_location, db_dest.dump_file_name + ".log")

        logfile = open(restore_path_log, 'w')

        cmd = ["pg_restore", "--verbose", "--clean", "--no-acl", "--no-owner", "--dbname={}".format(db_dest.database_name), restore_path]
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        for line in p.stdout:
            # sys.stdout.write(line.decode("utf-8")) # Write to shell
            logfile.write(line.decode("utf-8")) # Write to logfile

        p.wait()

    def dump_database(self, db):

        cmd = ["pg_dump", "-Fc", db.database_name]
        p = Popen(cmd, stdout=PIPE)
        output = p.communicate()[0]
        p.wait()

        with open(os.path.join(db.dump_location, db.dump_file_name), 'w+b') as file:
            file.write(output)


    def drop_database(self, db_name):
        cmd = [
            "psql", "postgres", "-c",
            "DROP DATABASE \"{}\";".format(db_name)
        ]
        p = Popen(cmd, stdout=PIPE)
        p.wait()

    def create_database(self, db_name):
        cmd = [
            "psql", "postgres", "-c",
            "CREATE DATABASE \"{}\" WITH ENCODING 'UTF8';".format(db_name)
        ]
        p = Popen(cmd, stdout=PIPE)
        p.wait()

    def check_existing_database(self, db_name):
        cmd = [
            "psql", "-tAc",
            "SELECT 1 FROM pg_database WHERE datname='{}'".format(db_name)
        ]
        p = Popen(cmd, stdout=PIPE)

        output = p.communicate()[0]

        p.wait()

        if output.decode("utf-8") != '':
            return True
        else:
            return False

    @staticmethod
    def list_databases():
        cmd = [
            "psql", "postgres", "-c",
            "SELECT datname FROM pg_database WHERE datistemplate = false;"
        ]
        p = Popen(cmd, stdout=PIPE)
        output = p.communicate()[0]
        file_list = output.splitlines()

        db_list = list()

        string_black_list = [
            "datname",
            "postgres",
        ]

        row_count_pattern = re.compile('\(.+\)')

        for row in file_list:
            cleaned_row = row.decode("utf-8").strip()

            filter_group = [
                not cleaned_row.startswith("-----"),
                len(cleaned_row) != 0,
                not any(cleaned_row in s for s in string_black_list),
                not row_count_pattern.match(cleaned_row)
            ]

            if all(filter_group):
                db_list.append(cleaned_row)

        return db_list

    def __init__(self):
        super().__init__(name="psql")
