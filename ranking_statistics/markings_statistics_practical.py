import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
plt.rcParams.update({'font.size': 20, 'legend.fontsize':18, 'legend.handlelength': 1})
import os
import seaborn as sns
from secret import figsize

version = 'Final'
os.makedirs(f'/home/daniel/Downloads/markings_plots_practical_{version}/', exist_ok=True)

exam_type = 'Practical' # 'Theory' or 'Practical'
num_questions = 4

df_markings_org = pd.read_csv(f'/home/daniel/Downloads/markings{exam_type}_{version}_filter.csv')
if exam_type == 'Theory':
    max_points = [22,33,29,34,34.5,32,34,31,29,39]
    weights_array = [5,5,6,6,7,7,7,5,6,6]
else:
    max_points = [70,90,59,40]
    weights_array = [16,13,11,40]

# Sum up the points in each subtask
df_totals = pd.DataFrame()
# Copy the 'Student' column from the original dataframe
rows_weighted = []
for index, row in df_markings_org.iterrows():
    sum_weighed = 0
    first_loop = True
    for question_num in list(range(1, num_questions+1)):
        num_points = 0
        num_subtasks = 0
        if question_num == 1 and first_loop:
            for task in ['Yield_A','TLC_A','Ded_A','Yield_B','TLC_B','Ded_B']:
                num_points += row[task]
                num_subtasks += 1
        if question_num == 2 and first_loop:
            for task in ['Titr_1','Titr_2']:
                num_points += row[task]
                num_subtasks += 1
        for column_header in df_markings_org.columns.values:
            if f'{question_num}_' in column_header:
                num_points += row[column_header]
                num_subtasks += 1
        if num_subtasks > 0:
            # print(f'Student {row["Student"]} reached {100*num_points/max_points[question_num-1]}% in question: {question_num}')
            df_totals.loc[index, f'{question_num}'] = 100*num_points/max_points[question_num-1]
            sum_weighed += weights_array[question_num-1]*num_points/max_points[question_num-1]        
    rows_weighted.append(sum_weighed)

# Add the sum of the rows in the last column
df_totals['Total'] = df_totals.sum(axis=1)/num_questions
df_totals['Student'] = df_markings_org['Student']
df_totals['Totals (weighted%)'] = rows_weighted

# Mean, std dev, max and min
print('Mean practical:', np.mean(df_totals['Totals (weighted%)']))
print('Std practical:', np.std(df_totals['Totals (weighted%)']))
print('Max practical:', max(df_totals['Totals (weighted%)']))
print('Min practical:', min(df_totals['Totals (weighted%)']))

df_totals.to_csv(f'/home/daniel/Downloads/markings{exam_type}_{version}_filter_totals.csv', index=False)


# Correlation map between the questions
df_corr = df_totals.drop(columns=['Student', 'Totals (weighted%)', '4']).corr()
dataplot = sns.heatmap(df_corr, cmap='Blues', vmin=0, vmax=1, annot=True, annot_kws={'size': 18})
plt.title(f'Correlation ({exam_type})', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_practical_{version}/markings_{exam_type.lower()}_corr.png')
# plt.show()

# Plot the histogram for each question
# for question_num in list(range(1, num_questions+1))+['Total']:
#     plt.figure(figsize=figsize)
#     if question_num == 'Total' and exam_type == 'Theory': question_weight = 60
#     elif question_num == 'Total' and exam_type == 'Practical': question_weight = 40
#     else: question_weight = weights_array[question_num-1]
#     plt.hist(df_totals[f'{question_num}'], weights=100*np.ones(len(df_totals[f'{question_num}'])) / len(df_totals[f'{question_num}']), bins=20, color = '#018e9e', edgecolor='black', linewidth=1.0)
#     # plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
#     plt.xticks(np.arange(0, 100, 10.0))
#     plt.title(f'Practical Question {question_num} ({question_weight}%)', weight='bold')
#     plt.xlabel('Achieved %', weight='bold')
#     plt.ylabel('% Students', weight='bold')
#     plt.tight_layout()
#     plt.savefig(f'/home/daniel/Downloads/markings_plots_practical_{version}/{exam_type}_{question_num}_percentage_hist.png')
#     plt.close()

for question_num in list(range(1, num_questions+1))+['Totals (weighted%)']:
    plt.figure(figsize=figsize)
    if question_num == 'Totals (weighted%)' and exam_type == 'Theory': question_weight = 60
    elif question_num == 'Totals (weighted%)' and exam_type == 'Practical': question_weight = 40
    else: question_weight = weights_array[question_num-1]
    plt.hist(df_totals[f'{question_num}'], bins=20, color = '#018e9e', edgecolor='black', linewidth=1.0)
    plt.xticks(np.arange(0, 50, 10.0))
    title_str = f'Practical Question {question_num} ({question_weight}%)' if isinstance(question_num, int) else 'Total score practical exam (40%)'
    plt.title(title_str, weight='bold')
    # Hide the x-axis
    # plt.gca().axes.get_xaxis().set_ticks([])
    plt.xlabel('Achieved %', weight='bold')
    plt.ylabel('Number of students', weight='bold')
    plt.tight_layout()
    plt.savefig(f'/home/daniel/Downloads/markings_plots_practical_{version}/{exam_type}_{question_num}_hist.png')
    plt.close()

# Plot a all the datapoints
for question_no in list(range(1, num_questions+1))+['Totals (weighted%)']:
    scores_sorted = sorted(df_totals[str(question_no)], reverse=True)
    plt.figure(figsize=figsize)
    plt.bar(np.linspace(0, 348, len(scores_sorted)), scores_sorted, color='#018e9e')
    title_str = f'Total score practical Q-{question_no}' if isinstance(question_no, int) else 'Total score practical exam (40%)'
    plt.title(title_str, weight='bold')
    # Hide the y-axis
    # plt.gca().axes.get_yaxis().set_ticks([])
    plt.xlabel('Rank', weight='bold')
    plt.ylabel('Achieved percentage', weight='bold')
    plt.savefig(f'/home/daniel/Downloads/markings_plots_practical_{version}/{exam_type}_scatter_{question_no}_sorted.png')

# Barplot with each students score sorted

plt.figure(figsize=figsize)
scores_sorted = sorted(df_totals['Totals (weighted%)'], reverse=True)
plt.bar(np.linspace(0, 348, len(scores_sorted)), scores_sorted, color='#018e9e')
# Get the mean and standard deviation of the total score
median = np.median(df_totals['Total'])
print('Median Practical:', median)
plt.title('Scores Practical (40%)', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.xlabel('Rank', weight='bold')
plt.ylabel('Achieved percentage', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_practical_{version}/01_practical_sorted.png')
plt.close()

