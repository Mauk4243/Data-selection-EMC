# Data-selection-EMC
Data selection scripts for my internship at EMC (Deep learning 3D dose prediction for cervical brachytherapy). 

1.	Sheet creating script with patient information for data selection. 
Main script: oefenen.py and uses sheet_helper_tag.py, mr1.py, struc2.py. 
2.	Selected patient print script (select properties you want to print the selected patients).
Main script: total3.py and uses mr1.py, struc2.py.
3.	Stratification script: distribution.py, distribution2.py, and stratification.py. 
4.	Script that compares the stratified total plan IDs with the plans created by BiCycle (in BiCycle1FxC1 folder in RT Studio): txt_test_pIDs.py and commonID-strat.py
5.	Checks the numpy/zip images created through instorad_evaluate: n_test_CTMR.py 
