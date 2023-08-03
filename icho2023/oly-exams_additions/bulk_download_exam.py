#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   bulk_download_exam.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Logs into the oly-exams website and compiles and downloads all the exam question for a given exam type. Before you need to specify the quesions id's in the problem_id_array variable and give recent cookie parameters in the secret.py file.
'''

import requests
import os
import time
from secret import csrftoken, sessionid
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger, PdfReader, PdfWriter


# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.join(PROJECT_DIR, 'exam_pdfs')
os.makedirs(tmp_dir, exist_ok=True)
os.makedirs(os.path.join(PROJECT_DIR, 'merged_exam'), exist_ok=True)
debug=1

download_latest_versions = True
build_exam = True
exam_type = 'Theory' # 'Practical' or 'Theory'
max_version_general_inst = []
general_inst_files = []
if exam_type == 'Practical':
    # For practical problems (question id, answer id, solution id, question number)
    problem_id_array = [(6,9,7,1), #OC problem (P1)
                        (11,14,12,2), #Titration tango (P2)
                        (18,21,16,3) #Beauty in simplicity (P3)
                        ] 
    general_inst_id = [2,3]
if exam_type == 'Theory':
    # For theory problems
    problem_id_array=[(4,8,5,1),(13,15,10,2),(17,20,19,3),(22,25,23,4), (26,28,27,5), (30,31,29,6), (33,34,32,7), (35,37,36,8), (39,40,38,9), (41,43,42,10)]
    general_inst_id = [1]

base_domain = 'icho2023.oly-exams.org'

# Set the necessary headers for qml export
download_headers = {
    'Host': base_domain,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, /; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cookie': f'csrftoken={csrftoken}; sessionid={sessionid}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'Sec-GPC': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}


# Download the pdf export from a problem
def download_pdf(url, filename):
    response = requests.get(url, headers=download_headers)
    if debug: print(response.status_code)
    if debug: print(response.url)
    if debug: print("Redirected to url: ", f'https://{base_domain}{response.url.split("next=")[1]}')
    time.sleep(5)
    response_redir = requests.get(f'https://{base_domain}{response.url.split("next=")[1]}', headers=download_headers)

    # Check if the file contains the pdf header
    while response_redir.content[:4] != b'%PDF':
        print(f'Retrying to download file {filename}... from {response_redir}')
        time.sleep(5)
        response_redir = requests.get(f'https://{base_domain}{response.url.split("next=")[1]}', headers=download_headers)

    # Check if the request was successful
    if response_redir.status_code == 200:
        # Specify the path where you want to save the downloaded file
        file_path = os.path.join(tmp_dir, filename)

        # Save the file
        with open(file_path, 'wb') as file:
            file.write(response_redir.content)
        
        if debug: print(f'File downloaded successfully from {url} to {file_path}')
    else:
        print(f'Could not find version {filename.split("_")[1]} for question {filename.split("_")[0]}')
    
    # Also download the general instructions

    
    return response_redir.status_code

def add_latest_versions(problem_id_array):
    links = []
    problem_id_array_with_versions = []
    for i in range(10):
        print(f'Getting https://{base_domain}/exam/admin/?exam_id={i}')
        # Download the source of the exam management page
        response = requests.get(f'https://{base_domain}/exam/admin/?exam_id={i}', headers=download_headers)
        # Parse the html
        soup = BeautifulSoup(response.text, 'html.parser')
         # Find all hyperlinks
        links += soup.find_all('a')
    # print([link for link in links])
    # if debug: print([link.get('href') for link in links])
    for id_quadrupel in problem_id_array:
        for (type, id) in enumerate(id_quadrupel[:3]):
            # Find all links with the form '/exam/pdf/question/{problem_id}/lang/1/v{version_num}'
            problem_links = [link for link in links if link.get('href') and f'/exam/pdf/question/{id}/lang/1/v' in link.get('href')]
            # Find the maximum version number
            try:
                max_version = max([int(link.get('href').split('v')[1].replace('"', "").replace("\\", "")) for link in problem_links])
                # Add an elemment to the problem_id_array with the maximum version number
                problem_id_array_with_versions.append((id, max_version, type, id_quadrupel[3]))
            except Exception as e:
                print(f'Could not find any versions for problem {id}: {e}')
                if str(e) == 'max() arg is an empty sequence':
                    # print("Maybe you are not logged in anymore?")
                    raise Exception("Not logged in anymore")
    # Also find the latest version of the general instructions
    for id in general_inst_id:
        # Find all links with the form '/exam/pdf/question/{problem_id}/lang/1/v{version_num}'
        problem_links = [link for link in links if link.get('href') and f'/exam/pdf/question/{id}/lang/1/v' in link.get('href')]
        # Find the maximum version number
        try:
            max_version = max([int(link.get('href').split('v')[1].replace('"', "").replace("\\", "")) for link in problem_links])
            max_version_general_inst.append(max_version)
        except Exception as e:
            print(f'Could not find any versions for general inst {id}: {e}')
            if str(e) == 'max() arg is an empty sequence':
                print("Maybe you are not logged in anymore?")
                raise Exception("Not logged in anymore")

    return problem_id_array_with_versions

def merge_pdfs(filenames, output_filename):
    writer = PdfWriter()
    
    for filename in filenames:
        reader = PdfReader(filename)
        for page in range(len(reader.pages)):
            writer.add_page(reader.pages[page])
    
    with open(output_filename, 'wb') as output_file:
        writer.write(output_file)


def build_exam_file(question_nums, general_inst_files):
    pdf_list = general_inst_files.copy()
    for question_num in question_nums:
        pdf_list += [f'{tmp_dir}/{exam_type}_Q{question_num}.pdf', f'{tmp_dir}/{exam_type}_A{question_num}.pdf']
    merge_pdfs(pdf_list, f'{PROJECT_DIR}/merged_exam/{exam_type}Exam_v{len([exam for exam in os.listdir(f"{PROJECT_DIR}/merged_exam") if f"{exam_type}Exam_v" in exam])}.pdf')
        
def build_solutions(question_nums, general_inst_files):  
    pdf_list = general_inst_files.copy()
    for question_num in question_nums:
        pdf_list.append(f'{tmp_dir}/{exam_type}_S{question_num}.pdf')
    print(pdf_list)
    merge_pdfs(pdf_list, f'{PROJECT_DIR}/merged_exam/{exam_type}Solutions_v{len([exam for exam in os.listdir(f"{PROJECT_DIR}/merged_exam") if exam_type+"Solutions_v" in exam])}.pdf')



# Download the latest version of each exam
if download_latest_versions:
    id_array_with_versions = add_latest_versions(problem_id_array)
    for (id, max_version, problem_type, question_num) in id_array_with_versions:
        if debug: print(f'Downloading latest version {max_version} of problem {id}')
        problem_type_str = 'Q' if problem_type == 0 else 'A' if problem_type == 1 else 'S'
        download_pdf(f'https://{base_domain}/exam/pdf/question/{id}/lang/1/v{max_version}', filename=f'{exam_type}_{problem_type_str}{question_num}.pdf')
    # Also download the general instructions
    for (id, max_version) in zip(general_inst_id, max_version_general_inst):
        if debug: print(f'Downloading latest version {max_version} of general instructions {id}')
        download_pdf(f'https://{base_domain}/exam/pdf/question/{id}/lang/1/v{max_version}', filename=f'{exam_type}_G{general_inst_id.index(id)}.pdf')
        general_inst_files.append(os.path.join(tmp_dir, f'{exam_type}_G{general_inst_id.index(id)}.pdf'))

if build_exam:
    build_exam_file(range(1,11) if exam_type == 'Theory' else range(1, 4), general_inst_files)
    print('\n\n', general_inst_files, '\n\n')
    build_solutions(range(1,11) if exam_type == 'Theory' else range(1, 4), general_inst_files)
