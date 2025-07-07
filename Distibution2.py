#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 12:34:36 2025

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

# Extract just 'Venezia' or 'Geneva' into a new column, MAKING NEW COLUMN
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

# THIS MAKES SURE THAT IF A PATIENT HAS CHARACTERISTICS THAT ARE NOT STRATIFIABLE HE BELONGS IN THE RANDOM DISTRIBUTED GROUP. 

#------------------------------------------------------------------------------
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

# Create the final DataFrames !!!
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

# Getting the StudyIDs from the final DATA frames (unique does not matter, every studyID is)
train_study_ids = df_train["StudyID"].unique().tolist()
val_study_ids = df_val["StudyID"].unique().tolist()
test_study_ids = df_test["StudyID"].unique().tolist()


# Assuming you already have these lists and the full DataFrame `df`
# train_patient_ids, val_patient_ids, test_patient_ids
# df should include columns: 'PatientID' and 'ApplicatorType'

'''
def count_applicator_types(study_ids, df):
   applicator_counts = df[df["StudyID"].isin(study_ids)]["ApplicatorType"].value_counts()
   geneva_count = applicator_counts.get("Geneva", 0)
   venezia_count = applicator_counts.get("Venezia", 0)
   return geneva_count, venezia_count
'''

def count_applicator_types(patient_ids, df):
    applicator_counts = df[df["PatientID"].isin(patient_ids)]["ApplicatorType"].value_counts()
    geneva_count = applicator_counts.get("Geneva", 0)
    venezia_count = applicator_counts.get("Venezia", 0)
    return geneva_count, venezia_count


# Count Geneva and Venezia patients in each split
geneva_train, venezia_train = count_applicator_types(train_patient_ids, df)
geneva, venezia_val = count_applicator_types(val_patient_ids, df)
geneva_test, venezia_test = count_applicator_types(test_patient_ids, df)

'''
# Count Geneva and Venezia patients in each split
geneva_train, venezia_train = count_applicator_types(train_study_ids, df)
geneva_val, venezia_val = count_applicator_types(val_study_ids, df)
geneva_test, venezia_test = count_applicator_types(test_study_ids, df)
'''

# Calculate ratios
ratio_train = geneva_train / venezia_train if venezia_train != 0 else 0
ratio_val = geneva_val / venezia_val if venezia_val != 0 else 0
ratio_test = geneva_test / venezia_test if venezia_test != 0 else 0

# Plotting
splits = ['Train', 'Validation', 'Test']
ratios = [ratio_train, ratio_val, ratio_test]

plt.figure(figsize=(8, 5))
plt.bar(splits, ratios, color=['blue', 'orange', 'green'])
plt.xlabel('Data Split')
plt.ylabel('Geneva/Venezia Ratio')
plt.title('Geneva to Venezia Ratio in Each Data Split')
plt.ylim(0, max(ratios) + 0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

print("Train - Geneva:", geneva_train, "Venezia:", venezia_train)
print("Validation - Geneva:", geneva_val, "Venezia:", venezia_val)
print("Test - Geneva:", geneva_test, "Venezia:", venezia_test)


# Add this at the end of your current script

# ------------------ Needle Bin Ratio Analysis ------------------

def count_needle_bins(patient_ids, df):
    needle_counts = df[df["PatientID"].isin(patient_ids)]["NeedleBin"].value_counts()
    bin_0_4 = needle_counts.get("0-4", 0)
    bin_5_9 = needle_counts.get("5-9", 0)
    bin_10_23 = needle_counts.get("10-23", 0)
    return bin_0_4, bin_5_9, bin_10_23

# Count needle bins in each split
bin_0_4_train, bin_5_9_train, bin_10_23_train = count_needle_bins(train_patient_ids, df)
bin_0_4_val, bin_5_9_val, bin_10_23_val = count_needle_bins(val_patient_ids, df)
bin_0_4_test, bin_5_9_test, bin_10_23_test = count_needle_bins(test_patient_ids, df)

# Calculate ratios
ratio_5_9_to_0_4_train = bin_5_9_train / bin_0_4_train if bin_0_4_train != 0 else 0
ratio_5_9_to_0_4_val = bin_5_9_val / bin_0_4_val if bin_0_4_val != 0 else 0
ratio_5_9_to_0_4_test = bin_5_9_test / bin_0_4_test if bin_0_4_test != 0 else 0

ratio_5_9_to_10_23_train = bin_5_9_train / bin_10_23_train if bin_10_23_train != 0 else 0
ratio_5_9_to_10_23_val = bin_5_9_val / bin_10_23_val if bin_10_23_val != 0 else 0
ratio_5_9_to_10_23_test = bin_5_9_test / bin_10_23_test if bin_10_23_test != 0 else 0

# Plotting
splits = ['Train', 'Validation', 'Test']
ratios_5_9_to_0_4 = [ratio_5_9_to_0_4_train, ratio_5_9_to_0_4_val, ratio_5_9_to_0_4_test]
ratios_5_9_to_10_23 = [ratio_5_9_to_10_23_train, ratio_5_9_to_10_23_val, ratio_5_9_to_10_23_test]

plt.figure(figsize=(12, 6))

# First plot: ratio of 5-9 needles to 0-4 needles
plt.subplot(1, 2, 1)
plt.bar(splits, ratios_5_9_to_0_4, color=['blue', 'orange', 'green'])
plt.xlabel('Data Split')
plt.ylabel('Ratio')
plt.title('Ratio of 5-9 Needles to 0-4 Needles')
plt.ylim(0, max(ratios_5_9_to_0_4) + 0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Second plot: ratio of 5-9 needles to 10-23 needles
plt.subplot(1, 2, 2)
plt.bar(splits, ratios_5_9_to_10_23, color=['blue', 'orange', 'green'])
plt.xlabel('Data Split')
plt.ylabel('Ratio')
plt.title('Ratio of 5-9 Needles to 10-23 Needles')
plt.ylim(0, max(ratios_5_9_to_10_23) + 0.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

# Optional: print raw counts
print("Train - 0-4:", bin_0_4_train, "5-9:", bin_5_9_train, "10-23:", bin_10_23_train)
print("Validation - 0-4:", bin_0_4_val, "5-9:", bin_5_9_val, "10-23:", bin_10_23_val)
print("Test - 0-4:", bin_0_4_test, "5-9:", bin_5_9_test, "10-23:", bin_10_23_test)
