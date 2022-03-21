# ComplexMultiEcho1

This project is part of a larger goal to improve fMRI data by thorough removal of noise and artifacts.
This specific study is examining ways to combine:

- Thermal noise reduction methods that take advantage of using complex (vs magnitude-only) fMRI
  data and noise scans (building off of NORDIC)
- Multi-echo fMRI denoising (building off of tedana)
- Cardiac and respiratory noise removal using respiratory and cardiac recordings

## Data

- fMRI data with magnitude + phase + multi-echo, and noise scan
- Respiration data from a belt around the chest and pulse from a pulse oximeter
- Tasks
  - [Visual vs Audio & Word vs Nonword task](PsychoPy/WordNonword/README_WordNonword.md) (3 8.5 min runs)
  - [Movie viewing runs](PsychoPy/MovieRespiration/README_MovieRespiration.md) with different patterns of cued breathing (2-3 7.5 min runs)
  - [Cued breathing "rest" runs](PsychoPy/MovieRespiration/README_MovieRespiration.md) where runs match the breathing patterns of a movie run (1-2 7.5 min runs)

## Organization & Processing Steps

1. [SettingUpDirectories.md](Conversion/SettingUpDirectories.md) is instructions for getting the MRI, biopac, & psychopy data from a scanning session to where it belongs. This (will) include:
    - DICOM to BIDS with Personally identifiable information removed
    - PsychoPy run logs to GLM regressors for AFNI & BIDS (and eventually other relevant reporting)
    - TODO: Biopac traces to BIDS-style cardiac, respiratory time series & TTL pulse times.

2. QA: Initial Processing of data to efficiently notice any issues. [WNW_afniproc.sh](InitialQAProcessing/WNW_afniproc.sh) is currently a bit hacky is a good starting point.
