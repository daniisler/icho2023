import os
from secret import smtp_username, smtp_password, smtp_host, smtp_port
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
from email.utils import formatdate
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
excel_file_path = os.path.join(PROJECT_DIR, 'Delegations.xlsx')
version = 'Final'
csv_tempdir = os.path.join(PROJECT_DIR, 'csv_tempdir')
os.makedirs(csv_tempdir, exist_ok=True)
df_pract = pd.read_csv(f'/home/daniel/Downloads/markingsPractical_{version}_filter_totals.csv')
df_theory = pd.read_csv(f'/home/daniel/Downloads/markingsTheory_{version}_filter_totals.csv')
merged_df = pd.merge(df_pract, df_theory, on='Student', how='outer')

def create_delegation_csv_results(delegation):
    # Merge the two DataFrames by the 'Student' column
    selected_rows = merged_df[merged_df['Student'].str[:3] == delegation]
    selected_cols = ['Student', 'Totals Practical (weighted%)', 'Totals Theory (weighted%)']
    selected_rows = selected_rows[selected_cols]
    # Add the total score
    selected_rows['Total (weighted%)'] = selected_rows['Totals Practical (weighted%)'] + selected_rows['Totals Theory (weighted%)']
    # Save the selected rows to a new CSV file
    selected_rows.to_csv(os.path.join(csv_tempdir, f'{delegation}_results.csv'), index=False)

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
        files = []
        iso3 = row.ISO3
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

        subject = "Your students results in IChO2023"
        # Construct the body of the email with added content
        body = f"Dear Mentors and Observers of the {iso3} Delegation\n\n"
        body += "We are happy to share your students final results with you. Please find attached a csv with:\n\n"
        body += "\t- Student code in first row\n"
        body += "\t- Achieved score in practical exam in second row\n"
        body += "\t- Achieved score in theory exam in third row\n"
        body += "\t- Achieved total score combined in fourth row\n\n"
        body += "Best regards on behalf of the Scientific Committee,\nDaniel\n\n"
        # body += "Sorry for the late arrival, there was a delay in the data processing."

        # Prepare the csv for task 2
        create_delegation_csv_results(iso3)
        files.append(os.path.join(csv_tempdir, f'{iso3}_results.csv'))
        send_email(smtp_username, smtp_password, recipient_emails, subject, body, files)

if __name__ == "__main__":
    process_excel_file(excel_file_path)
