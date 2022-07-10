## Processing Physiological Files
---
<br>

### <br> Convert AcqKnowledge BioPac files to BIDS Physiologicals (.tsv.gz/.json)) & trim to functional length

<br>Download acq2bidsphysio from GitHub (locally or on Biowulf)
```
git clone https://github.com/cbinyu/bidsphysio.git
```

<br>Extract acquisition times from 1st echo functionals with [acqtime.sh](acqtime.sh)
```
zsh acqtime.sh
```

<br>Convert the .ACQ files using acq2bidsphysio with [conversions.sh](conversions.sh)
<br><font size="1">If you decide to run this on Biowulf, you'll need to edit the paths in the file.</font>
```
zsh conversions.sh
```

<br>Make a directory "Originals" and move all those converted files to that directory
```
mkdir 'Originals'; mv sub* Originals/
```

<br>Trim the physiological files with [Physio_Proc.sh](Physio_Proc.sh) and enter 'trim' at the 'process to call' prompt
<br><font size="1">Again, if you decide to run this on Biowulf, you'll need to edit the paths to Biowulf for the "trim" function.</font>
```
zsh Physio_Proc.sh
```

<br>Transfer the trimmed physiological files to Biowulf with [transport.sh](transport.sh)
<br><font size="1">This step is only necessary if you trimmed & converted the files locally,and you'll need to modify the script to your local directories.</font>
```
zsh transport.sh
```


### <br>Calculate regressors 
<br>Call [Physio_Proc.sh](Physio_Proc.sh) and enter 'calc_regressors' at the 'process to call' prompt
```
zsh Physio_Proc.sh      
```

### <br>Fit the ICA components to the regressors with a Linear Model
<br>Call [run_FitReg2ICA.sh](run_FitReg2ICA.sh)
<br><font size="1">This file will run [FitReg2ICA.py](FitReg2ICA.py).</font>
```
bash run_FitReg2ICA.sh
```