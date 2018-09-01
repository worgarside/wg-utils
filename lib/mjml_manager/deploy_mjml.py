from subprocess import call, Popen, PIPE
from .helper.constants import MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, HTML_DIR, MJML_HASH_FILE, HTML_HASH_FILE, \
    BUCKET_NAME
from .helper.hash_functions import update_html_hash_file, update_mjml_hash_file, compare_hash_dicts, \
    gen_mjml_hash_dicts, gen_html_hash_dicts


def deploy_all_html_files():
    new_html_hashes, _ = gen_html_hash_dicts(HTML_DIR, HTML_HASH_FILE)

    files_to_deploy = []
    for file_path, file_hash in new_html_hashes.items():
        files_to_deploy.append(file_path)

    print('\nThere are {} file(s) to upload:\n \33[96m'.format(len(files_to_deploy)))

    deploy_confirm = input('\33[0m\n> Continue? [Y/n] ').lower() in {'y', ''}
    if deploy_confirm:
        print('\nUploaded templates:\33[92m')
        for file in files_to_deploy:
            cmd = ['aws']
            arg_list = ['s3', 'cp', file, 's3://{}/email_templates/'.format(BUCKET_NAME), '--acl', 'public-read']
            p = Popen(cmd + arg_list, stdout=PIPE)
            p.wait()
            output, _ = p.communicate()
            print(output.decode('utf-8').rstrip().split()[-3])
        print('\33[0m')
        update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
    else:
        update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
        exit('Aborting. Hash file updated.')


def deploy_new_html_files():
    new_html_hashes, old_html_hashes = gen_html_hash_dicts(HTML_DIR, HTML_HASH_FILE)
    files_to_deploy = compare_hash_dicts(new_html_hashes, old_html_hashes)

    print('\nThere are {} file(s) to upload:\n \33[96m'.format(len(files_to_deploy)))

    for file in files_to_deploy:
        print(file)

    deploy_confirm = input('\33[0m\n> Continue? [Y/n] ').lower() in {'y', ''}
    if deploy_confirm:
        print('\nUploaded templates:\33[92m')
        for file in files_to_deploy:
            cmd = ['aws']
            arg_list = ['s3', 'cp', file, 's3://{}/email_templates/'.format(BUCKET_NAME), '--acl', 'public-read']
            p = Popen(cmd + arg_list, stdout=PIPE)
            p.wait()
            output, _ = p.communicate()
            print(output.decode('utf-8').rstrip().split()[-3])
        print('\33[0m')
        update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
    else:
        update_html_hash_file(HTML_DIR, HTML_HASH_FILE)
        exit('Aborting. Hash file updated.')


def compile_new_mjml_files(new, old):
    files_to_compile = compare_hash_dicts(new, old)
    print('Compiled files: \33[92m')
    for file_path in files_to_compile:
        directories = file_path.split('/')[:-1]
        file_name = file_path.split('/')[-1]

        template_name = file_name.replace('-header', '').replace('-highlight', '') \
            if directories[-1].lower() == 'components' else file_name

        cmd = ['yarn']
        arg_list = ['run', 'mjml', '{}/{}'.format(MJML_TEMPLATE_DIR, template_name), '-o', '{}/'.format(HTML_DIR)]

        p = Popen(cmd + arg_list, stdout=PIPE)
        p.wait()
        output, _ = p.communicate()
        print(output.decode('utf-8').rstrip().split()[5])
    print('\33[0m')
    update_mjml_hash_file(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, MJML_HASH_FILE)


def main(**kwargs):
    if 'force' in kwargs:
        deploy_all_html_files()
        exit(0)

    compiled_flag = deployed_flag = False
    new_mjml_hashes, old_mjml_hashes = gen_mjml_hash_dicts(MJML_TEMPLATE_DIR, MJML_COMPONENT_DIR, MJML_HASH_FILE)
    if not new_mjml_hashes == old_mjml_hashes:
        compile_new_mjml_files(new_mjml_hashes, old_mjml_hashes)
        compiled_flag = True

    new_html_hashes, old_html_hashes = gen_html_hash_dicts(HTML_DIR, HTML_HASH_FILE)
    if not new_html_hashes == old_html_hashes:
        deploy_new_html_files()
        deployed_flag = True

    if not (compiled_flag or deployed_flag):
        exit('-- Nothing to compile or deploy. 🤷️ --')


def user_help():
    author = 'Will Garside'
    description = "Compile and deploy MJML templates at './{}' to S3 bucket"\
        .format('/'.join(MJML_TEMPLATE_DIR.split('/')[-2:]))
    expected_args = {
        '--force': 'Upload all HTML files regardless of their status'
    }
    env_list = {
        'AWS_ACCESS_KEY_ID': 'XXX_S3_BUCKET_KEY_XXX',
        'AWS_SECRET_ACCESS_KEY': 'XXX_S3_SECRET_KEY_XXX',
        'AWS_DEFAULT_REGION': 'eu-west-2',
        'AWS_BUCKET_NAME': 'XXX_BUCKET_NAME_XXX',
    }

    return author, description, expected_args, env_list


if __name__ == "__main__":
    main()
