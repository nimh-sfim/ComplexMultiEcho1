# Processing Physiological Files

Processing BIDS-formatted physiological files:

## 1. Trim files

```
python3 file_trimmer.py --filepath /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/sub-04_task-wnw_run-1_physio.tsv
rm *_physio.tsv 
```

## 2. Downsample physiological files (2000 Hz) to match PsychoPy log sampling rate (0.1 Hz)

```
python3 downsampler.py --filepath /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/.tsv
```

## 3. View breathing overlays

```
python3 overlay.py --filepath /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${sub}_task-breathing_run-1_resp_down.tsv --run_ideal A
```

## 4. transfer files for Linear Regression: ica_mixing.tsv & motion_demean.1D / motion_deriv.1D

Globus App

## 5. compute regressor models (minus 5 noise volumes: wnw: 340/345, movie/resp: 299)

```
python3 NiPhlem_regressors.py 
--tsv /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${sub}_task-wnw_run-1_physio.tsv.gz
--json /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${sub}_task-wnw_run-1_physio.json
--n_vols 340
--motion_demean /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/wnw/motion_demean.1D
--motion_deriv /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/wnw/motion_deriv.1D
--prefix RegressorModels_wnw_r1
```

## 6. compute Linear Regression

```
python3 Linear_Model.py 
--regressors /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/wnw/run1/RegressorModels_wnw_r1.tsv
--ica_mixing /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/wnw/run1/ica_mixing.tsv
--prefix LinearModel_wnw_r1
```

## 7. Call all the above with Physio_Proc.sh
```
zsh Physio_Proc.sh

Enter subject: (Ex: sub-01)
sub-01

Enter process to call: (Ex: trim)
check
```
