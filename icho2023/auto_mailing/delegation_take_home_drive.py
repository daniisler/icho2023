#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   delegations_take_home_drive.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Creates a google drive folder for each delegation and uploads the take-home exam files.
'''

import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def create_folder(drive, folder_name, parent_folder_id=None):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        folder_metadata['parents'] = [{'id': parent_folder_id}]

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']

def create_share_link(drive, folder_id):
    # Add the new permission with the custom link
    folder = drive.CreateFile({'id': folder_id})
    folder.InsertPermission({
        'type': 'anyone',
        'value': '',
        'role': 'reader',
        'withLink': False
    })
    folder.Upload()

def upload_files(drive, folder_id, file_paths):
    for file_path in file_paths:
        file = drive.CreateFile({
            'title': os.path.basename(file_path),
            'parents': [{'id': folder_id}]
        })
        file.SetContentFile(file_path)
        file.Upload()

def main():
    # Authenticate with Google Drive using pydrive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Create a folder and get its ID.
    folder_name = 'TEST_FOLDER'
    folder_id = create_folder(drive, folder_name, parent_folder_id='1Nygosakv5zFzzcBboaTyTB6N9MX55yOO')

    create_share_link(drive, folder_id)

    # Upload files to the folder.
    file_paths = ['/home/daniel/Documents/SwissChO/IChO2023/Event/PythonScripts/coversheets_glassware_chem.pdf']
    upload_files(drive, folder_id, file_paths)

    # Print the link and the password.
    link = f'https://drive.google.com/folderview?id={folder_id}'
    print(f'Shared link: {link}')

if __name__ == '__main__':
    main()
