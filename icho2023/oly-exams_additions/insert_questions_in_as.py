#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   inserd_questions_in_as.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   This script was used only once to insert the question formulation into the boxes of the answer sheets.
'''

import requests
import os
import xml.etree.ElementTree as ET
from secret import csrftoken, sessionid, problem_id_array
from requests_toolbelt.multipart import encoder
from bs4 import BeautifulSoup
import time

# Assuming you're already logged in using Firefox web browser
# Open the desired page in Firefox and perform any necessary authentication

# Use Firefox's developer tools to find the details of the request
# Look for the request made to download the file and find the necessary cookie and seession id. Define them in secret.py (see template.secrets.py)
problem_id_array=[]
# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.join(PROJECT_DIR, 'tmp_qml')
os.makedirs(tmp_dir, exist_ok=True)
debug=1

base_domain = 'icho2023-secret.oly-exams.org'#'oly-exams.daniisler.ch'

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

upload_get_headers = {
    'Host': base_domain,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': f'https://{base_domain}/exam/admin',
    'X-Requested-With': 'XMLHttpRequest',
    'Alt-Used': base_domain,
    'Connection': 'keep-alive',
    'Cookie': f'csrftoken={csrftoken}; sessionid={sessionid}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}


# Set the necessary headers for qml import
upload_headers = {
    'Host': base_domain,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': f'https://{base_domain}/exam/admin',
    'X-CSRFToken': csrftoken,
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': f'https://{base_domain}',
    'Connection': 'keep-alive',
    'Cookie': f'csrftoken={csrftoken}; sessionid={sessionid}',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-GPC': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'HTTP_PRIORITY': 'u=1'
}

# Download the qml export from a problem
def download_qml(url, filename):
    response = requests.get(url, headers=download_headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Specify the path where you want to save the downloaded file
        file_path = os.path.join(tmp_dir, filename)

        # Save the file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        
        if debug: print(f'File downloaded successfully from {url} to {file_path}')
    else:
        print(f'Could not find version {filename.split("_")[1]} for question {filename.split("_")[0]}')
    
    return response.status_code

def add_latest_versions(problem_id_array):
    links = []
    problem_id_array_with_versions = []
    for i in range(7):
        print(f'Getting https://icho2023-secret.oly-exams.org/exam/admin/?exam_id={i}')
        # Download the source of the exam management page
        response = requests.get(f'https://icho2023-secret.oly-exams.org/exam/admin/?exam_id={i}', headers=download_headers)
        # Parse the html
        soup = BeautifulSoup(response.text, 'html.parser')
         # Find all hyperlinks
        links += soup.find_all('a')
    # print([link for link in links])
    # if debug: print([link.get('href') for link in links])
    for i in range(len(problem_id_array)):
        problem_id_array_with_versions.append([])
        for id in problem_id_array[i]:
            # Find all links with the form '/exam/pdf/question/{problem_id}/lang/1/v{version_num}'
            problem_links = [link for link in links if link.get('href') and f'/exam/pdf/question/{id}/lang/1/v' in link.get('href')]
            # Find the maximum version number
            try:
                max_version = max([int(link.get('href').split('v')[1].replace('"', "").replace("\\", "")) for link in problem_links])
                # Add an elemment to the problem_id_array with the maximum version number
                problem_id_array_with_versions[i].append((id, max_version))
            except Exception as e:
                print(f'Could not find any versions for problem {id}: {e}')

    return problem_id_array_with_versions


# Upload the qml file to a problem
def upload_qml(url, filename):
    # Create the multipart data
    multipart_data = encoder.MultipartEncoder(fields={'file': (filename, open(filename, 'rb'), 'text/x-qml')})
    # Add the content type header to get a boundary
    upload_headers['Content-Type'] = multipart_data.content_type
    # Submit the post request
    response = requests.post(url, data=multipart_data, headers=upload_headers)

    # Check the response
    if response.status_code == 200:
        print('File uploaded successfully.')
    else:
        print('Error uploading the file. Status code:', response.status_code)

    print(response.text)

    return response.status_code



# Update the blocks with the same id in the solution file with the content from the question file
def update_blocks(question_file, answer_file):
    # If we get a html as answer, the cookie failed to authenticate
    with open(question_file, 'r') as f:
        with open(answer_file, 'r') as h:
            if '<!DOCTYPE html>' in f.read() or '<!DOCTYPE html>' in h.read():
                return False
    # Parse the first QML file
    question_tree = ET.parse(question_file)
    answer_tree = ET.parse(answer_file)

    # Iterate over the blocks in the task file and add the paragraph part in the answer sheet
    for block_q in question_tree.iter():
        # Check if the block has a part_nr and question_nr attribute
        if 'part_nr' in block_q.attrib and 'question_nr' in block_q.attrib:
            part_nr, question_nr = block_q.attrib['part_nr'], block_q.attrib['question_nr']
            # Find the corresponding block in the answer sheet file using the part_nr and question_nr
            # Print the whole content of the block
            block_content = ''.join(ET.tostring(child, encoding='unicode') for child in block_q)
            if debug:
                print('Block content:')
                # Print the whole content of the block
                print(block_content)

            block_a = answer_tree.find(f".//*[@part_nr='{part_nr}'][@question_nr='{question_nr}']")
            if block_a is not None and block_content != '':
                print('Updating block')
                # Add the content of the block in the first QML file to the answer sheet
                try:
                    block_content = ET.fromstring(block_content)
                    block_a.insert(0, block_content)
                    if debug: print(f'Updated block with part_nr {block_q.attrib["part_nr"]} and question_nr {block_q.attrib["question_nr"]} in {answer_file} with {block_q.text} from {question_file}')
                except Exception as e:
                    print('ERROR:', e)
                    print(f"Could not update {part_nr}.{question_nr}")

    # Save the updated solution QML file
    output_file = os.path.join(tmp_dir, f'{answer_file.replace(".qml", "")}-updated.qml')
    answer_tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    return True
    

if __name__ == '__main__':
    # Make the request to download the file
    # Triple of (question_id, answersheet_id, solution_id) needs to be entered manually (can be done once when the question is created in oly-exams)
    problem_ids = add_latest_versions(problem_id_array)
    for ((question_id, question_ver), _, _) in problem_ids:
        url = f'https://{base_domain}/exam/translation/export/question/{question_id}/lang/1/v{question_ver}'
        response_status = download_qml(url, f'q{question_id}_v{question_ver}.qml')


    for (_, (answer_id, answer_ver), _) in problem_ids:
        url = f'https://{base_domain}/exam/translation/export/question/{answer_id}/lang/1/v{answer_ver}'
        response_status = download_qml(url, f'a{answer_id}_v{answer_ver}.qml')


    # Write the questions from the question files to the answer files
    for ((question_id, question_ver), (answer_id, answer_ver), (_, _)) in problem_ids:
        # Select the question and solution files with the newest version
        question_file = os.path.join(tmp_dir, f'q{question_id}_v{question_ver}.qml')
        answer_file = os.path.join(tmp_dir, f'a{answer_id}_v{answer_ver}.qml')
        # Update the solution file with the content from the question file
        update_success = update_blocks(question_file, answer_file)
        if update_success:
            # Upload the updated solution file
            response_status = upload_qml(f'https://{base_domain}/exam/admin/{answer_id}/import', f'{answer_file.replace(".qml", "")}-updated.qml')
            if debug: print(f'Uploaded file {answer_file.replace(".qml", "")}-updated.qml with status code {response_status}')
        else:
            print(f'Failed to update file {answer_file} with content from {question_file}')
            print('Likely Authentication failed. Please check the cookie.')
    