import os
import pandas as pd

official_ranking_df = pd.read_csv('/home/daniel/Downloads/marking_eval_Final_merged.csv')

merged_df = official_ranking_df
for student_idx in range(1, 5):
    orig_script_names_df = pd.read_csv(f'/home/daniel/Downloads/Stud_{student_idx}.csv', header=1)
    merged_df = pd.merge(merged_df, orig_script_names_df, how='left', left_on=['First name', 'Last name'], right_on=[f'Student {student_idx} First Name - Value', f'Student {student_idx} Last Name - Value'])

for idx, row in merged_df.iterrows():
    found_orig_script = False
    for student_idx in range(1, 5):
        # If the student has a native script name, use that
        if not pd.isna(row[f'Student {student_idx} native script full name - Value']):
            # print(row[f'Student {student_idx} native script full name - Value'])
            official_ranking_df.loc[idx, f'Student native script full name - Value'] = row[f'Student {student_idx} native script full name - Value']
            found_orig_script = True
            break
    if not found_orig_script:
        official_ranking_df.loc[idx, f'Student native script full name - Value'] = row['First name']+' '+row['Last name']

# official_ranking_df.to_csv('/home/daniel/Downloads/marking_eval_Final_merged_with_orig_script_names.csv', index=False)

long_term_df = pd.DataFrame()

long_term_df['Contestant'] = official_ranking_df["First name"].str.strip()+' '+official_ranking_df["Last name"].str.strip()
long_term_df['Original Script'] = official_ranking_df['Student native script full name - Value']
long_term_df['Country'] = official_ranking_df['DELEGATION']
long_term_df['Rank'] = official_ranking_df['Rank']
long_term_df['Award'] = official_ranking_df['medal']

print(long_term_df.head())

long_term_df.to_csv('/home/daniel/Downloads/long_term_ranking.csv', index=False)