import csv
import random
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
version = 'Final'

for exam_type in ['Theory', 'Practical']:
    infile = os.path.join('/home/daniel/Downloads', f'markings_{exam_type}_{version}.csv')
    outfile_let = os.path.join('/home/daniel/Downloads', f'markings_let{exam_type}_{version}.csv')
    outfile = os.path.join('/home/daniel/Downloads', f'markings_percentage{exam_type}_{version}.csv')
    outfile_org = os.path.join('/home/daniel/Downloads', f'markings{exam_type}_{version}_filter.csv')
    fill_random = False

    # List of weighting factors for each task (as percentage)
    if exam_type == 'Theory':
        weighting_factors = [5,5,6,6,7,7,7,5,6,6]
    if exam_type == 'Practical':
        weighting_factors = [16, 13, 11, 100]

    def fill_empty_columns(csv_file, outfile):
        # Open the CSV file
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            # Find the maximum point values for each task
            max_points = {}
            for header in headers:
                if '(' in header and ')' in header:
                    start = header.index('(') + 1
                    end = header.index(')')
                    task = header[:start - 1]
                    points = float(header[start:end])
                    max_points[task] = points
            rows_org = []
            rows = []
            rows_let = []
            for row in reader:
                # Only take final marking
                if row['Version'] == 'F':
                    row_let = row.copy()
                    row_org = row.copy()
                    for column in headers:
                        task = column.strip().split(' (')[0]+' '
                        if task in max_points.keys():
                            # Use the percentage from the weighting factors list to calculate the achieved precentage overall
                            task_part = task.split('.')[0].split(' ')[-1]
                            if task_part in ['Yield', 'TLC', 'Ded']:
                                task_idx = 0
                            elif task_part == 'Titr':
                                task_idx = 1
                            else:
                                task_idx = int(task.split('.')[0].split(' ')[-1]) - 1
                            task_weight = weighting_factors[task_idx] / 100
                            # print(task_idx, 'With weight', task_weight, task)
                            if row[column.strip()] != '-':
                                points = max_points[task]
                                #print(row[column.strip()], points)
                                if row[column.strip()] == '':
                                    row[column.strip()] = 0
                                    row_let[column.strip()] = 0
                                    row_org[column.strip()] = 0
                                row[column.strip()] = task_weight * float(row[column.strip()]) / points
                                row_let[column.strip()] = float(row_let[column.strip()]) / points
                            else:
                                row[column.strip()] = 0
                                row_let[column.strip()] = 0
                                row_org[column.strip()] = 0
                    rows_org.append(row_org)
                    rows.append(row)
                    rows_let.append(row_let)

        # Write the updated data to a new CSV file
        with open(outfile, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        with open(outfile_let, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # For a header like Molecular Imaging - Answer sheet - 1.1 (1.00) only take 1.1
            let_headers = []
            for header in headers:
                if '(' in header and ')' in header:
                    let_headers.append(header.strip().split(' (')[0].split(' - ')[-1].replace('.', '_'))
                else:
                    let_headers.append(header)
            # Change the header while keeping the data that was inserted
            writer.writerow(dict(zip(headers,let_headers)))
            writer.writerows(rows_let)

        with open(outfile_org, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            # For a header like Molecular Imaging - Answer sheet - 1.1 (1.00) only take 1.1
            org_headers = []
            for header in headers:
                if '(' in header and ')' in header:
                    org_headers.append(header.strip().split(' (')[0].split(' - ')[-1].replace('.', '_'))
                else:
                    org_headers.append(header)
            # Change the header while keeping the data that was inserted
            writer.writerow(dict(zip(headers,org_headers)))
            writer.writerows(rows_org)

if __name__ == "__main__":
    fill_empty_columns(infile, outfile)
