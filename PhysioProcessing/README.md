# Processing Physiological Files

Going from AcqKnowledge BioPac files to BIDS-formatted Physiological (.tsv.gz/.json)):

### 1. Download acq2bidsphysio from GitHub
```
git clone https://github.com/cbinyu/bidsphysio.git
```

### 2. Extract acquisition times from 1st echo functionals
```
zsh acqtime.sh
```

### 3. Convert the .ACQ files using acq2bidsphysio
```
zsh conversions.sh
```

### 4. Make directory 'Originals' and mv all those converted files to that directory
```
mkdir 'Originals'; mv sub* Originals/
```

### 5. Process all the physiological files in the following order: 1) check, 2) trim, 3) overlay, 4) calc_regressors, 5) linearmodel
```
zsh Physio_Proc.sh 

Enter subject: (Ex: sub-01)
sub-01

Enter process to call: (Ex: trim)
check
```

### 6. Transfer the SigIC.txt files to Biowulf
```
zsh transport.sh
```
