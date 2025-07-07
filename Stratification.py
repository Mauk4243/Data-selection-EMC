#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 10:22:14 2025

@author: ERASMUSMC+109098
"""
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('InstoradCervixBT_sheet.csv')
#df = pd.read_csv('selected_p_info.csv')

# Filter rows where 'Applicator' contains either 'Venezia' or 'Geneva'
filtered_df = df[df['Applicator'].str.contains('Venezia|Geneva', na=False)]

# Extract just the applicator name ("Venezia" or "Geneva") into a new column
filtered_df['ApplicatorType'] = filtered_df['Applicator'].str.extract(r'(Venezia|Geneva)')

# Plot countplot
sns.countplot(x='ApplicatorType', data=filtered_df)
plt.title('Distribution of Applicator Types')
plt.xlabel('Applicator')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

column_name = 'Applicator'

Fletcher_count = df[column_name].str.contains('Fletcher', case=False, na=False).sum()
Venezia_count = df[column_name].str.contains('Venezia', case=False, na=False).sum()
Geneva_count = df[column_name].str.contains('Geneva', case=False, na=False).sum()

# Print results
print(f'Fletcher count studies: {Fletcher_count}')
print(f'Venezia count studies: {Venezia_count}')
print(f'Geneva count studies: {Geneva_count}')

criteria_count = df[df['MeetCriteria'].str.contains('YES', na=False)]
print(len(criteria_count))
MR = df[df['ImageType'].str.contains('MR FIESTA', na=False)]
print(len(MR))

