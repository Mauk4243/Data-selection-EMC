#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 12:35:19 2025

@author: ERASMUSMC+109098
"""
from mr1 import find_mri_studies
from struc2 import find_structure_studies
from collections import defaultdict
import os

def find_common_mri_and_structure_studies(mri_dict, structure_dict):
    combined_dict = defaultdict(list)
    for patient in mri_dict:
        if patient in structure_dict:
            for directory_study_id, dicom_study_id in structure_dict[patient]:
                if dicom_study_id in mri_dict[patient]:
                    combined_dict[patient].append((directory_study_id, dicom_study_id))
    return combined_dict

if __name__ == "__main__":
    base_path = "/home/research/MDBs/Archive/InstoradCervixBT/StorageTree/Patients"
    required_structures = {"ctv hr", "ctv ir", "oar bladder", "oar sigmoid", "oar rectum", "oar bowel"}

    mri_dict = find_mri_studies(base_path)
    structure_dict = find_structure_studies(base_path, required_structures)
    combined = find_common_mri_and_structure_studies(mri_dict, structure_dict)

    # Sort patients chronologically by ID (assuming R followed by date)
    sorted_patients = sorted(combined.keys(), reverse=False)

    print("Patients with MRI and all required structures (newest first):")
    for patient in sorted_patients:
        studies = sorted(combined[patient], key=lambda x: x[1])
        for directory_study_id, dicom_study_id in studies:
            print(f"{patient}: {directory_study_id} > {dicom_study_id}")

    print(f"\nTotal patients: {len(combined)}")
    print(f"Total matching studies: {sum(len(v) for v in combined.values())}")
