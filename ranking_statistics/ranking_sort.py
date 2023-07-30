import pandas as pd
import numpy as np
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
debug = 0
version = 'Final'
theory_df = pd.read_csv(f'/home/daniel/Downloads/markingsTheory_{version}_filter_totals.csv')
practical_df = pd.read_csv(f'/home/daniel/Downloads/markingsPractical_{version}_filter_totals.csv')

if debug: print('Input df:\n\tTheory:', theory_df, '\n\tPractical:', practical_df)

df = pd.DataFrame()
if theory_df['Student'].equals(practical_df['Student']):
    print('The two DataFrames have the same students')
else:
    print('WARNING: The two DataFrames do not have the same students')

df['Student'] = theory_df['Student']
df['Total'] = theory_df['Totals (weighted%)'] + practical_df['Totals (weighted%)']

# Sort the DataFrame by a thu number of points
sorted_df = df.sort_values('Total', ascending=False)

if debug: print('Sorted df:\n', sorted_df)

# Add a column with the rank
sorted_df['Rank'] = sorted_df['Total'].rank(method='min', ascending=False)

if debug: print('Ranking df:\n', sorted_df)

# Calculate the number of rows corresponding to 10% and 12%
num_rows = len(df)
min_gold = int(np.ceil(num_rows * 0.10))
max_gold = int(np.floor(num_rows * 0.12))

if debug:
    print('Total amount of participants', num_rows)
    print('First 10% end at rank', min_gold+1)
    print('First 12% end at rank', max_gold+1)

# Differences in points between consecutive ranks
point_diff = np.array(sorted_df['Total'].diff())
# The first one otherwise contains NaN
point_diff[0] = 0

if debug: print('Points differences:\n', point_diff)

# Find the largest difference between the first 10% and 12%
gold_cut = min_gold+np.argmin(point_diff[min_gold:max_gold])
# Find the largest difference between the next 20% and 22%
silver_cut = gold_cut+int(np.ceil(num_rows*0.2))+np.argmin(point_diff[gold_cut+int(np.ceil(num_rows*0.20)):gold_cut+int(np.floor(num_rows*0.22))])
# Find the largest difference between the next 30% and 32%
bronze_cut = silver_cut+int(np.ceil(num_rows*0.3))+np.argmin(point_diff[silver_cut+int(np.ceil(num_rows*0.30)):silver_cut+int(np.floor(num_rows*0.32))])
# Find the largest difference between 70% and 71% (independent of previous cuts) for the honorable mentions
mention_cut = int(np.ceil(0.7*num_rows) + np.argmin(point_diff[int(np.ceil(num_rows*0.70)):int(np.floor(num_rows*0.71))]))
if debug: 
    print('Points difference in gold range:\n', point_diff[min_gold:max_gold], 'gold cut at', gold_cut-min_gold)
    print('Points difference in silver range:\n', point_diff[gold_cut+int(np.ceil(num_rows*0.20)):gold_cut+int(np.floor(num_rows*0.22))], 'silver cut at', silver_cut-gold_cut-int(np.ceil(num_rows*0.20)))
    print('Points difference in bronze range:\n', point_diff[silver_cut+int(np.ceil(num_rows*0.30)):silver_cut+int(np.floor(num_rows*0.32))], 'bronze cut at', bronze_cut-silver_cut-int(np.ceil(num_rows*0.30)))
    print('Points difference in honorable mention range:\n', point_diff[int(np.floor(num_rows*0.70)):int(np.floor(num_rows*0.71))], 'mention cut at', mention_cut-bronze_cut)

# Return the results
print('Gold until rank', gold_cut, 'after which the point difference is', point_diff[gold_cut])
print('Silver until rank', silver_cut, 'after which the point difference is', point_diff[silver_cut])
print('Bronze until rank', bronze_cut, 'after which the point difference is', point_diff[bronze_cut])
print('Honorable Mention until rank', mention_cut, 'after which the point difference is', point_diff[mention_cut])

# Write medal column to csv
sorted_df['medal'] = ['Gold' if i in range(0, gold_cut) else 'Silver' if i in range(gold_cut, silver_cut) else 'Bronze' if i in range(silver_cut, bronze_cut) else 'Honorable Mention' if i in range(bronze_cut, mention_cut) else 'Participant' for i in range(0, num_rows)]

sorted_df.to_csv(f'/home/daniel/Downloads/marking_eval_{version}.csv', index=False)
