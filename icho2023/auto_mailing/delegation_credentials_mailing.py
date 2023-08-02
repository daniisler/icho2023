#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   delegation_credentials_mailing.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Sends out the credentials for each delegation to the mentors, observers and guests.
'''

import os
from secret import smtp_username, smtp_password, smtp_host, smtp_port
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(PROJECT_DIR, 'Delegations.xlsx')
csv_file_path = os.path.join(PROJECT_DIR, 'delegations_credentials.csv')

def send_email(sender_email, sender_password, recipient_email, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipient_email)  # Join multiple recipients with comma separator
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    print('EMAIL SENT TO:', message["To"])

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

def process_excel_file(excel_file, csv_file):
    # Read Excel file
    df_excel = pd.read_excel(excel_file, header=1)
    # Get the email columns from the Excel data
    email_columns = [col for col in df_excel.columns if "Email" in str(col)]
    # print(email_columns)
    # print(df_excel.head())
    # print(df_excel.columns)

    # Read CSV file
    df_csv = pd.read_csv(csv_file)
    # print(df_csv.head())
    # print(df_csv.columns)

    # Merge Excel and CSV data based on the 'ISO3' column
    df_merged = df_excel.merge(df_csv, left_on="ISO3", right_on="username")
    
    # Iterate over the merged data and send emails
    for row in df_merged.itertuples():
        iso3 = row.ISO3
        password = row.password
        recipient_emails = []
        for col in email_columns:
            # print(row[df_merged.columns.get_loc(col)+1])
            # Do not include the Email.1, 2, 3, 4 (STUDENTS) column
            if str(col) in ['Email.1', 'Email.2', 'Email.3', 'Email.4']:
                continue
            email = row[df_merged.columns.get_loc(col)+1]
            if not pd.isna(email) and "@" in email:
                recipient_emails.append(email)
        # print(recipient_emails)

        subject = "OlyExams Introduction 10.07.2023"
        # Construct the body of the email with added content
        body = f"Dear Mentors, Observers and Guests of the {iso3} Delegation\n\n"
        body += "As a followup on the 6th Circular sent out yesterday, please find your credentials for OlyExams below. They are valid from when the meeting (https://ethz.zoom.us/j/2345678901?pwd=TFRnS0Y3K2hyQkk2a3UyckQvZWNwdz09 , Passcode: IChO2023Ex) starts on Monday, 10.07.2023 at 11:00 UTC until Friday, 14.07.2023 at 23:59. You can already start translating the general instructions from the official exam which will be released during the event.\n\n"
        body += f"Username: {iso3}\n"
        body += f"Password: {password}\n\n"
        body += "Best regards,\nDaniel on behalf of the OlyExams Team\n\n"
        send_email(smtp_username, smtp_password, recipient_emails, subject, body)

if __name__ == "__main__":
    process_excel_file(excel_file_path, csv_file_path)
