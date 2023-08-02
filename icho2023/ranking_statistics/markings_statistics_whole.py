#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   markings_statistics_whole.py
@Time    :   2023/08/02
@Author  :   Daniel Isler
@Contact :   exams@icho2023.ch
@Desc    :   Gives somes statistics about the ranking, including medal distribution.
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
plt.rcParams.update({'font.size': 20, 'legend.fontsize':25, 'legend.handlelength': 1})
import os
import seaborn as sns
from secret import figsize

version = 'Final'
os.makedirs('/home/daniel/Downloads/markings_plots_Final/', exist_ok=True)

df_overall = pd.read_csv(f'/home/daniel/Downloads/marking_eval_{version}.csv')

# Barplot of the students total score by rank
plt.figure(figsize=figsize)
# Add an overlay where the medals are allocated
gold_idx = len([row for _, row in df_overall.iterrows() if row['medal']=='Gold'])
silver_idx = len([row for _, row in df_overall.iterrows() if row['medal']=='Silver'])+gold_idx
bronze_idx = len([row for _, row in df_overall.iterrows() if row['medal']=='Bronze'])+silver_idx
honorable_idx = len([row for _, row in df_overall.iterrows() if row['medal']=='Honorable Mention'])+bronze_idx
# plt.axvspan(0, gold_idx, facecolor='gold', alpha=0.5)
# plt.axvspan(gold_idx, silver_idx, facecolor='silver', alpha=0.75)
# plt.axvspan(silver_idx, bronze_idx, facecolor='#B1560F', alpha=0.5)
# plt.axvspan(bronze_idx, honorable_idx, facecolor='#9bc531', alpha=0.3)
plt.bar(df_overall['Rank'], df_overall['Total'], color='#018e9e', width=0.5889)
plt.title('Total score by rank', weight='bold')
plt.xlabel('Rank', weight='bold')
# Set the y-ticks
plt.yticks(np.arange(0, 110, 10.0))
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.ylabel('Total score', weight='bold')
# Get the median
median = np.mean(df_overall['Total'])
std = np.std(df_overall['Total'])
print('Mean overall:', median)
print('Std overall:', std)
print('Max overall:', max(df_overall['Total']))
print('Min overall:', min(df_overall['Total']))
# Add the mean as legend value
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/barplot_totals.png')
# plt.legend([f'Median: {round(median)}%'], loc='upper right')
# plt.show()
plt.close()

# Histogram plot of the students total score
plt.figure(figsize=figsize)
plt.hist(df_overall['Total'], bins=17, color = '#018e9e', edgecolor='black', linewidth=1.0)
plt.xticks(np.arange(0, 100, 10.0))
plt.title('Total score', weight='bold')
# plt.gca().axes.get_xaxis().set_ticks([])
plt.xlabel('Total (weighted%)', weight='bold')
plt.ylabel('Number of students', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/hist_totals.png')
plt.close()

# Bar plot of only the gold medals
plt.figure(figsize=figsize)
plt.bar(df_overall['Rank'][:gold_idx], df_overall['Total'][:gold_idx], color='gold')
plt.bar(df_overall['Rank'][gold_idx:gold_idx+2], df_overall['Total'][gold_idx:gold_idx+2], color='silver', hatch='//')
plt.vlines(gold_idx+0.5, 0, max(df_overall['Total'][:gold_idx+2]), color='red', linestyle='dashed')
plt.title('Gold medals', weight='bold')
plt.xlabel('Rank', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.ylabel('Total score', weight='bold')
# Get the median
median = np.median(df_overall['Total'][:gold_idx])
print('Median gold:', median)
# Add a label with the gold_idx
plt.text(gold_idx/2, max(df_overall['Total'][:gold_idx+2]), f'Gold until rank {gold_idx}', ha='center', va='center', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/barplot_gold.png')
# plt.show()
plt.close()

# Bar plot of only the silver medals
plt.figure(figsize=figsize)
plt.bar(df_overall['Rank'][gold_idx:silver_idx], df_overall['Total'][gold_idx:silver_idx], color='silver')
plt.bar(df_overall['Rank'][silver_idx:silver_idx+2], df_overall['Total'][silver_idx:silver_idx+2], color='#B1560F', hatch='//')
plt.vlines(silver_idx+0.5, 0, max(df_overall['Total'][gold_idx:silver_idx]), color='red', linestyle='dashed')
plt.title('Silver medals', weight='bold')
plt.xlabel('Rank', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.ylabel('Total score', weight='bold')
# Get the median
median = np.median(df_overall['Total'][gold_idx:silver_idx])
print('Median silver:', median)
# Add a label with the silver_idx
plt.text((silver_idx-gold_idx)/2+gold_idx, max(df_overall['Total'][gold_idx:silver_idx]), f'Silver until rank {silver_idx}', ha='center', va='center', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/barplot_silver.png')
# plt.show()
plt.close()

# Bar plot of only the bronze medals
plt.figure(figsize=figsize)
plt.bar(df_overall['Rank'][silver_idx:bronze_idx], df_overall['Total'][silver_idx:bronze_idx], color='#B1560F')
plt.bar(df_overall['Rank'][bronze_idx:bronze_idx+2], df_overall['Total'][bronze_idx:bronze_idx+2], color='#9bc531', hatch='//')
plt.vlines(bronze_idx+0.5, 0, max(df_overall['Total'][silver_idx:bronze_idx]), color='red', linestyle='dashed')
plt.title('Bronze medals', weight='bold')
plt.xlabel('Rank', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.ylabel('Total score', weight='bold')
# Get the median
median = np.median(df_overall['Total'][silver_idx:bronze_idx])
print('Median bronze:', median)
# Add a label with the bronze_idx
plt.text((bronze_idx-silver_idx)/2+silver_idx, max(df_overall['Total'][silver_idx:bronze_idx]), f'Bronze until rank {bronze_idx}', ha='center', va='center', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/barplot_bronze.png')
# plt.show()
plt.close()

# Bar plot of only the honorable mentions
plt.figure(figsize=figsize)
plt.bar(df_overall['Rank'][bronze_idx:honorable_idx], df_overall['Total'][bronze_idx:honorable_idx], color='#9bc531')
plt.bar(df_overall['Rank'][honorable_idx:honorable_idx+2], df_overall['Total'][honorable_idx:honorable_idx+2], color='#018e9e', hatch='//')
plt.vlines(honorable_idx+0.5, 0, max(df_overall['Total'][bronze_idx:honorable_idx]), color='red', linestyle='dashed')
plt.title('Honorable mentions', weight='bold')
plt.xlabel('Rank', weight='bold')
# Hide the y-axis
# plt.gca().axes.get_yaxis().set_ticks([])
plt.ylabel('Total score', weight='bold')
# Get the median
median = np.median(df_overall['Total'][bronze_idx:honorable_idx])
print('Median honorable:', median)
# Add a label with the honorable_idx
plt.text((honorable_idx-bronze_idx)/2+bronze_idx, max(df_overall['Total'][bronze_idx:honorable_idx]), f'Honorable mention until rank {honorable_idx}', ha='center', va='center', weight='bold')
plt.savefig(f'/home/daniel/Downloads/markings_plots_Final/barplot_honorable.png')
# plt.show()
plt.close()



