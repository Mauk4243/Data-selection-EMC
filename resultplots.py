#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 11:39:04 2025

@author: ERASMUSMC+109098
"""
# INDEX:

#1.  Box plots
#------------------------------------------
#- CTVHR (D90, D98) predicted and reference
#- CTVHR (D90, D98) difference
#- OARs predicted and reference
#- OARs difference
#------------------------------------------

#2. Table
#------------------------------------------
# DOSIMETRIC MEASUREMENT TABLE
#------------------------------------------

#3. Bin plot
#------------------------------------------
# CTVHR D90
# CTVHR D98
# OARs
#------------------------------------------


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# %matplotlib inline
# Upload data
df = pd.read_csv('Test_customL_results.csv', skiprows=1)

"""
Plan1 = Ground truth
Plan2 = Prediction
"""

#------------------------------------------------------------------------------


# Filter data for specific RT Structures and Metric Names
# Step 1: Filter the data
filtered_df = df[
    (df['RT Structure'].isin(['CTV HR', 'CTV IR'])) &
    (df['Metric Name'].isin(['Drel(0.90)', 'Drel(0.98)'])) &
    (df['RT Dose Set'].isin(['Plan1', 'Plan2']))
]

# Create a new column that combines RT Structure and Metric Name
filtered_df['RT_Metric'] = filtered_df['RT Structure'] + ' ' + filtered_df['Metric Name']

#
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=filtered_df,
    x='RT_Metric',       # X-axis: the combined RT Structure and Metric
    y='Metric Value',    # Y-axis: the actual data
    hue='RT Dose Set',      # Two boxes per group: ReferencePlan and PredictedPlan
    width=0.7
)

# Labels and title
#plt.title('Boxplots for Drel(0.90) and Drel(0.98) in CTVHR, CTVIR, and GTVRES')
plt.ylabel('Gy [J/kg]')
plt.xlabel('RT Structure & Metric')
plt.xticks(rotation=45)  # Rotate for better readability

#--------------------------------------------------------------------------------
#CTV ABSOLUTE DIFFERENCE


# Style
sns.set(style='whitegrid')

fig, ax = plt.subplots(figsize=(8,6))

# Filter the relevant data
filtered_df = df[
    (df['RT Structure'].isin(['CTV HR', 'CTV IR'])) &
    (df['Metric Name'].isin(['Drel(0.90)', 'Drel(0.98)'])) &
    (df['RT Dose Set'].isin(['Plan1', 'Plan2']))
]

# Create combined label for grouping
filtered_df['RT_Metric'] = filtered_df['RT Structure'] + ' ' + filtered_df['Metric Name']

# Pivot so we can calculate difference per patient per metric
pivot_df = filtered_df.pivot_table(
    index=['Patient ID', 'RT_Metric'],
    columns='RT Dose Set',
    values='Metric Value'
).reset_index()

# Calculate absolute difference
pivot_df['Difference'] = np.abs(pivot_df['Plan2'] - pivot_df['Plan1'])

#print(pivot_df)

# Now create a boxplot grouped by RT_Metric
sns.boxplot(
    data=pivot_df,
    x='RT_Metric',
    y='Difference',
    ax=ax,
    width=0.7
)

# Labels and display
plt.ylabel('')
plt.xlabel('')
#plt.title('Absolute Difference: Predicted vs Reference Plan')
plt.xticks(rotation=45)
plt.ylim((0,2.5))
plt.tight_layout()
plt.show()



#------------------------------------------------------------------------------
# OARs BOXPLOT REFERENCE/PREDICTED AND ABSOLUTE DIFFERENCE

#OARs predicted, reference in one plot



# Filter data for specific RT Structures and Metric Names
# Step 1: Filter the data
filtered_df = df[
    (df['RT Structure'].isin(['OAR Bladder', 'OAR Rectum', 'OAR Sigmoid', 'OAR Bowel'])) &
    (df['Metric Name']) &
    (df['RT Dose Set'].isin(['Plan1', 'Plan2']))
]

# Create a new column that combines RT Structure and Metric Name
filtered_df['RT_Metric'] = filtered_df['RT Structure'] + ' ' + filtered_df['Metric Name']

#
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=filtered_df,
    x='RT_Metric',       # X-axis: the combined RT Structure and Metric
    y='Metric Value',    # Y-axis: the actual data
    hue='RT Dose Set',      # Two boxes per group: ReferencePlan and PredictedPlan
    width=0.7
)

# Labels and title
#plt.title('Boxplots for Drel(0.90) and Drel(0.98) in CTVHR, CTVIR, and GTVRES')
plt.ylabel('Gy [J/kg]')
plt.xlabel('RT Structure & Metric')
plt.xticks(rotation=45)  # Rotate for better readability



# Style
sns.set(style='whitegrid')

fig, ax = plt.subplots(figsize=(8,6))

# Filter the relevant data
filtered_df = df[
    (df['RT Structure'].isin(['OAR Bladder', 'OAR Rectum', 'OAR Sigmoid', 'OAR Bowel'])) &
    (df['Metric Name']) &
    (df['RT Dose Set'].isin(['Plan1', 'Plan2']))
]

# Create combined label for grouping
filtered_df['RT_Metric'] = filtered_df['RT Structure'] + ' ' + filtered_df['Metric Name']

# Pivot so we can calculate difference per patient per metric
pivot_df = filtered_df.pivot_table(
    index=['Patient ID', 'RT_Metric'],
    columns='RT Dose Set',
    values='Metric Value'
).reset_index()

# Calculate absolute difference
pivot_df['Difference'] = np.abs(pivot_df['Plan2'] - pivot_df['Plan1'])


# Now create a boxplot grouped by RT_Metric
sns.boxplot(
    data=pivot_df,
    x='RT_Metric',
    y='Difference',
    ax=ax,
    width=0.7
)

# Labels and display
plt.ylabel(' ')    #('Absolute difference in dose [Gy]')
plt.xlabel('')
plt.title('')
plt.xticks(rotation=45)
plt.tight_layout()
plt.ylim((0,3.5))
#plt.savefig("T_default.pdf", format="pdf", bbox_inches="tight")
plt.show()



#------------------------------------------------------------------------------
#TABLE DOSIMETRIC MEASURES

grouped = df.groupby(['RT Dose Set', 'RT Structure', 'Metric Name']) # Group the data by 'RT Dose Set', 'RT Structure', and 'Metric Name'
# Calculate the mean of 'Metric Value' for each group
mean_values = grouped['Metric Value'].mean()
# Calculate the standard deviation of 'Metric Value' for each group
std_values = grouped['Metric Value'].std()

# Calculate the absolute errors between 'ReferencePlan' and 'PredictedPlan'
abs_errors = np.abs(mean_values['Plan1'] - mean_values['Plan2'])

# Calculate the standard deviation of the absolute errors
abs_errors_std = np.sqrt(std_values['Plan1']**2 + std_values['Plan2']**2)
#checked

# Combine MAE and standard deviation into a single DataFrame
results = pd.DataFrame({
    'MAE': abs_errors,
    'MAE_std': abs_errors_std
})


# Display the results
print(results)


# Group by dose set, structure, and metric
grouped = df.groupby(['RT Dose Set', 'RT Structure', 'Metric Name'])['Metric Value'].mean().unstack(level=0)

# Calculate absolute percentage difference
grouped['Absolute % Difference'] = 100 * np.abs(grouped['Plan2'] - grouped['Plan1']) / grouped['Plan1']

# Display or export
print(grouped[['Absolute % Difference']])


#also max and min. values
#absolute values

#df.query("RT Structure == 'CTVHR', 'CTVIR', 'CTVRES' and Metric Name == 'Drel(0.90)', 'Drel(0.98)' ")

#df.loc[df['Metric Value'], ['RT Structure', 'Metric Name']]



#---------------------------------------------------------------------- BIN PLOTS!!! 

# ------------- CTVHR ---------------
flt_df_CTVHR_D90 = df[(df['RT Structure'] == 'CTV HR') & (df['Metric Name'] == 'Drel(0.90)')]
pivot_df_CTVHR = flt_df_CTVHR_D90.pivot(index="Patient ID", columns="RT Dose Set", values="Metric Value")
pivot_df_CTVHR['Difference'] = np.abs(pivot_df_CTVHR['Plan2'] - pivot_df_CTVHR['Plan1'])

# ------------------ CTVIR ------------------
flt_df_CTVIR = df[df['RT Structure'] == 'CTV IR']
pivot_df_CTVIR = flt_df_CTVIR.pivot(index="Patient ID", columns="RT Dose Set", values="Metric Value")
pivot_df_CTVIR['Difference'] = np.abs(pivot_df_CTVIR['Plan2'] - pivot_df_CTVIR['Plan1'])

# ------------------ Plotting ------------------
plt.figure(figsize=(12, 6))

# CTVHR plot
plt.subplot(1, 2, 1)
plt.hist(pivot_df_CTVHR['Difference'].dropna(), bins=18, color="skyblue", edgecolor='black')
plt.xlabel("Difference (Predicted - Reference)")
plt.ylabel("Frequency")
plt.title("CTVHR: Predicted vs Reference")
plt.ylim(0,4)
plt.grid(True)
print(pivot_df_CTVIR['Difference'])

# CTVIR plot
plt.subplot(1, 2, 2)
plt.hist(pivot_df_CTVIR['Difference'].dropna(), bins=18, color="lightgreen", edgecolor='black')
plt.xlabel("Difference (Predicted - Reference)")
plt.ylabel("Frequency")
plt.title("CTVIR: Predicted vs Reference")
plt.ylim(0,4)
plt.grid(True)

plt.tight_layout()
plt.show()
