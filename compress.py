# https://developers.google.com/drive/api/quickstart/python
# https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html
# https://console.cloud.google.com/apis/credentials

from __future__ import print_function

import logging
import os.path
import sys
import tarfile

from os import makedirs
from os.path import exists
from pathlib import Path
from hurry.filesize import size, si
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

logging.basicConfig(stream=sys.stdout,
                    format="%(levelname)s %(asctime)s - %(message)s",
                    level=logging.INFO)

if not exists('tmp'):
    makedirs('tmp')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            q="(name contains 'sms' or name contains 'calls') and name contains 'xml' and not name contains 'tar.gz'",
            pageSize=1000,
            fields="nextPageToken, files(id, name, quotaBytesUsed, parents)").execute()
        items = sorted(results.get('files', []), key=lambda d: int(d['quotaBytesUsed']))

        if not items:
            print('No files found.')
            return
        for item in items:
            # ({1}) {2} {3}'.format(item['name'], item['id'], item['quotaBytesUsed'], item['parents']))
            filename_raw = str(item['name'])
            filename_friendly = filename_raw.split(".")[0]
            compressed_filename = f"{filename_friendly}.tar.gz"
            size_raw = int(item['quotaBytesUsed'])
            size_friendly = size(size_raw, system=si)

            logging.info(f"Downloading {filename_raw} ({size_friendly})...")
            with open(f"tmp/{filename_raw}", 'wb') as file:
                file.write(service.files().get_media(fileId=item['id']).execute())
            logging.info(f"Saved (local) {filename_raw}")

            logging.info(f"Deleting (remote) {filename_raw}")
            service.files().delete(fileId=item['id']).execute()

            logging.info(f"Compressing into {compressed_filename}")
            with tarfile.open(f"tmp/{compressed_filename}", "w:gz") as tar:
                tar.add(f"tmp/{filename_raw}")
            compressed_size_raw = os.path.getsize(f"tmp/{compressed_filename}")
            compressed_size_friendly = size(compressed_size_raw, system=si)

            percent = (float(compressed_size_raw) / float(size_raw))
            logging.info(f"Compressed {size_friendly} => {compressed_size_friendly} ({'{:.2%}'.format(percent)})")

            logging.info(f"Deleting local {filename_raw}")
            delete = Path(f"tmp/{filename_raw}")
            delete.unlink(missing_ok=True)

            file_metadata = {
                'name': f"{compressed_filename}",
                'mimeType': 'application/gzip',
                'parents': item['parents']
            }
            media = MediaFileUpload(f"tmp/{compressed_filename}",
                                    mimetype='application/gzip',
                                    resumable=True)
            logging.info(f"Uploading {compressed_filename} ({compressed_size_friendly})...")

            service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            logging.info(f"Deleting (local) {compressed_filename}")
            delete = Path(f"tmp/{compressed_filename}")
            delete.unlink(missing_ok=True)

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
