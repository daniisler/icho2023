#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   marked_exams_sorter.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Sorts the scanned marked exams by qr code into a folder structure you should read from the code.
'''

import os
from PyPDF2 import PdfWriter, PdfReader, PdfMerger
import json
import shutil
import uuid
from PIL import Image
import zbarlight
import contexttimer
import re
import datetime
import subprocess
import random

batch_num=12

# Env
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
debug = 1
temp_folder = os.path.join('/tmp', str(uuid.uuid4()))
# Where can I find the scans?
# input_scans_dir = os.path.join(PROJECT_DIR, 'combined_ans')
input_scans_dir = f'/home/daniel/Downloads/rescans_single_pdfs_{str(batch_num)}'
input_scans_tracking = os.path.join(PROJECT_DIR, 'scans_tracking.json')
scanned_dict = json.load(open(input_scans_tracking, 'r'))
# Where should I put the sorted scans?
exam_type='Theory'
store_file = True
processing_dir = os.path.join(PROJECT_DIR, f'processing_{exam_type}')
problems_dir = os.path.join(PROJECT_DIR, f'problems_dir_{exam_type}_{str(batch_num)}')
sorted_dir = os.path.join(PROJECT_DIR, f'sorted_dir_{exam_type}')
os.makedirs(processing_dir, exist_ok=True)
os.makedirs(problems_dir, exist_ok=True)
os.makedirs(sorted_dir, exist_ok=True)
# Is the scan double sided?
double_sided = True
# Do you want to allow any document without a barcode?
allow_no_barcode = True
os.makedirs(temp_folder, exist_ok=True)


def all_same(items):
    return all(x == items[0] for x in items)


# Checks if student code is valid
def is_valid_code(code):
    code_pattern = re.compile(r'^([^ ]+) ([^ ]+) ([^ ]+)$')
    match = code_pattern.match(code)
    if not match:
        print('Barcode "{}" is not valid. I will ignore it'.format(code))
        return False
    if match.group(1).count('-') not in (1,2):
        print('Number of `-` inconsistent in first group: '+code)
        return False
    if match.group(2).count('-') != 1:
        print('Number of `-` inconsistent in second group: '+code)
        return False
    if match.group(3).count('-') != 1:
        print('Number of `-` inconsistent in third group: '+code)
        return False
    return True

cropped_output_file = None
cropped_output_file_counter = 0

def crop_image(im, crop=None):
    global cropped_output_file_counter
    if crop is not None:
        width, height = im.size
        LEFT_CUT = 0.35 # previously: 0.35
        RIGHT_CUT = 0.65 # previously: 0.65
        HEIGHT_CUT = 0.2 # previously: 0.2
        UPPER_CUT = 0.00 # previously: 0.0
        if crop == 'upper':
            mask = (round(LEFT_CUT * width), round(height * UPPER_CUT), round(RIGHT_CUT * width), round(height * HEIGHT_CUT))
        else:
            mask = (round(LEFT_CUT * width), height - round(height / 5.), round(RIGHT_CUT * width), height - 1)
        im = im.crop(mask)
        # im.show()
    if cropped_output_file is not None:
        fn = os.path.splitext(cropped_output_file)[0] + '_{:03d}_{}'.format(cropped_output_file_counter, str(crop)) + '.png'
        im.save(fn)
        cropped_output_file_counter += 1
        cropped_output_file_counter %= 1000
    return im


def detect_barcode_zbarlight(img_path):

    im = Image.open(img_path)
    im.load()
    # im = im.convert(mode='I')

    for crop in ['upper', 'lower']:
        for mode in ['RGB', '1', 'L', 'P', 'RGB', 'RGBA', 'CMYK', 'YCbCr', 'I', 'F']:
            for size_mult in [0.2, 0.5, 1.]:
                for contrast_mult in [1., 2.]:
                    im_cont = im.point(lambda p: p * contrast_mult)
                    im_c = crop_image(im_cont, crop)
                    new_size = [round(s * size_mult) for s in im_c.size]
                    im_c_convert = im_c.convert(mode=mode).resize(new_size)
                    symbols = zbarlight.scan_codes(['qrcode'], im_c_convert)
                    if symbols is None:
                        symbols = []
                    symbols = [s.decode('ascii') for s in symbols]
                    if len(symbols) > 0:
                        print('Working params:', mode, crop, size_mult, contrast_mult)
                        return symbols, crop
    return symbols, None


def detect_barcode(img_path):
    symbols, crop = detect_barcode_zbarlight(img_path)
    symbols = list(filter(is_valid_code, symbols))

    if len(symbols) == 0:
        return None, None
    elif not all_same(symbols):
        raise RuntimeError('Multiple barcodes detected and they are different! {}'.format(symbols))
    else:
        return symbols[0], crop
    

def detect_barcodes_pdftoppm(input, ppi=200):
    """ Detect barcodes in a PDF file
    :param input: input file object
    :param ppi: resolution in points per inch for the PDF to image converion
    :return: List of tuples (page_number, detected_barcode, crop (upper/lower) to see if page needs to be turned)
    """
    pages = []
    if debug: print('starting pdftoppm')

    with contexttimer.Timer() as t:
        p = subprocess.Popen(
            # ["pdftoppm", "-r",  str(int(ppi)), input.name, os.path.join(temp_folder, "temp")],
            ["pdftoppm", "-gray", "-aa", "no", "-aaVector", "no", "-r",  str(int(ppi)), input.name, os.path.join(temp_folder, "temp")],
            # ["pdftoppm", "-gray", "-r",  str(int(ppi)), input.name, os.path.join(temp_folder, "temp")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
    if len(os.listdir(temp_folder)) != 0:
        if debug: print("pdftoppm time per page: {0}s".format(t.elapsed / len(os.listdir(temp_folder))))
    err = p.stderr.read()
    if debug: print('pdftoppm done')
    if err:
        print('PDFTOPPM PROCESSING ERROR: {}'.format(err))
    else:
        out = p.stdout.read()
        if out:
            if debug: print('pdftoppm processing log: {}'.format(out))
        if debug: print('starting to extract barcodes')
        for pg, fn in enumerate(sorted(os.listdir(temp_folder))):
            fp = os.path.join(temp_folder, fn)
            with contexttimer.Timer() as t:
                code, crop = detect_barcode(fp)
            if debug: print("detect_barcode time per page: {0}s".format(t.elapsed))
            pages.append((pg, code, crop))
            os.remove(fp)
        if debug: print('barcodes done')
    return pages


def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


def create_unique_filename(filename):
    if re.match('2\d{7}_\d{6}_\d{3}_', filename) is None:
        return "{}_{:03d}_{}".format(get_timestamp(), random.randint(0,999), filename)
    else:
        return filename
    

def page_sort(page_info):
    lookup_type = {"C" : 0, "A": 100, "W": 200, "Z": 300}  # do not use 900 or higher, 900 is used as default
    pg, code = page_info
    if code is None:
        return
    page_parts = code.split()[-1].split('-')
    try:
        val = lookup_type[page_parts[0]]
    except KeyError:
        print("page type '{}' not found, using default (900).".format(page_parts[0]))
        val = 900
    try:
        val += int(page_parts[1])
    except TypeError:
        print("failed to convert page number '{}' to int, using default (0).".format(page_parts[1]))
    return val


# Takes the qr code data array and saves the marked exam question to the students folder
def save_pages_with_qr_codes(file, qr_code_data, output_folder):
    pdf_reader = PdfReader(file)
    pages_without_qrs = False
    # Check if the number of pages in the pdf file matches the number of qr codes
    num_pages_scan = len(pdf_reader.pages) / 2 if double_sided else len(pdf_reader.pages)
    if num_pages_scan == len(qr_code_data) or allow_no_barcode:

        pdf_writer = PdfWriter()
        pdf_writer_empty = PdfMerger()
        for (page_idx, qr_code, crop) in qr_code_data:
            if qr_code is None:
                pdf_writer_empty.append(file, pages=(page_idx, page_idx+1, 1))
                pages_without_qrs = True
                continue
            qr_data = qr_code.split(' ')
            folder_path = os.path.join(output_folder, qr_data[0], qr_data[1])
            os.makedirs(folder_path, exist_ok=True)
            
            pdf_writer.add_page(pdf_reader.pages[page_idx] if crop == 'upper' else pdf_reader.pages[page_idx].rotate(180))
            output_filename = os.path.join(folder_path, f'{qr_data[2]}.pdf')
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)
            pdf_writer = PdfWriter()
        if pages_without_qrs:
            pdf_writer_empty.write(os.path.join(f'/home/daniel/Downloads/no_barcode/{len(os.listdir("/home/daniel/Downloads/no_barcode"))}.pdf'))

    else:
        print(f"Number of pages in the pdf file {num_pages_scan} does not match the number of qr codes {len(qr_code_data)}")
        shutil.copy(file, os.path.join(problems_dir, os.path.basename(file.name)))
        raise Exception("Number of pages in the pdf file does not match the number of qr codes!")


def main(input, problems_dir, sorted_dir):
    """ Recognize QR codes in a given PDF file, separate to different pdf files for the students and save them to the respective folders
    Args:
        input: input file object
        sorted_dir: directory in which to place PDFs that have been processed
        problems_dir: directory in which to place PDFs which resulted in failures
    Returns:
        None
    """
    if True:
        pages = detect_barcodes_pdftoppm(input)
        if debug: 
            print('got {} pages.'.format(len(pages)))
            print('Upside down are: {}'.format(len([crop for i,code,crop in pages if crop=='lower'])))
            print('Barcodes: {}'.format([code for i,code,crop in pages]))

        # Write the pages to the respective folders (One folder per students with one folder for each question)
        save_pages_with_qr_codes(input, [(page_num, qr_code, crop) for (page_num, qr_code, crop) in pages], sorted_dir)

        return
    
    # except Exception as error:
    #     print(f'An exception occured!\n{error}')
    #     oname = os.path.join(problems_dir, os.path.basename(input.name))
    #     shutil.copy(input.name, oname)
    #     print(u'Causing document has been saved to '+str(oname))


if __name__ == '__main__':
    for filename in [os.path.join(input_scans_dir, filename) for filename in os.listdir(input_scans_dir)]:
        if debug: print('Process file {}'.format(filename))
        input_filename = os.path.join(processing_dir, os.path.basename(filename))
        shutil.copy(filename, input_filename)
        with open(input_filename, 'rb') as input:
            main(input, sorted_dir=sorted_dir, problems_dir=problems_dir)
        os.remove(input_filename)
        if not store_file:
            os.remove(filename)
