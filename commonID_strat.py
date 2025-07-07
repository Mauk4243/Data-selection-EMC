#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 15:07:53 2025

@author: ERASMUSMC+109098
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load full dataset
df = pd.read_csv("selected_p_info.csv")

# Load available patient IDs for each subset
def load_ids(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

available_train_ids = load_ids("available_strat_train_ID.txt")
available_val_ids = load_ids("available_strat_val_ID.txt")
available_test_ids = load_ids("available_strat_test_ID.txt")

# Preprocess function with added filter: FractionNumber == 1
def preprocess_subset(df, available_ids, name=""):
    print(f"\n▶ Preprocessing {name} set with {len(available_ids)} IDs")
    
    subset = df[df["PatientID"].str.replace("Patient_", "").isin(available_ids)].copy()
    print(f"✓ Matched {len(subset)} rows with IDs in {name} set")

    subset = subset[subset["FractionNumber"] == 1]
    print(f"✓ {len(subset)} rows remaining after filtering for FractionNumber == 1")

    subset = subset.dropna(subset=["Applicator"])
    subset = subset[subset["Applicator"].str.contains("Venezia|Geneva", na=False)].copy()
    subset["ApplicatorType"] = subset["Applicator"].str.extract(r"(Venezia|Geneva)")
    subset["NeedleCount"] = pd.to_numeric(subset["NeedleCount"], errors="coerce")
    subset = subset.dropna(subset=["NeedleCount"])
    
    bins = [0, 4, 9, 23]
    labels = ["0-4", "5-9", "10-23"]
    subset["NeedleBin"] = pd.cut(subset["NeedleCount"], bins=bins, labels=labels, include_lowest=True)
    subset["StrataGroup"] = subset["ApplicatorType"] + "_" + subset["NeedleBin"].astype(str)
    
    print(f"✓ {len(subset)} rows remaining after full preprocessing for {name}")
    return subset

# Apply to all subsets
df_train = preprocess_subset(df, available_train_ids, "Training")
df_val = preprocess_subset(df, available_val_ids, "Validation")
df_test = preprocess_subset(df, available_test_ids, "Test")

# Plotting function with actual counts
def plot_distribution_with_counts(df, column, title, order=None):
    plt.figure(figsize=(10, 6))
    ax = sns.countplot(data=df, x=column, order=order)
    
    for p in ax.patches:
        count = p.get_height()
        ax.annotate(f"{count}", (p.get_x() + p.get_width() / 2., count / 2),
                    ha='center', va='center', fontsize=10, color='white')
    
    plt.title(title)
    plt.ylabel("Number of studies")
    plt.tight_layout()
    plt.show()

# Define consistent orderings
needle_bin_order = ["0-4", "5-9", "10-23"]
applicator_type_order = ["Venezia", "Geneva"]
strata_group_order = [f"{app}_{bin}" for app in applicator_type_order for bin in needle_bin_order]

# Plot distributions
for subset, name in zip([df_train, df_val, df_test], ["Training", "Validation", "Test"]):
    plot_distribution_with_counts(subset, "NeedleBin", f"NeedleBin Distribution ({name} Set)", order=needle_bin_order)
    plot_distribution_with_counts(subset, "ApplicatorType", f"ApplicatorType Distribution ({name} Set)", order=applicator_type_order)
    plot_distribution_with_counts(subset, "StrataGroup", f"StrataGroup Distribution ({name} Set)", order=strata_group_order)
