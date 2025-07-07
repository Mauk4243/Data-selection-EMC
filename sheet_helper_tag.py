#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 14:32:18 2025

@author: ERASMUSMC+109098
"""
import os
import subprocess
import re

def find_dicom_file(base_path, patient, directory_study_id):
    treatment_plan_dir = os.path.join(base_path, patient, "Studies", directory_study_id, "TreatmentPlans")
    for root, dirs, files in os.walk(treatment_plan_dir):
        for file in files:
            if file.endswith(".dcm"):
                return os.path.join(root, file)
    return None

def extract_applicator_and_needlecount(dicom_path):
    tags = ['300b,100f', '300a,0282', '300a,0002']
    info = {}

    for dicomTag in tags:
        cmd = f'dcmdump -ev -q --print-indented --search {dicomTag} "{dicom_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        cmdout = result.stdout

        if dicomTag == '300b,100f':  # Applicator
            hexString = re.sub(r' # .*$','', cmdout.replace('(300b,100f) ?? ', ''))
            hexString = hexString.replace('...', '')
            if hexString:
                try:
                    info['Applicator'] = ''.join([chr(int(h, 16)) for h in hexString.split('\\')])
                except ValueError:
                    info['Applicator'] = "DecodeError"
            else:
                info['Applicator'] = "N/A"

        elif dicomTag == '300a,0282':  # NeedleCount
            string = re.sub(r' # .*$','', cmdout) 
            string = string.replace('[', '').replace(']', '')
            channel_num = string.split()[-1] if string else "No ChannelNumber found"
            try:
                info['NeedleCount'] = str(int(channel_num) - 3)
            except ValueError:
                info['NeedleCount'] = "N/A"
                
        elif dicomTag == '300a,0002': #fraction
            match = re.search(r'C\d+', cmdout)
            if match:
               info['FractionNumber'] = match.group(0)
            else:
               info['FractionNumber'] = match.group(0)
                
                

    return info
