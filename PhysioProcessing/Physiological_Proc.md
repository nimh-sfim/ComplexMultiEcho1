## Processing Physiological Files
---
<br>

### <br> Convert AcqKnowledge BioPac files to BIDS Physiologicals (.tsv.gz/.json)) & trim to functional length

<br>Download acq2bidsphysio from GitHub (locally or on Biowulf)
```
git clone https://github.com/cbinyu/bidsphysio.git
```

<br>Convert the .acq files to BIDS format (BIDSPhysio) with [Physio_Proc.sh](Physio_Proc.sh).
This call will extract the acquisition times from 1st echo functionals, which you can use to enter the corresponding date and time of acquisition for the .acq files. <bold>Enter 'module load jq' first.</bold>
<br>Note: This step is very manual, and detail- and time-intensive, so should be done after every scan.
```
bash Physio_Proc.sh sub-?? convert
Enter task run:
wnw 1
Enter date:
2022-04-07T09_35_21
```

<br>Trim the physiological files with [Physio_Proc.sh](Physio_Proc.sh) and enter 'trim' at the 'process to call' prompt. The trimmed files will be dropped in the 'Unprocessed/func/' directory.
```
bash Physio_Proc.sh sub-?? trim
```
<br>Note: you can trim for multiple subjects with the following command:
```
for s in sub-{01..25}; do bash Physio_Proc.sh $s trim; done
```

### <br>Calculate physiological regressors via NiPhlem
<br>This call will calculate the design matrix of NiPhlem and AFNI physiological regressors and will drop them in each subject-level directory called 'sub-??/Regressors/'.
```
bash Physio_Proc.sh sub-?? calc_regressors 
OR
for s in sub-{01..25}; do bash Physio_Proc.sh $s calc_regressors; done
```

### <br>Fit the ICA components to the regressors with a Linear Model
<br>Call [run_FitReg2ICA.sh](run_FitReg2ICA.sh)
```
bash run_FitReg2ICA.sh
```
<font size="2">This file will run [FitReg2ICA.py](FitReg2ICA.py), which runs on a group of subjects listed in the file.<br> To see the methods used in the FitReg2ICA class obj, view [FitReg2ICAClass.py](FitReg2ICAClass.py).</font>



### <br> Optional: plot the regressors to view them
<br>This call will enable you to view the plots of your Niphlem and AFNI regressors that you are including in your design matrix. These plots include: peak-detection, motion parameter plots (first derivative and demeaned), Retroicor, HRV/RVT plots, and WM/CSF plots. All of these plots are time-series.
```
bash Physio_Proc.sh sub-?? plot_regressors
OR
for s in sub-{01..25}; do bash Physio_Proc.sh $s plot_regressors; done
```

