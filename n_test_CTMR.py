#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 14:32:18 2025

@author: ERASMUSMC+109098
"""
import zipfile
import os
import numpy as np
import matplotlib.pyplot as plt

# DP model

# GT
#zip_path = '/home/ERASMUSMC/109098/MatterhornDBs/Intermediate_results/StorageTree/Patients/Patient_R01225945/AnnConverter_shared_resolution_orig_slice/RTDose/1.2.826.0.1.3680043.2.968.3.5137936.2880913.1747918845.888.zip'

# DP prediction
#npy_path = '/home/ERASMUSMC/109098/MatterhornDBs/Intermediate_results/StorageTree/Patients/Patient_R01225945/AnnConverter_shared_resolution_orig_slice/RTDose/dose_HDUnet_Cervix_test_@8_HDUnet*.npy' 


def load_npy_from_zip(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.npy'):
                return np.load(os.path.join(root, file))
    return None

def load_npy_file(npy_path):
    return np.load(npy_path)

def visualize_axial_slice(volume, title):
    plt.imshow(volume[:, :, volume.shape[2] // 2], cmap='gray')
    plt.title(title)
    plt.axis('off')
    plt.show()
    print("volume:", volume.shape[0])


def main():
    zip_dose = '/home/ERASMUSMC/109098/MatterhornDBs/Intermediate_results/StorageTree/Patients/Patient_R01225945/AnnConverter_shared_resolution_orig_slice/RTDose/1.2.826.0.1.3680043.2.968.3.5137936.2880913.1747918845.888.zip'
    pred_dose_path = '/home/ERASMUSMC/109098/MatterhornDBs/Intermediate_results/StorageTree/Patients/Patient_R01225945/AnnConverter_shared_resolution_orig_slice/RTDose/dose_HDUnet_Cervix_test_@8_HDUnet*.npy'
    extract_dir = '/tmp/zip_extraction'

    gt_dose = load_npy_from_zip(zip_dose, extract_dir)
    if gt_dose is not None:
        visualize_axial_slice(gt_dose, 'Ground Truth Dose (Axial Slice)')
    else:
        print("Failed to load ground truth dose.")

    pred_dose = load_npy_file(pred_dose_path)
    if pred_dose is not None:
        visualize_axial_slice(pred_dose, 'Predicted Dose (Axial Slice)')
    else:
        print("Failed to load predicted dose.")
        
    difference = gt_dose - pred_dose
    if difference is not None:
         visualize_axial_slice(difference, 'differrence (Axial Slice)')
    else:
        print("Failed to load difference dose.")
        
      
    
    
    
    if gt_dose is not None and pred_dose is not None:
        print(f"Ground Truth shape: {gt_dose.shape}")
        print(f"Predicted shape: {pred_dose.shape}")

        if gt_dose.shape == pred_dose.shape:
            print("The dimensions match.")
        else:
            print("The dimensions do not match.")


if __name__ == "__main__":
    main()
    






'''
import zipfile
import os
import numpy as np
import matplotlib.pyplot as plt

# Image check
zip_path = '/home/ERASMUSMC/109098/MatterhornDBs/Intermediate_results/StorageTree/Patients/Patient_R00303290/AnnConverter_shared_resolution_orig_slice/RTStructure/1.2.826.0.1.3680043.2.968.3.5152272.2290514.1747918650.462_CTV HR.zip'
extract_dir = '/tmp/zip_extraction'

# Step 1: Open and list contents
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.printdir()
    zip_ref.extractall(extract_dir)

# Step 2: Find and load the .npy file
data = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.npy'):
            file_path = os.path.join(root, file)
            print(f"Found 3D data file: {file_path}")
            try:
                data = np.load(file_path)
                print(f"Loaded .npy file with shape: {data.shape}, dtype: {data.dtype}")
            except Exception as e:
                print(f"Failed to load .npy file: {e}")

# Step 3: Visualize if data was loaded
if data is not None:
    def visualize_slices(volume):
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        axes[0].imshow(volume[:, :, volume.shape[2] // 2], cmap='gray')
        axes[0].set_title('Axial View (z-axis)')
        axes[1].imshow(volume[:, volume.shape[1] // 2, :], cmap='gray')
        axes[1].set_title('Coronal View (y-axis)')
        axes[2].imshow(volume[volume.shape[0] // 2, :, :], cmap='gray')
        axes[2].set_title('Sagittal View (x-axis)')
        for ax in axes:
            ax.axis('off')
        plt.tight_layout()
        plt.show()

    visualize_slices(data)
else:
    print("No .npy file was loaded.")
'''