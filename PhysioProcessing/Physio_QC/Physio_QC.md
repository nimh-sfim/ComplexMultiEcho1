## Physiological Data QC
### These scripts allow you to check the quality of physiological data processing and subject participation on the level of 1) individual and 2) group
---
<br>

### Visually checking the quality of subject task performance (on a group-level)
* These scripts will allow you to QC subject participation on a group-level

<br>1) Organize all of your subject files by pattern [A,B,C] and task [movie,breathing]<br>
<br>Output:
<br>Multiple .tsv files with each subject as a column & each datapoint as a row
```
python3 organize_files.py
```

<br>2) Plot the group figures (by calling the .tsv files you generated)

Output:
1) Ideal time series plots for the respiration and RVT data
2) Individual subject time series plots
3) Group plots that are averaged/median-ed across subjects
```
python3 group_figures
```

### (Optional) Checking whether your physiological data was processed correctly (from BIDS conversion to trimming stage)
* These scripts are meant to QC the data on a subject-level (for closer inspection)

<br>1) Check whether header/data integrity was maintained
1) from BIDS-conversion (originals) to file-trimming (trimmed)
2) across .tsv/.json file headers within 'Unprocessed'

<br>Note: This script was created since BIOPAC channels can often be switched prior to data acquisition (because other researchers are using the same equipment). Therefore, it's important to visually check whether the correct headers are being maintained during file trimming and post-transportation across directories, since this may potentially introduce issues in data integrity.
```
python3 check_physios.py sub-??
```

<br>2) (Old user-intensive & rough script) -> would only recommend after running the scan and you'd like to check if that partipant was following the task
* This script requires you to open the 'ScanningNotes.txt' for that subject, check the respiration pattern per task/run, and only then will it produce a plot for you.

<br>Output:
1) Plots the peak detection of the real time series
2) Overlays the real respiration/RVT breathing patterns (black) over the ideal A/B patterns (red)

```
python3 overlay_resp.py sub-??
```

<br>3) Exploratory script to check regressor calculation and plots
* Note: This script requires you to change the parameters by editing the script, but that allows you more freedom when testing things out (i.e., changing parameters for the RVT function which is highly-dependent on those parameters), in case you wanted to get a better RVT time series.

<br>Output:
1) Plots each regressor that you specify (can be any regressor in the 'RegressorModels' .tsv)
2) Preprocesses the respiration trace and calculates the RVT

<br>Example of functions and their editable parameters:
<br>def regressor_length(regressor:str) -> regressor_length('resp_rvt')</n>
<br>def preproc_rvt(tr:float,physio_rate:int,n_vols:int,time_window:int,low_pass:float,high_pass:float) -> preproc_rvt(tr=1.5,physio_rate=2000,n_vols=299,time_window=6,low_pass=0.5,high_pass=0.1)

```
python3 check_regressors.py sub-?? movie_run-1
python3 check_regressors.py sub-?? breathing_run-1
```