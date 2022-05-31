# Processing Physiological Files

Step 1:
Convert AcqKnowledge BioPac files to BIDS-formatted Physiological (.tsv.gz/.json)) & Trim

```
# download acq2bidsphysio from GitHub
git clone https://github.com/cbinyu/bidsphysio.git
# extract acquisition times from 1st echo functionals
zsh acqtime.sh
# convert the .ACQ files locally using acq2bidsphysio
# Note: this step was done locally, but could be changed to do on Biowulf
zsh conversions.sh
# Make a directory "Originals" and mv all those converted files to that directory
mkdir 'Originals'; mv sub* Originals/
# Trim the physiological files
zsh Physio_Proc.sh      (process to call = trim)
# Transfer the trimmed physiological files to Biowulf
zsh transport.sh
```

Step 2:
Calculate regressors (on Biowulf)

```
zsh Physio_Proc.sh      (process to call = calc_regressors)
```

Step 3:
Run the Linear Model

```
python3 FitReg2ICA.py
```
