from subprocess import call


def main():
    print('Updating cfl-utils...')
    cmd = ['npm']
    arg_list = ['i', '-g', '@chetwoodfinancial/cfl-utils@latest']
    call(cmd + arg_list)
    print(' \U0001F44D\n')


def user_help():
    author = ''
    description = 'Update the cfl-utils package'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list
