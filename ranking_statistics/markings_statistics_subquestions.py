import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
plt.rcParams.update({'font.size': 20, 'legend.fontsize':18, 'legend.handlelength': 1})
import os
import seaborn as sns
from secret import figsize

version = 'Final'
os.makedirs(f'/home/daniel/Downloads/markings_plots_theory_subtasks_{version}/', exist_ok=True)
os.makedirs(f'/home/daniel/Downloads/markings_plots_practical_subtasks_{version}/', exist_ok=True)

df_markings_theory = pd.read_csv(f'/home/daniel/Downloads/markings_letTheory_{version}.csv')
df_markings_practical = pd.read_csv(f'/home/daniel/Downloads/markings_letPractical_{version}.csv')

# Get single dataframes for each question (theory)
question_df_list = []
for question_no in range(1, 11):
    # print([header for header in df_markings_theory.columns.values if header.startswith(f'{question_no}_')])
    question_df_list.append(df_markings_theory[[header for header in df_markings_theory.columns.values if header.startswith(f'{question_no}_')]])

# # Get correlation maps for each question
# for question_no in range(1, 11):
#     df_corr = question_df_list[question_no-1].corr()
#     plt.figure(figsize=figsize)
#     sns.heatmap(df_corr, annot=True, cmap='Blues', vmin=0, vmax=1)
#     plt.title(f'Correlation map for question {question_no}')
#     plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_subtasks_{version}/corr_question_{question_no}.png', dpi=300)
#     plt.show()
#     plt.close()

# Get histogram plots for each subtask (theory)
for question_no in range(1, 11):
    for subtask in question_df_list[question_no-1].columns.values:
        plt.figure(figsize=figsize)
        plt.hist(question_df_list[question_no-1][subtask], bins=10, color = '#018e9e', edgecolor='black', linewidth=1.0)
        # plt.hist(question_df_list[question_no-1][subtask], weights=100*np.ones(len(question_df_list[question_no-1][subtask])) / len(question_df_list[question_no-1][subtask]), bins=10, color = '#018e9e', edgecolor='black', linewidth=1.0)
        # plt.hist(question_df_list[question_no-1][subtask], bins=10)
        # plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.title(f'Question {subtask}', weight='bold')
        plt.xlabel('Achieved marks (%)', weight='bold')
        plt.ylabel('Number of students', weight='bold')
        plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_subtasks_{version}/hist_question_{subtask}.png', dpi=300)
        # plt.show()
        plt.close()
