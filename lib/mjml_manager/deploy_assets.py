from subprocess import Popen, PIPE
from pathlib import Path
from enum import Enum
from .helper.constants import ASSET_DIR, BUCKET_NAME


class ImageType(Enum):
    """An Enum class to add set image file types"""
    PNG = '.png'
    JPG = '.jpg'
    JPEG = '.jpeg'


def deploy_files_of_type(file_type, subdir):
    path_list = Path('{}/{}'.format(ASSET_DIR, subdir)).glob('**/*{}'.format(file_type))

    for file in path_list:
        file = str(file)
        cmd = ['aws']
        arg_list = ['s3', 'cp', file, r's3://{}/assets/{}/'.format(BUCKET_NAME, subdir), '--acl', 'public-read']

        p = Popen(cmd + arg_list, stdout=PIPE)
        p.wait()
        output, _ = p.communicate()
        print(output.decode('utf-8').rstrip().split()[-3])


def main(**kwargs):
    if not BUCKET_NAME:
        exit('The S3 bucket name must be provided in an envfile. See the help for this utility for more information.\n')

    deploy = True \
        if 'confirm' in kwargs \
        else input("This will overwrite all assets on the bucket '{}'. Continue? [Y/n] ".format(BUCKET_NAME)).lower() in {'y', ''}

    if deploy:
        print('\nUploaded files:\33[92m')
        for image_type in ImageType:
            deploy_files_of_type(image_type.value, 'images')
        print('\33[0m')


def user_help():
    author = 'Will Garside'
    description = "Deploy assets at './{}' to S3 bucket".format('/'.join(ASSET_DIR.split('/')[-2:]))
    expected_args = {
        '--confirm': 'Skip confirmation message at start of utility'
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
