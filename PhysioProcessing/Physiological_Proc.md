# Processing Physiological Files

Note: This directory is the only directory with "Zsh" scripts

## Convert AcqKnowledge BioPac files to BIDS-formatted Physiological (.tsv.gz/.json)) & Trim

1. Download acq2bidsphysio from GitHub (locally or on Biowulf)
```
git clone https://github.com/cbinyu/bidsphysio.git
```

2. Extract acquisition times from 1st echo functionals
### acqtime.sh
```
zsh acqtime.sh
```

3. Convert the .ACQ files using acq2bidsphysio
### conversions.sh
```
zsh conversions.sh
```
{Note: If you decide to run this on Biowulf, you'll need to edit the paths in the file.}

4. Make a directory "Originals" and move all those converted files to that directory
```
mkdir 'Originals'; mv sub* Originals/
```

5. Trim the physiological files
### Physio_Proc.sh (process to call = trim)
```
zsh Physio_Proc.sh
```
{Note: You'll also need to change these paths to Biowulf for the "trim" function.}

6. Transfer the trimmed physiological files to Biowulf
### transport.sh
```
zsh transport.sh
```
{Note: This step is ONLY necessary if you trimmed & converted the files locally.)


## Calculate regressors
### Physio_Proc.sh (process to call = calc_regressors)
```
zsh Physio_Proc.sh      
```

## Run the Linear Model (to fit the ICA components to the regressors)
### run_FitReg2ICA.sh
```
bash run_FitReg2ICA.sh
```
{Note: This file will run `FitReg2ICA.py`.}