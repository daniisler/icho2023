import pandas as pd
import os
import matplotlib.pyplot as plt
from secret import figsize
plt.rcParams.update({'font.size': 20, 'legend.fontsize':18, 'legend.handlelength': 1})


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

theory_df_organizer = pd.read_csv(f'/home/daniel/Downloads/markingsTheory_Organizer_filter_totals.csv')
practical_df_organizer = pd.read_csv(f'/home/daniel/Downloads/markingsPractical_Organizer_filter_totals.csv')

theory_df_final = pd.read_csv(f'/home/daniel/Downloads/markingsTheory_Final_filter_totals.csv')
practical_df_final = pd.read_csv(f'/home/daniel/Downloads/markingsPractical_Final_filter_totals.csv')

output_dir_theory = '/home/daniel/Downloads/arbitration_plots_theory'
output_dir_practical = '/home/daniel/Downloads/arbitration_plots_practical'
os.makedirs(output_dir_theory, exist_ok=True)
os.makedirs(output_dir_practical, exist_ok=True)

organizer_ranking = pd.read_csv(f'/home/daniel/Downloads/marking_eval_Organizer.csv')
final_ranking = pd.read_csv(f'/home/daniel/Downloads/marking_eval_Final.csv')
output_dir_ranking = '/home/daniel/Downloads/arbitration_plots_ranking'
os.makedirs(output_dir_ranking, exist_ok=True)

# Compute the difference for each questions total score and plot them
for exam_type in ['Theory', 'Practical'][0:0]:
    for question_num in range(1, 11 if exam_type == 'Theory' else 5):
        difference_df = pd.DataFrame()
        difference_df['Student'] = theory_df_final['Student']
        question_num = str(question_num)
        if exam_type == 'Practical':
            difference_df[question_num] = practical_df_final[question_num] - practical_df_organizer[question_num]
        else:
            difference_df[question_num] = theory_df_final[question_num] - theory_df_organizer[question_num]
        # Remove the instances with 0 difference
        difference_df = difference_df[difference_df[question_num] != 0]
        print(f'DIFFERENCE FOR QUESTION {question_num}')
        print(difference_df.head())
        print('\n\n')
        # difference_df.to_csv('/home/daniel/Downloads/difference.csv', index=False)
        plt.figure(figsize=figsize)
        plt.hist(difference_df[question_num], bins=10, color = '#018e9e', edgecolor='black', linewidth=1.0)
        plt.title(f'Arbitration Effect: Question {question_num}', weight='bold')
        plt.xlabel('Difference (% question score)', weight='bold')
        plt.ylabel('Count', weight='bold')
        plt.savefig(f'{output_dir_theory}/q_{question_num}' if exam_type == 'Theory' else f'{output_dir_practical}/q_{question_num}.png')
        plt.close()


# Compute the difference between organizer and final ranking
difference_df = pd.DataFrame()
difference_df['Student'] = final_ranking['Student']
# Compute the rank difference for each student
medal_change_count = 0
for idx, row in final_ranking.iterrows():
    student = row['Student']
    organizer_rank = organizer_ranking[organizer_ranking['Student'] == student]['Rank'].values[0]
    final_rank = row['Rank']
    difference_df.loc[idx, 'Rank'] = final_rank - organizer_rank
    # Find if the medal has changed
    organized_medal = organizer_ranking[organizer_ranking['Student'] == student]['medal'].values[0]
    final_medal = row['medal']
    if organized_medal != final_medal:
        difference_df.loc[idx, 'medal'] = f'{organized_medal} -> {final_medal}'
        medal_change_count += 1
    else:
        difference_df.loc[idx, 'medal'] = 'unchanged'

# Remove the instances with 0 difference
# difference_df = difference_df[difference_df['Rank'] != 0]
# Plot a histogram with the difference in rank
plt.figure(figsize=figsize)
plt.hist(difference_df['Rank'], bins=40, color = '#018e9e', edgecolor='black', linewidth=1.0)
plt.title(f'Arbitration Effect: Rank', weight='bold')
plt.xlabel('Difference (Rank)', weight='bold')
plt.ylabel('Count', weight='bold')
# Add a note to the plot with the minimum and maximum rank difference
plt.text(0.2, 0.9, f'Min: {difference_df["Rank"].min()}\nMax: {difference_df["Rank"].max()}\nMedal Changed: {medal_change_count}', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.5), weight='bold')
plt.savefig(f'{output_dir_ranking}/rank_diff_hist.png')
plt.show()
plt.close()