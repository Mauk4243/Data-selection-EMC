#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 14 13:01:35 2025

@author: ERASMUSMC+109098
"""
import os
import pydicom
from datetime import datetime
from collections import defaultdict
import csv

from sheet_helper_tag import find_dicom_file, extract_applicator_and_needlecount
from mr1 import find_mri_studies
from struc2 import find_structure_studies



def find_common_mri_and_structure_studies(mri_dict, structure_dict):
    combined_dict = defaultdict(list)
    for patient in mri_dict:
        if patient in structure_dict:
            for directory_study_id, dicom_study_id in structure_dict[patient]:
                if dicom_study_id in mri_dict[patient]:
                    combined_dict[patient].append((directory_study_id, dicom_study_id))
    return combined_dict

def find_image_type(study_path):
    images_path = os.path.join(study_path, "Images")
    if not os.path.exists(images_path):
        return None, None

    found_fiesta = False
    found_modality = None
    study_id = None

    for image_set in os.listdir(images_path):
        image_set_path = os.path.join(images_path, image_set)
        if not os.path.isdir(image_set_path):
            continue

        dicom_files = [f for f in os.listdir(image_set_path) if f.endswith('.dcm') or '.' not in f]
        if dicom_files:
            try:
                ds = pydicom.dcmread(os.path.join(image_set_path, dicom_files[0]), stop_before_pixels=True)
                study_id = getattr(ds, "StudyID", None) or getattr(ds, "StudyDescription", None)
                modality = ds.Modality
                if modality in ["MR", "CT"]:
                    found_modality = modality
                    if modality == "MR" and "FIESTA" in getattr(ds, "SeriesDescription", ""):
                        found_fiesta = True
            except Exception:
                continue

    if found_modality:
        if found_fiesta:
            return "MR FIESTA", study_id
        return found_modality, study_id
    return None, None


def generate_csv_with_study_info(base_path, combined_dict, output_csv):
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "PatientID", "FractionNumber", "StudyID", "DirectoryStudyID",
            "StudyInfo", "ImageType", "Applicator", "NeedleCount", "MeetCriteria", "Error"
        ])
# LIMIT --------------------------------------------------------> LIMIT 5 patients
        for patient_id in sorted(os.listdir(base_path)):
            patient_path = os.path.join(base_path, patient_id)
            if not os.path.isdir(patient_path):
                continue

            studies_path = os.path.join(patient_path, "Studies")
            if not os.path.isdir(studies_path):
                continue

            for directory_study_id in os.listdir(studies_path):
                study_path = os.path.join(studies_path, directory_study_id)
                if not os.path.isdir(study_path):
                    continue

                # Check of de studie voorkomt in combined_dict[patient_id]
                patient_combined = combined_dict.get(patient_id, [])
                in_combined = any(directory_study_id == dir_id or directory_study_id == dcm_id
                                  for dir_id, dcm_id in patient_combined)
                study_meets_criteria = "YES" if in_combined else "NO"

                dicom_file_found = False
                for root, dirs, files in os.walk(study_path):
                    for file in files:
                        if file.lower().endswith(".dcm") or "." not in file:
                            try:
                                dcm = pydicom.dcmread(os.path.join(root, file), stop_before_pixels=True)
                                study_id = dcm.StudyID if 'StudyID' in dcm else "?"
                                study_date_raw = dcm.StudyDate if 'StudyDate' in dcm else ""
                                study_time_raw = dcm.StudyTime if 'StudyTime' in dcm else ""

                                try:
                                    study_date = datetime.strptime(study_date_raw, "%Y%m%d").strftime("%d-%m-%Y")
                                except:
                                    study_date = "?"
                                try:
                                    study_time = datetime.strptime(study_time_raw.split(".")[0], "%H%M%S").strftime("%H:%M:%S")
                                except:
                                    study_time = "?"

                                study_uid = dcm.StudyInstanceUID if 'StudyInstanceUID' in dcm else "?"
                                study_info = f"{study_id}, {study_date} / {study_time}, {study_uid}"

                                image_type, _ = find_image_type(study_path)

                                dicom_path = find_dicom_file(base_path, patient_id, directory_study_id)
                                if dicom_path:
                                    extra_info = extract_applicator_and_needlecount(dicom_path)
                                    applicator = extra_info.get('Applicator', 'N/A')
                                    needle_count = extra_info.get('NeedleCount', 'N/A')
                                    fraction_number = extra_info.get('FractionNumber', 'N/A')
                                else:
                                    applicator = 'N/A'
                                    needle_count = 'N/A'
                                    fraction_number = 'N/A'

                                writer.writerow([
                                    patient_id, fraction_number, study_id, directory_study_id,
                                    study_info, image_type or "", applicator, needle_count, study_meets_criteria, ""
                                ])
                                dicom_file_found = True
                                break
                            except Exception as e:
                                print(f"  [Error reading file {file} in {directory_study_id}]: {e}")
                    if dicom_file_found:
                        break

                if not dicom_file_found:
                    print(f"  [No DICOM files found in {directory_study_id}]")

            

if __name__ == "__main__":
    base_path = "/home/research/MDBs/Archive/InstoradCervixBT/StorageTree/Patients"
    required_structures = {"ctv hr", "ctv ir", "oar bladder", "oar sigmoid", "oar rectum", "oar bowel"}

    
    mri_dict = find_mri_studies(base_path)
    structure_dict = find_structure_studies(base_path, required_structures)
    combined = find_common_mri_and_structure_studies(mri_dict, structure_dict)



    output_csv = "InstoradCervixBT_sheet.csv"
    generate_csv_with_study_info(base_path, combined, output_csv)

    print(f"CSV file '{output_csv}' has been created with the study information.")
