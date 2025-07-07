#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 15:33:35 2025

@author: ERASMUSMC+109098
"""

import os
import pydicom
from collections import defaultdict


def is_mri_study(study_path):
    """Check if a study contains MRI images by examining DICOM headers."""
    images_path = os.path.join(study_path, "Images")
    if not os.path.exists(images_path):
        return False, None

    for image_set in os.listdir(images_path)[:]:  # Check first image set only
        image_set_path = os.path.join(images_path, image_set)
        dicom_files = [f for f in os.listdir(image_set_path) if f.endswith('.dcm') or '.' not in f]

        if dicom_files:
            try:
                ds = pydicom.dcmread(os.path.join(image_set_path, dicom_files[0]), stop_before_pixels=True)
                modality = getattr(ds, "Modality", "")
                study_id = getattr(ds, "StudyID", None) or getattr(ds, "StudyDescription", None) or os.path.basename(study_path)
                if modality in ("MR"): #and "FIESTA":
                    return True, study_id
            except Exception:
                continue
    return False, os.path.basename(study_path)

#def check_study_components(study_path):
#    """Check if the study has the required components: TreatmentPlans, StructureSets, and Images."""
#    required_components = {"TreatmentPlans", "StructureSets"} #, "Images"}
#    study_components = set(os.listdir(study_path))
    
#    if not required_components.issubset(study_components):
#        return False
    
#    for component in required_components:
#       component_path = os.path.join(study_path, component)
#        if not os.path.exists(component_path) or not os.listdir(component_path):
 #           return False
    
  #  return True


def find_mri_studies(base_path):
    mri_patients = defaultdict(list)
    for patient in os.listdir(base_path):
        patient_path = os.path.join(base_path, patient)
        studies_path = os.path.join(patient_path, "Studies")
        if os.path.exists(studies_path):
            for study in os.listdir(studies_path):
                study_path = os.path.join(studies_path, study)
                is_mri, study_id = is_mri_study(study_path)
                if is_mri: #and check_study_components(study_path):
                    mri_patients[patient].append(study_id)
    return mri_patients