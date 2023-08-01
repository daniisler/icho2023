import requests
import os
from secret import telegram_token, telegram_chat_id, scan_api_key
from PyPDF2 import PdfMerger
import time
import json
import shutil
import uuid
from cover_sheets import cover_sheet_with_text, coversheet_tempdir
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, mm

# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

debug = 1
# Index of the operated exam
exam_type='Theory' # 'Theory' or 'Practical
if exam_type == 'Theory':
    # How many students task files should be combined into 1 pdf, one entry per task
    N_tasks = [23, 19, 19, 28, 28, 28, 3, 28, 22, 6]
    num_questions = 10
    exam_str = 'T'
    no_reprint_questions = [2, 9]
elif exam_type == 'Practical':
    # How many students task files should be combined into 1 pdf
    N_tasks = [5, 30, 20, 100]
    num_questions = 4
    exam_str = 'P'
    no_reprint_questions = [1,4]
# Temporary directory for the single pdfs from OlyExams
pdfs_dir_local = os.path.join(PROJECT_DIR, f'answer_sheets_scans_{exam_type}')
os.makedirs(pdfs_dir_local, exist_ok=True)
# Tracking of which documents have been printed
json_traking_before_ftp = os.path.join(PROJECT_DIR, f'printed_answer_sheets_{exam_type}_before_ftp.json')
json_tracking_path = os.path.join(PROJECT_DIR, f'printed_answer_sheets_{exam_type}.json')
if not os.path.exists(json_tracking_path):
    with open(json_tracking_path, 'w') as f:
        json.dump({}, f, indent=4)
with open(json_tracking_path, 'r') as f:
    printed_dict = json.load(f)
# Same for documents which have thrown an error
json_errors_traking = os.path.join(PROJECT_DIR, f'reprint_as_errors_{exam_type}.json')
if not os.path.exists(json_errors_traking):
    with open(json_errors_traking, 'w') as f:
        json.dump({}, f, indent=4)
with open(json_errors_traking, 'r') as f:
    errors_dict = json.load(f)
# Tracking of which (successful) documents have been downloaded
download_tracking_path = os.path.join(PROJECT_DIR, f'downloaded_answer_sheets_{exam_type}.json')
if not os.path.exists(os.path.join(PROJECT_DIR, download_tracking_path)):
    with open(os.path.join(PROJECT_DIR, download_tracking_path), 'w') as f:
        json.dump({}, f, indent=4)
with open(os.path.join(PROJECT_DIR, download_tracking_path), 'r') as f:
    dowloaded_dict = json.load(f)
# Local directory for the combined pdfs
output_dir = os.path.join(PROJECT_DIR, f'combined_ans_{exam_type}')
os.makedirs(output_dir, exist_ok=True)

# API credentials
base_domain = 'icho2023.oly-exams.org'   #'icho2023.oly-exams.org'
api_url = f'https://{base_domain}/api/exam/documents/'

# FTP Credentials; A connection must be setup manually, but that shouldn't be a problem
connection_path = f'/run/user/1000/gvfs/sftp:host={base_domain}'
connection_appendix = ',user=ipho-files/media'

api_headers = {
    'accept': 'application/json',
    'ApiKey': scan_api_key
}

# Temporary directory for the cover sheets
coversheet_tempdir = os.path.join(PROJECT_DIR, 'coversheet_tempdir')
os.makedirs(coversheet_tempdir, exist_ok=True)
# Position for the text on the cover sheet
# (x, y) position of the rectangle's upper-left corner in mm
position_covertext = (15*mm, 40*mm)
# Define rectangle size in points
width = 91*mm
height = 32*mm

# Send a message to the telegram chat that an envelope needs to be rescanned
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text={message}"
    print(requests.get(url).json())

# Get an updated list of the scan status
def get_successful_scans():
    api_url = f'https://{base_domain}/api/exam/documents/'
    response = requests.get(api_url, headers=api_headers)

    # Get all entries where scan_status is 'S'
    successful_scans = [entry for entry in response.json() if entry['scan_status'] == 'S']
    problematic_scans = [entry for entry in response.json() if entry['scan_status'] == 'M' or entry['scan_status'] == 'W']
    for scan in problematic_scans:
        if not scan['scan_file'] in errors_dict.keys():
            # Send a telegram message that the scan has to be redone
            send_telegram_message(f'Status {scan["scan_status"]} received for {scan["participant"]} at {str(datetime.now())}, please rescan!')
            errors_dict[scan['scan_file']] = scan['scan_status']+' - '+str(datetime.now())
    json.dump(errors_dict, open(json_errors_traking, 'w'), indent=4)

    return [(entry['participant'], entry['scan_file'], entry['barcode_base']) for entry in successful_scans]

def prepare_print_files(ready_scans):
    to_print_list = []
    # Loop through all successful scans
    for participant, scan_file, barcode_base in ready_scans:
        # Skip if it's not from the correct exam type
        if exam_type == 'Theory' and ' T-' not in barcode_base or exam_type == 'Practical' and ' P-' not in barcode_base:
            # if debug: # print(f'Skipping {barcode_base} because it is not a {exam_type} exam')
            continue
        # Define the local directory for the participant
        pdfs_dir_local_delegation = os.path.join(pdfs_dir_local, participant)
        os.makedirs(pdfs_dir_local_delegation, exist_ok=True)
        local_filepath = os.path.join(pdfs_dir_local_delegation, scan_file.split('/')[-1])
        # Check if something for the participant has already been printed
        if participant in printed_dict.keys():
            # Check if the file has already been printed
            if f"T-{barcode_base.split(' T-')[1]}".strip() in printed_dict[participant].keys():
                print(f'{barcode_base} already been printed')
                # If the file has already been printed, skip it
                continue
            # if barcode_base[-3:].strip() in printed_dict[participant].keys():
            #     print(f'{barcode_base} already been printed')
            #     # If the file has already been printed, skip it
            #     continue
        if participant in dowloaded_dict.keys():
            if f"T-{barcode_base.split(' T-')[1]}".strip() in dowloaded_dict[participant].keys():
                # If the file has already been downloaded, don't download it again, but add to the list of files to print
                to_print_list.append((local_filepath, barcode_base))
                if debug: print(f'{barcode_base} already been dowloaded, but not printed yet')
                continue
            
        # If the file has not been printed yet, get it from the ftp
        ftp_filepath = f'{connection_path}{connection_appendix}{scan_file.split("oly-exams.org")[-1]}'
        shutil.copy(ftp_filepath, local_filepath)
        # Add an entry to the downloaded dict
        if participant in dowloaded_dict.keys():
            dowloaded_dict[participant][f"T-{barcode_base.split(' T-')[1]}".strip()] = local_filepath
        else:
            dowloaded_dict[participant] = {f"T-{barcode_base.split(' T-')[1]}".strip(): local_filepath}
        # Add the file to the list of files to be printed
        to_print_list.append((local_filepath, barcode_base))
        if debug: print(f'Downloaded {barcode_base} to the list of files to be printed')
    return to_print_list

def gen_coversheet(task_num, student_list, coverpath):
    c = canvas.Canvas(coverpath, pagesize=A4)
    c.setFont("Helvetica", 60)
    x, y = position_covertext
    # Calculate the y-coordinate from the top of the page
    page_height = A4[1]
    y_top = page_height - y
    # Draw the rectangle
    c.rect(x, y_top - height, width, height)
    # Add text inside the rectangle
    text_x = x + 5
    text_y = y_top - height + 5
    c.drawString(text_x, text_y, f'Task {task_num}')
    # Add the list of students who's exam is contained in the pdf
    c.setFont("Helvetica", 14)
    c.drawString(30, A4[1]/2 + 200, 'Scans of answers of the students:')
    for i in range(len(student_list)):
        c.drawString(50, A4[1]/2 + 200 - 20*(i+1), student_list[i])
    c.save()

def gen_merged_pdfs(to_print_list):
    generated_files = []
    for question_no in range(1, num_questions+1):
        if debug: print(f'Checking if enough available for question {question_no}')
        # Generate the cover sheet of not yet existing
        covertext = f'Task {question_no}'
        if question_no in no_reprint_questions:
            print(f'Skipping question {question_no} because it is not to be reprinted')
            continue
        # Tasks to print that belong to the question question_no
        # task_splitter = ' P-' if exam_type=='Practical' else ' T-'
        # if debug: print(f'List to print: {to_print_list}')
        # for i in range(len(to_print_list)):
        #     if len(to_print_list[i]) != 2:
        #         print(to_print_list[i])

        tasks_to_print = [(task, barcode_base) for (task, barcode_base) in to_print_list if int(barcode_base.split(f' {exam_str}-')[1]) == question_no]
        # if debug: print(f'Tasks to print: {tasks_to_print}')
        # Combine the tasks into one pdf in batches of N_tasks
        num_reprint_tasks = len(tasks_to_print)
        batch_start = 0
        while N_tasks[question_no-1] <= num_reprint_tasks-batch_start:
            print(f'{num_reprint_tasks} is more than {N_tasks[question_no-1]} tasks to print for question {question_no}. Creating batch...')
            uuid_batch = uuid.uuid4()
            output_path = os.path.join(output_dir, f'reprint_ans_q_{question_no}_{uuid_batch}.pdf')
            merger = PdfMerger()
            coverpath = os.path.join(coversheet_tempdir, f'cover_{covertext}_{uuid_batch}.pdf')
            gen_coversheet(question_no, [barcode_base for (task, barcode_base) in tasks_to_print[batch_start:batch_start+N_tasks[question_no-1]]], coverpath)
            merger.append(coverpath)
            # Loop through all question question_no and add them to the merger
            for (task, barcode_base) in tasks_to_print[batch_start:batch_start+N_tasks[question_no-1]]:
                task_pdf = os.path.join(pdfs_dir_local, task)
                merger.append(task_pdf)
                if not barcode_base.split(' ')[0] in printed_dict.keys():
                    printed_dict[barcode_base.split(' ')[0]] = {barcode_base.split(' ')[1]: output_path}
                else:
                    printed_dict[barcode_base.split(' ')[0]][barcode_base.split(' ')[1]] = output_path
            # Move on to the next batch
            batch_start += N_tasks[question_no-1]
            # First save the output file locally
            merger.write(output_path)
            merger.close()
            with open(json_traking_before_ftp, 'w') as of:
                json.dump(printed_dict, of, indent=4)
            generated_files.append(output_path)
        else:
            if debug: print(f'Less than {N_tasks[question_no-1]} tasks to print for question {question_no}. Waiting for more')
            
    return generated_files


# Transfer the files to the p+p print folder (ftp from olyexams)
def transfer_files_to_print(generated_files):
    if debug: print('Copying the files to OlyExams folder')
    for file in generated_files:
        print(f'Copying {file} to OlyExams folder')
        file_name = os.path.basename(file)
        # shutil.copy(file, os.path.join(f'{connection_path},user=ipho-files/media/eth-print-docs/', file_name))
    if debug: print('Finished copying to ftp eth print folder')
    # Write to the tracking sheet that the files have been successfully transferred 
    with open(json_tracking_path, 'w') as of:
        json.dump(printed_dict, of, indent=4)

if __name__ == '__main__':
    while True:
        # Get the list of successful scans
        print('Getting the list of successful scans')
        ready_scans = get_successful_scans()
        # Find out which files are ready to be printed
        print('Getting the files to be reprinted from the ftp')
        to_print_list = prepare_print_files(ready_scans)
        with open(download_tracking_path, 'w') as of:
            json.dump(dowloaded_dict, of, indent=4)
        # Generate the merged pdfs
        print('Checking if merged pdfs should be generated')
        generated_files = gen_merged_pdfs(to_print_list)
        # Transfer the files to the print folder
        transfer_files_to_print(generated_files)
        print(f'We have now downloaded {len(dowloaded_dict.keys())} successful participants downloads')
        for participant in dowloaded_dict.keys():
            if len(dowloaded_dict[participant].keys()) != num_questions:
                print(f'\nWARNING: Participant {participant} has only downloaded {len(dowloaded_dict[participant].keys())} instead of the expected {num_questions} files\n')
        print(f'Left for printing: {348*num_questions-sum([len(printed_dict[participant].keys()) for participant in printed_dict.keys()])} ans_sheets:')
        for question_no in range(num_questions):
            if question_no+1 in no_reprint_questions:
                continue
            print(f'\tQuestion {question_no+1}: {348-len([participant for participant in printed_dict.keys() if exam_str+"-"+str(question_no+1) in printed_dict[participant].keys()])} participants left to print.')
        # Sleep for 3 minutes
        print('Sleeping for 5 minutes')
        time.sleep(300)
