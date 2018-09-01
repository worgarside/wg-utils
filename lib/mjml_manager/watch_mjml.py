from .helper.hash_functions import update_mjml_hash_file, gen_mjml_hash_dicts
from .helper.constants import MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, HTML_DIR, MJML_HASH_FILE
from time import sleep
from .deploy_mjml import compile_new_mjml_files


def main():
    try:
        print("Watching MJML files at '{}'. CTRL + C to stop.".format(MJML_TEMPLATE_DIR))
        while True:
            try:
                new_mjml_hashes, old_mjml_hashes = gen_mjml_hash_dicts(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR,
                                                                       MJML_HASH_FILE)
            except FileNotFoundError:
                print("MJML_HASH_FILE '{}' not found. Generating now.".format(MJML_HASH_FILE))
                update_mjml_hash_file(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, MJML_HASH_FILE)
                new_mjml_hashes, old_mjml_hashes = gen_mjml_hash_dicts(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR,
                                                                       MJML_HASH_FILE)
            if not new_mjml_hashes == old_mjml_hashes:
                compile_new_mjml_files(new_mjml_hashes, old_mjml_hashes)
            sleep(1)
    except KeyboardInterrupt:
        exit(0)


def user_help():
    author = 'Will Garside'
    description = "Watch MJML files at './{}' for updates and compile them to HTML files in './{}'" \
        .format('/'.join(MJML_TEMPLATE_DIR.split('/')[-2:]), '/'.join(HTML_DIR.split('/')[-2:]))
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == "__main__":
    main()
