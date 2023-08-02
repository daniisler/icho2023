import requests
import os
from secret import csrftoken, sessionid, solutions_id_array
from requests_toolbelt.multipart import encoder
from bs4 import BeautifulSoup
import re

# Assuming you're already logged in using Firefox web browser
# Open the desired page in Firefox and perform any necessary authentication

# Use Firefox's developer tools to find the details of the request
# Look for the request made to download the file and find the necessary cookie and seession id. Define them in secret.py (see template.secrets.py)

# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
tmp_dir = os.path.join(PROJECT_DIR, 'tmp_qml')
os.makedirs(tmp_dir, exist_ok=True)
debug=1

base_domain = 'icho2023-secret.oly-exams.org'#'oly-exams.daniisler.ch'

# Set the necessary headers for qml export
download_headers = {
    'Host': base_domain,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cookie': f'csrftoken={csrftoken}; sessionid={sessionid}',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
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

def add_latest_versions(solutions_id_array):
    links = []
    solutions_id_array_with_versions = []
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
    for i in range(len(solutions_id_array)):
        for id in solutions_id_array:
            # Find all links with the form '/exam/pdf/question/{problem_id}/lang/1/v{version_num}'
            problem_links = [link for link in links if link.get('href') and f'/exam/pdf/question/{id}/lang/1/v' in link.get('href')]
            # Find the maximum version number
            try:
                max_version = max([int(link.get('href').split('v')[1].replace('"', "").replace("\\", "")) for link in problem_links])
                # Add an elemment to the problem_id_array with the maximum version number
                solutions_id_array_with_versions.append((id, max_version))
            except Exception as e:
                print(f'Could not find any versions for problem {id}: {e}')

    return solutions_id_array_with_versions


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


def replace_points_with_color(solution_file):
    # Read the solution file
    with open(solution_file, 'r') as f:
        content = f.read()
    # First replace all the margin-left's with something else:
    pattern_margins = r'margin-left:(\d+(?:\.\d+)?)pt'
    replaced_content = re.sub(pattern_margins, r'margin-left:\1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', content, flags=re.IGNORECASE)
    # Regular expression pattern to match the point values
    pattern = r'(\d+(?:\.\d+)?)(?!\s*pt")(?!")\s*(?![^\s{}]*[}\\])(?:pts?|points?)'
    replaced_content = re.sub(pattern, r'\\textcolor{blue}{\1pt}', replaced_content, flags=re.IGNORECASE)
    # Replace the margin-left's back
    pattern = r'margin-left:(\d+(?:\.\d+)?)xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    replaced_content = re.sub(pattern, r'margin-left:\1pt', replaced_content, flags=re.IGNORECASE)
    #replaced_content = re.sub(pattern, lambda match: match.group(1) or (r'\textcolor{blue}{\1pt}'), content, flags=re.IGNORECASE)
    # Write the replaced content to the file
    with open(f'{solution_file.replace(".qml", "")}-updated.qml', 'w') as f:
        f.write(replaced_content)
    
    return True
    

if __name__ == '__main__':
    # Make the request to download the file
    # Triple of (question_id, answersheet_id, solution_id) needs to be entered manually (can be done once when the question is created in oly-exams)
    solution_ids = add_latest_versions(solutions_id_array)

    # All versions will be downloaded and the newest version will be used
    for (solution_id, solution_ver) in solution_ids:
        url = f'https://{base_domain}/exam/translation/export/question/{solution_id}/lang/1/v{solution_ver}'
        response_status = download_qml(url, f's{solution_id}_v{solution_ver}.qml')


    # Modify the solutions and reupload the qml files
    for (solution_id, solution_ver) in solution_ids:
        # Select the solution files with the newest version
        solution_file = os.path.join(tmp_dir, f's{solution_id}_v{solution_ver}.qml')
        # Update the solution file with the content from the question file
        update_success = replace_points_with_color(solution_file)
        if update_success:
            # Upload the updated solution file
            response_status = upload_qml(f'https://{base_domain}/exam/admin/{solution_id}/import', f'{solution_file.replace(".qml", "")}-updated.qml')
            if debug: print(f'Uploaded file {solution_file.replace(".qml", "")}-updated.qml with status code {response_status}')
        else:
            print("Failed to change points colors in solution file")
            print('Likely Authentication failed. Please check the cookie.')
    