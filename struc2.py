#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 15:31:53 2025

@author: ERASMUSMC+109098
"""
import os
import pydicom
from concurrent.futures import ProcessPoolExecutor
import functools
from collections import defaultdict

def check_patient_studies(patient, base_path, required_structures):
    """Check all studies for a patient and return ones with all required structures."""
    patient_path = os.path.join(base_path, patient, "Studies")
    if not os.path.exists(patient_path):
        return []
    
    matching_studies = []
    
    for study in os.listdir(patient_path):
        study_path = os.path.join(patient_path, study)
        structure_set_path = os.path.join(study_path, "StructureSets")
        if not os.path.exists(structure_set_path):
            continue
        
        found_all_structures = False
        
        for struct_folder in os.listdir(structure_set_path):
            struct_folder_path = os.path.join(structure_set_path, struct_folder)
            
            for file in os.listdir(struct_folder_path):
                if not file.endswith(".dcm"):
                    continue
                    
                dicom_path = os.path.join(struct_folder_path, file)
                try:
                    # Read only necessary tags to improve performance
                    ds = pydicom.dcmread(dicom_path, specific_tags=['StructureSetROISequence', 'StudyID', 'StudyDescription'])
                    
                    if not hasattr(ds, "StructureSetROISequence"):
                        continue
                        
                    roi_names = {roi.ROIName.strip().lower() for roi in ds.StructureSetROISequence}
                    #if required_structures.issubset(roi_names):
                    if required_structures.issubset(roi_names):
                        # Get StudyID from DICOM or use folder name as fallback
                        dicom_study_id = getattr(ds, "StudyID", None) or getattr(ds, "StudyDescription", None)
                        directory_study_id = study
                        
                        matching_studies.append((patient, directory_study_id, dicom_study_id))
                        found_all_structures = True
                        break
                        
                except Exception:
                    continue
                    
            if found_all_structures:
                break
    
    return matching_studies


def find_structure_studies(base_path, required_structures):
    patient_dirs = [d for d in os.listdir(base_path) if d.startswith("Patient_")]
    all_matching_studies = []
    with ProcessPoolExecutor() as executor:
        check_func = functools.partial(check_patient_studies, base_path=base_path, required_structures=required_structures)
        results = executor.map(check_func, patient_dirs)
        for patient_studies in results:
            all_matching_studies.extend(patient_studies)
    study_dict = defaultdict(list)
    for patient, directory_study_id, dicom_study_id in all_matching_studies:
        study_dict[patient].append((directory_study_id, dicom_study_id))
    return study_dict

