from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from secret import practical_folder_id, theoretical_folder_id
   
  
# Below code does the authentication
# part of the code
gauth = GoogleAuth()
  
# Creates local webserver and auto
# handles authentication.
gauth.LocalWebserverAuth()       
drive = GoogleDrive(gauth)
   
def upload_files_googledrive(upload_file_list, exam_type):
    for upload_file in upload_file_list:
        folder_id = practical_folder_id if exam_type == 'Practical' else theoretical_folder_id
        gfile = drive.CreateFile({'parents': [{f'id': folder_id}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload() # Upload the file.
        gfile = None