import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
plt.rcParams.update({'font.size': 20, 'legend.fontsize':18, 'legend.handlelength': 1})
import os
import seaborn as sns
from secret import figsize

version = 'Final'
os.makedirs(f'/home/daniel/Downloads/markings_plots_theory_{version}/', exist_ok=True)


exam_type = 'Theory' # 'Theory'
num_questions = 3 if exam_type=='Practical' else 10

df_markings_org = pd.read_csv(f'/home/daniel/Downloads/markings{exam_type}_{version}_filter.csv')
if exam_type == 'Theory':
    max_points = [22,33,29,34,34.5,32,34,31,29,39]
    weights_array = [5,5,6,6,7,7,7,5,6,6]
else:
    max_points = [70,90,59]
    weights_array = [16,13,11]

# Sum up the points in each subtask
df_totals = pd.DataFrame()
# Copy the 'Student' column from the original dataframe
rows_weighted = []
for index, row in df_markings_org.iterrows():
    sum_weighed = 0
    for question_num in range(1, num_questions+1):
        num_points = 0
        num_subtasks = 0
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
print('Mean theory:', np.mean(df_totals['Totals (weighted%)']))
print('Std theory:', np.std(df_totals['Totals (weighted%)']))
print('Max theory:', max(df_totals['Totals (weighted%)']))
print('Min theory:', min(df_totals['Totals (weighted%)']))

df_totals.to_csv(f'/home/daniel/Downloads/markings{exam_type}_{version}_filter_totals.csv', index=False)


# Correlation map between the questions
df_corr = df_totals.drop(columns=['Student', 'Totals (weighted%)']).corr()
plt.figure(figsize=(12,7.5))
dataplot = sns.heatmap(df_corr, cmap='Blues', vmin=0, vmax=1, annot=True, annot_kws={'size': 18})
plt.title(f'Correlation between questions ({exam_type})', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_{version}/markings_{exam_type.lower()}_corr.png')
plt.show()
plt.close()

# Plot the histogram for each question
# for question_num in list(range(1, num_questions+1))+['Total']:
#     plt.figure(figsize=figsize)
#     if question_num == 'Total' and exam_type == 'Theory': question_weight = 60
#     elif question_num == 'Total' and exam_type == 'Practical': question_weight = 40
#     else: question_weight = weights_array[question_num-1]
#     plt.hist(df_totals[f'{question_num}'], weights=100*np.ones(len(df_totals[f'{question_num}'])) / len(df_totals[f'{question_num}']), bins=20, color = '#018e9e', edgecolor='black', linewidth=1.0)
#     # plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
#     plt.xticks(np.arange(0, 100, 10.0))
#     plt.title(f'Theory Question {question_num} ({question_weight}%)', weight='bold')
#     plt.xlabel('Achieved %', weight='bold')
#     plt.ylabel('% Students', weight='bold')
#     plt.tight_layout()
#     plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_{version}/{exam_type}_{question_num}_percentage_hist.png')
#     plt.close()

for question_num in list(range(1, num_questions+1))+['Totals (weighted%)']:
    plt.figure(figsize=figsize)
    if question_num == 'Totals (weighted%)' and exam_type == 'Theory': question_weight = 60
    elif question_num == 'Totals (weighted%)' and exam_type == 'Practical': question_weight = 40
    else: question_weight = weights_array[question_num-1]
    plt.hist(df_totals[f'{question_num}'], bins=20, color = '#018e9e', edgecolor='black', linewidth=1.0)
    plt.xticks(np.arange(0, 70, 10.0))
    title_str = f'Theory Question {question_num} ({question_weight}%)' if isinstance(question_num, int) else 'Total score theory exam (60%)'
    plt.title(title_str, weight='bold')
    # Hide the x-axis
    # plt.gca().axes.get_xaxis().set_ticks([])
    plt.xlabel('Achieved %', weight='bold')
    plt.ylabel('Number of students', weight='bold')
    plt.tight_layout()
    plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_{version}/{exam_type}_{question_num}_hist.png')
    plt.close()

# Plot a all the datapoints
for question_no in list(range(1, num_questions+1))+['Totals (weighted%)']:
    scores_sorted = sorted(df_totals[str(question_no)], reverse=True)
    plt.figure(figsize=figsize)
    plt.bar(np.linspace(0, 348, len(scores_sorted)), scores_sorted, color='#018e9e')
    title_str = f'Total score theory Q-{question_no}' if isinstance(question_no, int) else 'Total score theory exam (60%)'
    plt.title(title_str, weight='bold')
    # Hide the y-axis
    # plt.gca().axes.get_yaxis().set_ticks([])
    plt.xlabel('Student_idx', weight='bold')
    plt.ylabel('Achieved percentage', weight='bold')
    plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_{version}/{exam_type}_scatter_{question_no}_sorted.png')
    plt.close()


# Create a geopandas DataFrame from the country codes and scores
# gdf = gpd.GeoDataFrame(df_totals, geometry=gpd.points_from_xy(df_totals['Student'].str[:3], [0]*len(df_totals)))

# # World map shapefile (You'll need to download the shapefile from a source)
# # Replace "world_shapefile.shp" with the path to the shapefile on your system
# world_map = gpd.read_file("world_shapefile.shp")

# Merge the world map with the scores DataFrame based on the country codes
# merged = world_map.set_index('ISO_A3').join(gdf.set_index('Country Code'))

# # Plot the heatmap
# fig, ax = plt.subplots(1, 1, figsize=figsize)
# ax.set_title('Grades Heatmap by Country')
# ax.set_xlim([-180, 180])
# ax.set_ylim([-90, 90])
# merged.plot(column='Organic Synth.', cmap='YlGnBu', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)

# # Show the plot
# plt.show()

# Barplot with each students score sorted

plt.figure(figsize=figsize)
scores_sorted = sorted(df_totals['Totals (weighted%)'], reverse=True)
plt.bar(np.linspace(0, 348, len(scores_sorted)), scores_sorted, color='#018e9e')
plt.title('Scores Theory (60%)', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.xlabel('Rank', weight='bold')
plt.ylabel('Achieved percentage', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_theory_{version}/01_theory_sorted.png')
median = np.median(df_totals['Total'])
print('Median Theory:', median)
plt.close()

