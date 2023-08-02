#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   gen_delegations_answers_pdf.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Gets a list of the delegations that want printout of their students answer sheets and combines them into one pdf per delegation
'''

import numpy as np
import os
from PyPDF2 import PdfMerger
import time
import json
import csv
from cover_sheets import cover_sheet_with_text, coversheet_tempdir
from upload_google_drive import upload_files_googledrive

# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# Exam number and number of questions for the exam
exam_type='Practical' # 'Theory' or 'Practical'
if exam_type == 'Practical':
    num_questions = 4
elif exam_type == 'Theory':
    num_questions = 10
# Read the csv file with the delegations and num students in the columns
csv_path = os.path.join(PROJECT_DIR, 'RequestPrintedAnserSheets.csv')
# Where to save the combined answer sheets for the delegations
output_path = os.path.join(PROJECT_DIR, f'delegation_answersheets_{exam_type}')
os.makedirs(output_path, exist_ok=True)
# Path of the tracking json file from the scanned answer sheets
json_scanned_exams = os.path.join(PROJECT_DIR, f'downloaded_answer_sheets_{exam_type}.json')
# Path to scanned exams folder
scanned_exams_path = os.path.join(PROJECT_DIR, f'answer_sheets_scans_{exam_type}')


# Read the CSV file
def get_delegations_num_students():
    delegations_num_students = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            delegation = row['Delegation']
            num_students = int(row['Num_students'])
            # Check if the delegation wants printout and if the pdf has not been generated yet
            if row['Want_printout'] == '1' and not row['PDF_generated'] == '1':
                delegations_num_students.append((delegation, num_students))
    return delegations_num_students

# Tracking of which documents have been submitted for printing and could also be used for delegations print
def get_ready_sheets():
    if not os.path.exists(json_scanned_exams):
        with open(json_scanned_exams, 'w') as f:
            json.dump({}, f, indent=4)
    with open(json_scanned_exams, 'r') as f:
        ready_sheets = json.load(f)
    return ready_sheets

def update_csv(csv_path, delegation, mode):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    header = rows[0]
    delegation_index = header.index('Delegation')
    pdf_generated_index = header.index('PDF_generated')
    uploaded_index = header.index('Uploaded')

    for row in rows[1:]:
        if row[delegation_index] == delegation and mode == 'pdf_generated':
            row[pdf_generated_index] = '1'
            break  # Stop iterating if delegation is found
        if row[delegation_index] == delegation and mode == 'pdf_uploaded':
            row[uploaded_index] = '1'
            break

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

# Check with the content from the json file for which delegations we have all answer sheets ready
def check_delegations_ready(delegations_num_students, ready_sheets):
    ready_delegations = []
    for delegation, num_students in delegations_num_students:
        # Check if all students of the delegations had scans yet
        if all([f'{delegation}-{student_idx+1}' in ready_sheets for student_idx in range(num_students)]):
            print(delegation, num_students)
            # Check if all answer sheets are available been scanned
            if all([len(ready_sheets[f'{delegation}-{student_idx+1}'].keys()) == num_questions for student_idx in range(num_students)]):
                ready_delegations.append((delegation, num_students))
    return ready_delegations

# For all delegations that are ready to be printed, combine the pdfs
def combine_pdfs(ready_delegations):
    for delegation, num_students in ready_delegations:
        # Initialize the merger
        merger = PdfMerger()
        # Add all the pdfs to the merger
        cover_sheet_with_text(delegation)
        merger.append(os.path.join(coversheet_tempdir, f'cover_{delegation}.pdf'))
        for student_idx in range(num_students):
            # Sort it according to the number after T- in the value
            sorted_keys = sorted(ready_sheets[f'{delegation}-{student_idx+1}'].keys(), key=lambda x: int(x.split('-')[1]))
            for key in sorted_keys:
                merger.append(ready_sheets[f'{delegation}-{student_idx+1}'][key])
        # Write the merger to a new pdf
        merger.write(os.path.join(output_path, f'{delegation}.pdf'))
        # Write to the csv file that the pdf has been generated
        update_csv(csv_path, delegation, 'pdf_generated')
        merger.close()

if __name__ == '__main__':
    while True:
        print('Checking for delegation answer sheets to be printed')
        # Get the delegations and number of students from the csv file
        delegations_num_students = get_delegations_num_students()
        # Get the ready sheets from the json file
        ready_sheets = get_ready_sheets()
        # Check which delegations are ready to be printed
        ready_delegations = check_delegations_ready(delegations_num_students, ready_sheets)
        print(f'Found {len(ready_delegations)} delegations that are ready to be printed, leaving us with {len(delegations_num_students) - len(ready_delegations)} delegations that are not ready yet.')
        # Combine the pdfs for the delegations that are ready
        combine_pdfs(ready_delegations)
        print('Combined the pdfs for the delegations that are ready, uploading to the drive folder...')
        # Upload the pdfs to drive
        
        for delegation, num_students in ready_delegations:
            try:
                upload_files_googledrive([os.path.join(output_path, f'{delegation}.pdf')], exam_type)
                update_csv(csv_path, delegation, 'pdf_uploaded')
                # Wait for 10 min before checking again
                print(f'Successful upload for delegation {delegation}\n\n')
            except Exception as e:
                print(f'UPLOAD FAILED, CHECK MANUALLY FOR {delegation}:\n{e}')
        print('Sleeping for 10 min before checking again\n\n')
        time.sleep(600)