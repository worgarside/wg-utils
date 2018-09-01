from os import getcwd
from main import environ

MJML_TEMPLATE_DIR = '{}/src/templates'.format(getcwd())
MJML_COMPONENT_DIR = '{}/src/components'.format(getcwd())
HTML_DIR = '{}/dist/templates'.format(getcwd())
HTML_HASH_FILE = '{}/html_hashes.json'.format(getcwd())
MJML_HASH_FILE = '{}/mjml_hashes.json'.format(getcwd())
BUCKET_NAME = environ.get('AWS_BUCKET_NAME')
ASSET_DIR = '{}/src/assets'.format(getcwd())
