# THIS SCRIPT SHOULD ONLY BE RUN ONCE ALL MARKED SHEETS HAVE BEEN PROVIDED, SCANNED AND SORTED
import os
from PyPDF2 import PdfMerger, PdfReader

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
skipped_q_no_theory = [2,9]
skipped_q_no_practical = [1,2]
found_pages = 0
missing_pages = 0
for exam_type in ['Theory', 'Practical']:
    num_questions = 10 if exam_type == 'Theory' else 3
    exam_idx = 1 if exam_type == 'Theory' else 2
    # Path to original scans from the answer sheets (not marked)
    scanned_exams_path = os.path.join(PROJECT_DIR, f'answer_sheets_scans_{exam_type}')
    # Path to the marked version of the answer sheets (might not contain all exams)
    sorted_dir = os.path.join(PROJECT_DIR, f'sorted_dir_Theory')

    # Loop through the exams from the sorted directory
    for student_code in os.listdir(sorted_dir):
        output_dir = os.path.join(PROJECT_DIR, f'final_version_exams_{exam_type}', student_code.split('-')[0])
        os.makedirs(output_dir, exist_ok=True)
        # Get everything that has been rescanned for this student
        merger = PdfMerger()
        for question_no in range(1, num_questions+1):
            exam_str = f'T-{question_no}' if exam_type == 'Theory' else f'P-{question_no}'
            # print((os.path.join(sorted_dir, student_code, exam_str)), os.path.exists(os.path.join(sorted_dir, student_code, exam_str)))
            if os.path.exists(os.path.join(sorted_dir, student_code, exam_str)):
                # Check out the num pages of the original scan
                possible_filenames = [f for f in os.listdir(os.path.join(scanned_exams_path, student_code)) if f.startswith(f'exam-{exam_idx}-{question_no}')]
                num_pages_orig = len(PdfReader(os.path.join(scanned_exams_path, student_code, possible_filenames[0])).pages)
                num_pages_rescan = len(os.listdir(os.path.join(sorted_dir, student_code, exam_str)))
                for page_idx in range(num_pages_orig):
                    if os.path.exists(os.path.join(sorted_dir, student_code, exam_str, f'A-{page_idx+1}.pdf')):
                        merger.append(os.path.join(sorted_dir, student_code, exam_str, f'A-{page_idx+1}.pdf'))
                        found_pages += 1
                    else:
                        print(f'WARNING: Missing page {page_idx+1} for task {question_no} for student {student_code}: {num_pages_rescan} pages instead of {num_pages_orig}')
                        merger.append(os.path.join(scanned_exams_path, student_code, possible_filenames[0]), pages=(page_idx, page_idx+1, 1))
                        missing_pages += 1
                # else:
                #     print('WARNING')
                #     print(f'Exam {exam_str} for student {student_code} has {num_pages_rescan} pages instead of {num_pages_orig}')
                #     print('Taking original scan instead')
                #     possible_filenames = [f for f in os.listdir(os.path.join(scanned_exams_path, student_code)) if f.startswith(f'exam-{exam_idx}-{question_no}')]
                #     merger.append(os.path.join(scanned_exams_path, student_code, possible_filenames[0]))
                #     missing_pages += 1
                    
            else:
                # missing_question = False
                # if not question_no in skipped_q_no_theory and exam_type == 'Theory':
                #     # print(f'WARNING: Exam {exam_str} for student {student_code} is missing')
                #     missing_question = True
                # if not question_no in skipped_q_no_practical and exam_type == 'Practical':
                #     # print(f'WARNING: Exam {exam_str} for student {student_code} is missing')
                #     missing_question = True
                # if missing_question:
                possible_filenames = [f for f in os.listdir(os.path.join(scanned_exams_path, student_code)) if f.startswith(f'exam-{exam_idx}-{question_no}')]
                merger.append(os.path.join(scanned_exams_path, student_code, possible_filenames[0]))
                if not question_no == 9 and not (question_no == 1 and exam_type == 'Practical') and not (question_no == 2 and exam_type == 'Practical'):
                    missing_pages += len(PdfReader(os.path.join(scanned_exams_path, student_code, possible_filenames[0])).pages)
        merger.write(os.path.join(output_dir, f'{student_code}.pdf'))


print(f'Found pages: {found_pages}')
print(f'Missing pages: {missing_pages}')
    
