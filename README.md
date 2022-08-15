# sms-backup-compress
Compress Android SMS, MMS and call logs created by SMS Backup

## Description
SMS Backup & Restore is an excellent tool to back up text messages from your phone to Google Drive. Unfortunately drive space will get eaten up by progressively larger and larger backup files. This tool was written for personal use to reclaim drive space by compressing and replacing the uncompressed files on Google Drive.

## Prerequisites
Read:
- https://developers.google.com/drive/api/quickstart/python
- https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html
- Download credentials.json from https://console.cloud.google.com/apis/credentials
```
pipenv install
```

## Usage
```
pipenv run python3 compress.py
```

## Links
- https://www.synctech.com.au/sms-backup-restore/
- https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore

## Troubleshooting
- [File not found error for credentials.json](https://developers.google.com/drive/api/quickstart/python#file_not_found_error_for_credentialsjson)
- For cli development update credentials.json to `"redirect_uris": []`