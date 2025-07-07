#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 14:32:18 2025

@author: ERASMUSMC+109098
"""
import os

# Base path to patient directories
base_path = "/home/ERASMUSMC/109098/MatterhornDBs/BiCycler1Fx1C1/StorageTree/Patients"

# Stratified patient ID files
strat_train_list = "strat_train_ID.txt"
strat_val_list = "strat_val_ID.txt"
strat_test_list = "strat_test_ID.txt"

# Get all available patient directories (without 'Patient_' prefix)
patient_dirs = [
    d.replace('Patient_', '') 
    for d in sorted(os.listdir(base_path)) 
    if d.startswith("Patient_") and os.path.isdir(os.path.join(base_path, d))
]

# Load stratified patient IDs
def load_ids(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

strat_train_ids = load_ids(strat_train_list)
strat_val_ids = load_ids(strat_val_list)
strat_test_ids = load_ids(strat_test_list)

# Find common IDs
common_train_ids = sorted(set(patient_dirs) & set(strat_train_ids))
common_val_ids = sorted(set(patient_dirs) & set(strat_val_ids))
common_test_ids = sorted(set(patient_dirs) & set(strat_test_ids))

# Save to new files
def save_ids(ids, filename):
    with open(filename, 'w') as f:
        for pid in ids:
            f.write(pid + '\n')

save_ids(common_train_ids, "available_strat_train_ID.txt")
save_ids(common_val_ids, "available_strat_val_ID.txt")
save_ids(common_test_ids, "available_strat_test_ID.txt")

# Print summary
print("Total patients in RTStudio:", len(patient_dirs))
print("Original stratified training IDs:", len(strat_train_ids))
print("Original stratified validation IDs:", len(strat_val_ids))
print("Original stratified test IDs:", len(strat_test_ids))
print("Available training IDs:", len(common_train_ids))
print("Available validation IDs:", len(common_val_ids))
print("Available test IDs:", len(common_test_ids))
