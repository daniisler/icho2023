import os
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
question_no = 6
marked_pdfs_dir = '/home/daniel/Downloads/backup_prod/checked'

for file in os.listdir(marked_pdfs_dir):
    reader = PdfReader(os.path.join(marked_pdfs_dir, file))
    os.makedirs(os.path.join(PROJECT_DIR, 'sorted_dir_Theory', file.split('_')[1], f'T-{question_no}'), exist_ok=True)
    # print(f'Processing {file}')
    try:
        for page_idx in range(len(reader.pages)-2, len(reader.pages)):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_idx])
            print('Writing to ', os.path.join(PROJECT_DIR, 'sorted_dir_Theory', file.split('_')[1], f'T-{question_no}',  f'A-{page_idx+1}.pdf'))
            writer.write(os.path.join(PROJECT_DIR, 'sorted_dir_Theory', file.split('_')[1], f'T-{question_no}',  f'A-{page_idx+1}.pdf'))
            writer.close()
    except Exception as e:
        print('WARNING: ', e)
        print(f'File {file} needs to be processed manually.')
        #print(f'Exam {file} has {len(reader.pages)} pages and does caused an error')

