from datetime import datetime
import json
import logging
import os
import subprocess
from typing import Optional
import urllib.request

import boto3
from botocore.exceptions import ClientError


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get the s3 client
s3 = boto3.client('s3')

local_tmp_folder = '/tmp'
bucket = os.environ['BUCKET_NAME']
project_name = os.environ['PROJECT_NAME']
try:
    default_bucket_folder = os.environ['DEFAULT_BUCKET_FOLDER']
except KeyError:
    default_bucket_folder = 'tmp/'

def download_s3_file(bucket: str, file_key: str) -> str:
    """Downloads a file from s3 to `/tmp/[File Key]`.

    Args:
        bucket (str): Name of the bucket where the file lives.
        file_key (str): The file key of the file in the bucket.

    Returns:
        The local file name as a string.
    """
    local_filename = os.path.basename(file_key)
    local_full_filename = f'{local_tmp_folder}/{local_filename}'
    s3.download_file(Bucket=bucket, Key=file_key, Filename=local_full_filename)
    logger.info('Downloaded HTML file to %s' % local_full_filename)

    return local_full_filename


def upload_file_to_s3(bucket: str, bucket_key: str, local_filename:str) -> Optional[str]:
    """Uploads the generated PDF to s3.

    Args:
        bucket (str): Name of the s3 bucket to upload the PDF to.
        filename (str): Location of the file to upload to s3.

    Returns:
        The file key of the file in s3 if the upload was successful.
        If the upload failed, then `None` will be returned.
    """
    try:
        s3.upload_file(Filename=local_filename, Bucket=bucket, Key=bucket_key)
        logger.info('Successfully uploaded the PDF to %s as %s'
                    % (bucket, bucket_key))
    except ClientError as e:
        logger.error('Failed to upload file to s3: %s' % (bucket_key))
        logger.error(e)

    return bucket_key

def lambda_handler(event, context):
    logger.info(event)

    # TODO: secure the string by regex validation (regex pattern from env)
    try:
        url = event['url']
    except KeyError:
        url = None

    try:
        file_key = event['file_key']
    except KeyError:
        file_key = None

    try:
        html_string = event['html_string']
    except KeyError:
        html_string = None

    try:
        header_html_string = event['header_html_string']
    except KeyError:
        header_html_string = None

    try:
        footer_html_string = event['footer_html_string']
    except KeyError:
        footer_html_string = None

    if file_key is None and html_string is None and url is None:
        error_message = (
            'One of "file_key", "html_string" or "url" must be present.'
        )
        logger.error(error_message)
        return {
            'status': 400,
            'body': json.dumps(error_message),
        }

    try:
        target_bucket_folder = event['folder']
    except KeyError:
        target_bucket_folder = default_bucket_folder

    # Now we can check for the option wkhtmltopdf_options and map them to values
    # Again, part of our assumptions are that these are valid
    wkhtmltopdf_options = {}
    if 'wkhtmltopdf_options' in event:
        # Margin is <top> <right> <bottom> <left>
        if 'margin' in event['wkhtmltopdf_options']:
            margins = event['wkhtmltopdf_options']['margin'].split(' ')
            if len(margins) == 4:
                wkhtmltopdf_options['margin-top'] = margins[0]
                wkhtmltopdf_options['margin-right'] = margins[1]
                wkhtmltopdf_options['margin-bottom'] = margins[2]
                wkhtmltopdf_options['margin-left'] = margins[3]

        if 'orientation' in event['wkhtmltopdf_options']:
            wkhtmltopdf_options['orientation'] = 'portrait' \
                if event['wkhtmltopdf_options']['orientation'].lower() not in ['portrait', 'landscape'] \
                else event['wkhtmltopdf_options']['orientation'].lower()

        if 'title' in event['wkhtmltopdf_options']:
            wkhtmltopdf_options['title'] = event['wkhtmltopdf_options']['title']

    # If we got a file_key in the request, let's download our file
    # If not, we'll write the HTML string to a file
    if file_key is not None:
        local_filename = download_s3_file(bucket, file_key)
        local_filename_pdf = local_filename.replace('.html', '.pdf')
    elif html_string is not None:
        timestamp = str(datetime.now()).replace('.', '').replace(' ', '_')
        local_filename = f'{local_tmp_folder}/{timestamp}-html-to-pdf.html'
        local_filename_pdf = local_filename.replace('.html', '.pdf')

        # Delete any existing files with that name
        try:
            os.unlink(local_filename)
        except FileNotFoundError:
            pass

        with open(local_filename, 'w') as f:
            f.write(html_string)
    else:
        local_filename_pdf = f'{local_tmp_folder}/url.pdf'

    logger.info('Preparing to run the command')

    # Now we can create our command string to execute and upload the result to s3
    command = 'wkhtmltopdf  --load-error-handling ignore'  # ignore unnecessary errors

    # if header/footer required:
    if header_html_string is not None:
        tmp_header_file_path = f'{local_tmp_folder}/header.html'
        with open(tmp_header_file_path, 'w') as file:
            file.write(header_html_string)
        command += f' --header-html {tmp_header_file_path}'

    if footer_html_string is not None:
        tmp_footer_file_path = f'{local_tmp_folder}/footer.html'
        with open(tmp_footer_file_path, 'w') as file:
            file.write(footer_html_string)
        command += f' --footer-html {tmp_footer_file_path}'

    for key, value in wkhtmltopdf_options.items():
        if key == 'title':
            value = f'"{value}"'
        command += ' --{0} {1}'.format(key, value)
    if url is not None:
        command += ' {0} {1}'.format(url, local_filename_pdf)
    else:
        command += ' {0} {1}'.format(local_filename, local_filename_pdf)

    # Important! Remember, we said that we are assuming we're accepting valid HTML
    # this should always be checked to avoid allowing any string to be executed
    # from this command. The reason we use shell=True here is because our title
    # can be multiple words.
    logger.info(f'Running the command: {command}')
    subprocess.run(command, shell=True)
    logger.info('Successfully generated the PDF.')
    filename_pdf = os.path.basename(local_filename_pdf)
    file_size = os.path.getsize(local_filename_pdf)
    file_key = upload_file_to_s3(bucket, f'{project_name}/{target_bucket_folder}{filename_pdf}', local_filename_pdf)

    if file_key is None:
        error_message = (
            'Failed to generate PDF from the given HTML file.'
            ' Please check to make sure the file is valid HTML.'
        )
        logger.error(error_message)
        return {
            'status': 400,
            'body': json.dumps(error_message),
        }

    return {
        'status': 201,
        'file_key': file_key,
        'file_size': file_size,
    }
