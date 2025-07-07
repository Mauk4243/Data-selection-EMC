#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 15:21:49 2025

@author: ERASMUSMC+109098
"""
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('selected_p_info.csv')

# Keep only rows that mention Venezia or Geneva in the Applicator column
df = df[df["Applicator"].str.contains("Venezia|Geneva", na=False)]

# Extract just 'Venezia' or 'Geneva' into a new column
df["ApplicatorType"] = df["Applicator"].str.extract(r"(Venezia|Geneva)")


# Convert NeedleCount to numeric, coercing errors to NaN, DROP NAN INFO IN NEEDLECOUNT
df["NeedleCount"] = pd.to_numeric(df["NeedleCount"], errors='coerce')
# Drop rows where NeedleCount is NaN (i.e., non-numeric or missing)
df = df.dropna(subset=["NeedleCount"])


# Bin NeedleCount into categories
bins = [0, 4, 9, 23]
labels = ["0-4", "5-9", "10-23"]
df["NeedleBin"] = pd.cut(df["NeedleCount"], bins=bins, labels=labels, include_lowest=True)

# Combine the two stratification factors into one group
df["StrataGroup"] = df["ApplicatorType"] + "_" + df["NeedleBin"].astype(str)

#------------------------- MAKE SURE THAT ALL PATIENT STUDIES ARE IN THE SAME SET

# Assign each patient a single StrataGroup, *only* if all studies agree
def determine_strata_group(studies):
    unique_groups = studies["StrataGroup"].unique()
    if len(unique_groups) == 1:
        return unique_groups[0]
    else:
        return np.nan  # Not stratifiable

# Apply per patient
patient_strata = df.groupby("PatientID").apply(determine_strata_group).reset_index()
patient_strata.columns = ["PatientID", "StrataGroup"]

# Split into stratifiable and non-stratifiable
strat_df = patient_strata.dropna()
non_strat_df = patient_strata[patient_strata["StrataGroup"].isna()]

print("number strat patients:", (len(strat_df)))
print("number random distributed patients", (len(non_strat_df)))
#-------------------------


# Stratified split (train/test first)
train_ids, test_ids = train_test_split(
    strat_df, test_size=0.2, stratify=strat_df["StrataGroup"], random_state=42
) # Test = 0.2, so new set contains 80%

# Then split train further into train/val
train_final_ids, val_ids = train_test_split(
    train_ids, test_size=0.2, stratify=train_ids["StrataGroup"], random_state=42
) # Test = 0.2, so validation is 16% and training is 64%

# Convert to ID lists
train_patient_ids = train_final_ids["PatientID"].tolist()
val_patient_ids = val_ids["PatientID"].tolist()
test_patient_ids = test_ids["PatientID"].tolist()

# Shuffle non-stratifiable
remaining_ids = non_strat_df["PatientID"].tolist()
np.random.seed(42)
np.random.shuffle(remaining_ids)

n = len(remaining_ids)
test_cut = int(0.2 * n)
val_cut = int(0.2 * (n - test_cut))

test_patient_ids += remaining_ids[:test_cut]
val_patient_ids += remaining_ids[test_cut:test_cut + val_cut]
train_patient_ids += remaining_ids[test_cut + val_cut:]


# Map patients to their study indices
patient_to_studies = df.groupby("PatientID").apply(lambda x: x.index.tolist())

def get_study_indices(patient_list):
    indices = []
    for pid in patient_list:
        indices.extend(patient_to_studies[pid])
    return indices

# Get the final splits
train_indices = get_study_indices(train_patient_ids)
val_indices = get_study_indices(val_patient_ids)
test_indices = get_study_indices(test_patient_ids)



# Create the final DataFrames
df_train = df.loc[train_indices]
df_val = df.loc[val_indices]
df_test = df.loc[test_indices]

# First: clean up whitespace and newline issues in your key columns
for col in ['PatientID', 'StudyID']:
    df_test[col] = df_test[col].astype(str).str.strip()

# 1. Print number of studies (i.e. rows in test set)
print(f"Number of studies in test set: {len(df_test)}")
print("Patients in test:",len(test_patient_ids))

print(f"Number of studies in validation set: {len(df_val)}")
print("Patients in validation:",len(val_patient_ids))

print(f"Number of studies in training set: {len(df_train)}")
print("Patients in training:", len(train_patient_ids))


#-----------------------------------------------


def plot_distribution_with_percentages(dfs, column, title):
    for name, df in dfs.items():
        df["Set"] = name

    combined_df = pd.concat(dfs.values(), axis=0)

    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=combined_df, x=column, hue="Set")

    # Voeg percentage-labels toe binnen elke Set-groep
    for container in ax.containers:
        # Som van hoogtes binnen dezelfde hue (Set)
        total = sum([bar.get_height() for bar in container])
        labels = [f"{(bar.get_height() / total * 100):.1f}%" if bar.get_height() > 0 else "" for bar in container]
        
        for bar, label in zip(container, labels):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
            height / 2,
            label,
            ha="center",
            va="center",
            fontsize=10,
            color="white"
        )
   

        #ax.bar_label(container, labels=labels, label_type='center', fontsize=10, color='white')


    plt.title(title)
    plt.ylabel("Number of studies")
    plt.tight_layout()
    plt.show()

# Clean whitespace again
for subset in [df, df_train, df_val, df_test]:
    subset['NeedleBin'] = subset['NeedleBin'].astype(str).str.strip()
    subset['ApplicatorType'] = subset['ApplicatorType'].astype(str).str.strip()

# Create mapping of all sets
dfs = {
    "Full": df,
    "Train": df_train,
    "Validation": df_val,
    "Test": df_test
}

# Plot for NeedleBin
plot_distribution_with_percentages(dfs, "NeedleBin", " ") #"NeedleBin Distribution (% within set)")


# Plot for ApplicatorType
plot_distribution_with_percentages(dfs, "ApplicatorType", " ") #"ApplicatorType Distribution (% within set)")


#-----------------------------------------------
# Save StudyInfo for each set to text files
def save_study_info(df_subset, filename):
    with open(filename, 'w') as f:
        for info in df_subset["PatientID"]:
            info = info.replace('Patient_', '') #remove Patient_ 
            f.write(str(info) + '\n')
           

save_study_info(df_train, "strat_train_ID.txt")
save_study_info(df_val, "strat_val_ID.txt")
save_study_info(df_test, "strat_test_ID.txt")
