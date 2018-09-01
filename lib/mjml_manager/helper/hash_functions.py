from pathlib import Path
from hashlib import sha1
from json import load, dump
from .constants import HTML_HASH_FILE, HTML_DIR, MJML_TEMPLATE_DIR, MJML_HASH_FILE, MJML_COMPONENT_DIR


def hash_file(file):
    sha = sha1()
    with open(file, 'rb') as f:
        while True:
            block = f.read(2 ** 10)  # one-megabyte blocks.
            if not block:
                break
            sha.update(block)
        return sha.hexdigest()


def compare_hash_dicts(new, old):
    updated_files = []

    for file_path, file_hash in new.items():
        try:
            if not old[file_path] == file_hash:
                updated_files.append(file_path)
        except KeyError:
            updated_files.append(file_path)
            if file_path.split('.')[-1] == 'html':
                update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
            elif file_path.split('.')[-1] == 'mjml':
                update_mjml_hash_file(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, MJML_HASH_FILE)

    return updated_files


# ------------------------------------ HTML ------------------------------------ #


def hash_html_files(html_dir):
    hashes = {}
    html_list = Path(html_dir).glob('**/*.html')

    for file_path in html_list:
        file_path = '/'.join(str(file_path).split('/')[-3:])
        hashes[file_path] = hash_file(file_path)

    return hashes


def update_html_hash_file(html_dir, html_hash_file):
    print('Updating html_hashes.json', end='')
    hashes = hash_html_files(html_dir)

    with open(html_hash_file, 'w') as f:
        dump(hashes, f)

    print(' \U0001F44D\n')


def gen_html_hash_dicts(html_dir, html_hash_file):
    new_html_hashes = hash_html_files(html_dir)
    try:
        with open(html_hash_file, 'r') as f:
            old_html_hashes = load(f)
    except FileNotFoundError:
        print("Unable to find HTML hash file '{}'. Generating now.".format('/'.join(HTML_HASH_FILE.split('/')[-2:])))
        update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
        with open(html_hash_file, 'r') as f:
            old_html_hashes = load(f)

    return new_html_hashes, old_html_hashes


# ------------------------------------ MJML ------------------------------------ #


def hash_mjml_files(mjml_template_dir, mjml_component_dir):
    hashes = {}
    template_list = Path(mjml_template_dir).glob('**/*.mjml')
    component_list = Path(mjml_component_dir).glob('**/*.mjml')

    for file_path in template_list:
        file_path = '/'.join(str(file_path).split('/')[-3:])
        hashes[file_path] = hash_file(file_path)

    for file_path in component_list:
        file_path = '/'.join(str(file_path).split('/')[-3:])
        hashes[file_path] = hash_file(file_path)

    return hashes


def update_mjml_hash_file(mjml_template_dir, mjml_component_dir, mjml_hash_file):
    print('Updating mjml_hashes.json', end='')
    hashes = hash_mjml_files(mjml_template_dir, mjml_component_dir)

    with open(mjml_hash_file, 'w') as f:
        dump(hashes, f)

    print(' \U0001F44D\n')


def gen_mjml_hash_dicts(mjml_template_dir, mjml_component_dir, mjml_hash_file):
    new_mjml_hashes = hash_mjml_files(mjml_template_dir, mjml_component_dir)

    try:
        with open(mjml_hash_file, 'r') as f:
            old_mjml_hashes = load(f)
    except FileNotFoundError:
        print("Unable to find MJML hash file '{}'. Generating now.".format('/'.join(MJML_HASH_FILE.split('/')[-2:])))
        update_mjml_hash_file(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, MJML_HASH_FILE)
        with open(mjml_hash_file, 'r') as f:
            old_mjml_hashes = load(f)

    return new_mjml_hashes, old_mjml_hashes
