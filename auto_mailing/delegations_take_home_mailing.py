import os
from secret import smtp_username, smtp_password, smtp_host, smtp_port
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
from email.utils import formatdate
import pandas as pd
import zipfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from delegations_take_home_drive import create_folder, create_share_link, upload_files


# Authenticate with Google Drive using pydrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

parent_folder_id='1Nygosakv5zFzzcBboaTyTB6N9MX55yOO'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(PROJECT_DIR, 'Delegations.xlsx')
version = 'Final'
csv_tempdir = os.path.join(PROJECT_DIR, 'csv_tempdir')
os.makedirs(csv_tempdir, exist_ok=True)
final_version_theory = os.path.join(PROJECT_DIR, f'final_version_exams_Theory')
final_version_practical = os.path.join(PROJECT_DIR, f'final_version_exams_Practical')
delegation_zips_dir = os.path.join(PROJECT_DIR, 'delegation_takehome_zips')
os.makedirs(delegation_zips_dir, exist_ok=True)

def prepare_delegation_folder(delegation):
    # Create a folder for the delegation
    delegation_folder_id = create_folder(drive, delegation, parent_folder_id=parent_folder_id)
    create_share_link(drive, delegation_folder_id)
    # Upload files to the folder.
    file_paths = create_delegation_takehome_zip(delegation)
    upload_files(drive, delegation_folder_id, file_paths)
    link = f'https://drive.google.com/folderview?id={delegation_folder_id}'
    return link

def create_delegation_takehome_zip(delegation):
    # Create a zip file with the take home rescans for the delegation
    generated_files = []
    for exam_type in ['Theory', 'Practical']:
        # if exam_type == 'Theory':
        #     exam_dir = final_version_theory
        # elif exam_type == 'Practical':
        #     exam_dir = final_version_practical
        # for file in os.listdir(os.path.join(exam_dir, delegation)):
        #     generated_files.append(os.path.join(exam_dir, delegation, file))
        zip_file = os.path.join(delegation_zips_dir, f'{delegation}_{exam_type}.zip')
        with zipfile.ZipFile(zip_file, 'w') as zipObj:
            if exam_type == 'Theory':
                exam_dir = final_version_theory
            elif exam_type == 'Practical':
                exam_dir = final_version_practical
            for file in os.listdir(os.path.join(exam_dir, delegation)):
                zipObj.write(os.path.join(exam_dir, delegation, file), file)
        generated_files.append(zip_file)
    return generated_files

def send_email(sender_email, sender_password, recipient_email, subject, body, files=None):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipient_email)  # Join multiple recipients with comma separator
    # Add myself in BCC
    recipient_email.append(sender_email)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    for f in files or []:
        with open(f, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        message.attach(part)

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

    print('EMAIL SENT TO:', message["To"])

def process_excel_file(excel_file):
    # Read Excel file
    df_excel = pd.read_excel(excel_file, header=1)
    # Get the email columns from the Excel data
    email_columns = [col for col in df_excel.columns if "Email" in str(col)]
    
    # Iterate over the merged data and send emails
    First = True
    for row in df_excel.itertuples():
        if First:
            First = False
            continue
        iso3 = row.ISO3
        password, sharing_link = prepare_delegation_folder(iso3)
        recipient_emails = []
        for col in email_columns:
            # print(row[df_excel.columns.get_loc(col)+1])
            # Do not include the Email.1, 2, 3, 4 (STUDENTS) column
            if str(col) in ['Email.1', 'Email.2', 'Email.3', 'Email.4']:
                continue
            email = row[df_excel.columns.get_loc(col)+1]
            if not pd.isna(email) and "@" in email:
                recipient_emails.append(email)
        # print(recipient_emails)

        subject = "IChO2023 - Take home corrected exams"
        # Construct the body of the email with added content
        body = f"Dear Mentors and Observers of the {iso3} Delegation\n\n"
        body += "We hope this email finds you well and that you have recovered from the busy week of the IChO2023.\n\n"
        body += "We have finally managed to collate your students corrected work on their exams into pdfs. Please find them shared in a google drive folder using the link:\n"
        body += f"\t- Link: {sharing_link}\n"
        body += "Please share them with your students and keep them in your archive should you ever want to revise them.\nNote that for P-1, P-2, T-9 the corrections were done directly in oly-exams and therefore the original scans were added here.\nFurther we have added the official solutions, that are also published on the official website and you could also directly share with your students.\n\n"
        body += "Best regards on behalf of the Scientific Committee,\nDaniel\n\n"
        # body += "Sorry for the late arrival, there was a delay in the data processing."

        # Prepare the takehome zip files
        send_email(smtp_username, smtp_password, recipient_emails, subject, body)
        break

if __name__ == "__main__":
    process_excel_file(excel_file_path)
