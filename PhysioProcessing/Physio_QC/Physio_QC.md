## Physiological Data QC
### These scripts allow you to check the quality of physiological data processing and subject participation on the level of 1) individual and 2) group
---
<br>

### Group plots of subject task performance
<br>1) Organize all of your subject files by pattern [A,B,C] and task [movie,breathing]<br>
<br>Output:
<br>Multiple .tsv files with each subject as a column & each datapoint as a row
```
python3 organize_files.py
```

<br>2) Plot the group figures (by calling the .tsv files you generated)
This script created the figures in our OHBM 2023 poster/abstract.
Output:
1) Ideal time series plots for the respiration and RVT data
2) Individual subject time series plots
3) Group plots that are averaged/median-ed across subjects
```
python3 group_figures.py
```

### (Optional) Checking whether the physiological data was processed correctly (from BIDS conversion to trimming stage)
Note: to run with multiple subjects in a sequential fashion, run the following code in terminal:
```
for s in sub-{01..25}; do echo $s; python3 file.py $s; done
```

<br>1) Check whether header/data integrity was maintained
1) from BIDS-conversion (originals) to file-trimming (trimmed)
2) across .tsv/.json file headers within 'Unprocessed'

<br>Note: This script was created to make sure the BIOPAC channels weren't switched prior to data acquisition on different sessions.
<br>Second Note: This script mainly pulls from /data/holnessmn/tmp, so the other files that weren't there [local on my Desktop], were checked prior.
```
python3 check_physios.py sub-??
```

<br>2) Overlay plots
<br>Output:
1) Plots the peak detection of the real time series
2) Overlays the real respiration/RVT breathing patterns (black) over the ideal A/B patterns (red)
```
python3 overlay_resp.py sub-??
```

<br>3) A script to check regressor calculation and plots
* Note: This script requires you to change the parameters by editing the script, but that allows you more freedom when testing things out (i.e., changing parameters for the RVT function which is highly-dependent on those parameters), in case you wanted to get a better RVT time series.
<br>Output:
1) Plots each regressor that you specify (can be any regressor in the 'RegressorModels' .tsv)
2) Preprocesses the respiration trace and calculates the RVT
3) overlays the real RVT over the ideal RVT
<br>I used this function to alter the time-window in order to get calculate the best RVT possible (one that would fit the ideal RVT).
```
python3 check_regressors.py sub-?? movie 1
python3 check_regressors.py sub-?? breathing 1
```