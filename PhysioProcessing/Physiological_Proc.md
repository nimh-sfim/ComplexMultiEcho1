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
```
zsh Physio_Proc.sh sub-??
Enter process to call:
convert
Enter task run:
wnw 1
Enter date:
2022-04-07T09_35_21
```

<br>Trim the physiological files with [Physio_Proc.sh](Physio_Proc.sh) and enter 'trim' at the 'process to call' prompt
```
zsh Physio_Proc.sh sub-??
Enter process to call:
trim
```

### <br>Calculate physiological regressors via NiPhlem
```
zsh Physio_Proc.sh sub-??
Enter process to call:
calc_regressors   
```

### <br>Fit the ICA components to the regressors with a Linear Model
<br>Call [run_FitReg2ICA.sh](run_FitReg2ICA.sh)
```
bash run_FitReg2ICA.sh
```
<font size="2">This file will run [FitReg2ICA.py](FitReg2ICA.py), which runs on a group of subjects listed in the file.<br> To see the methods used in the FitReg2ICA class obj, view [FitReg2ICAClass.py](FitReg2ICAClass.py).</font>
