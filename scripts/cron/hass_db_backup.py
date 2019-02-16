from psycopg2 import connect
from os import path, getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta

WGUTILS = 'wg-utils'
DIRNAME, _ = path.split(path.abspath(__file__))
WGUTILS_DIR = DIRNAME[:DIRNAME.find(WGUTILS) + len(WGUTILS)] + '/'

ENV_FILE = '{}secret_files/.env'.format(WGUTILS_DIR)

load_dotenv(ENV_FILE)

DB_URL = getenv('HASS_DB_URL')
HASS_BACKUP_DIR = getenv('HASS_BACKUP_DIR')


def main():
    con = None

    try:
        con = connect(DB_URL)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM states WHERE last_updated::date < '{(datetime.today().date())}'")

        file_name = f'{HASS_BACKUP_DIR}hass_backup_{datetime.today().date() - timedelta(days=1)}.sql'

        with open(file_name, 'w') as f:
            for row in cur:
                f.write(f'INSERT INTO states VALUES ({str(row)});')
    except Exception as e:
        print(f'Error {e}')
        exit(1)
    finally:
        if con:
            con.close()


if __name__ == '__main__':
    main()
