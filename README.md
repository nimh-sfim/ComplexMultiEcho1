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
  - [DataCollectionGuide.md](DataCollectionGuide.md) is guide/reminder for our data collection procedure

## Organization & Processing Steps

1. [SettingUpDirectories.md](Conversion/SettingUpDirectories.md) is instructions for getting the MRI, biopac, & psychopy data from a scanning session to where it belongs. This (will) include:
    - DICOM to BIDS with Personally identifiable information removed
    - PsychoPy run logs to GLM regressors for AFNI & BIDS (and eventually other relevant reporting)
    - TODO: Biopac traces to BIDS-style cardiac, respiratory time series & TTL pulse times.

2. [AnatomicalProcessing.md](AnatomicalProcessing/AnatomicalProcessing.md) is instructions for running freesurfer
and generating the labelled ROIs-of-interest in EPI space.

3. [FMRI_processing.md](FMRI_processing/FMRI_processing.md) contains instructions for processing the fMRI data
starting with afni_proc.py

4. [Physiological_Proc.md](PhysioProcessing/Physiological_Proc.md) have instructions for processing and analyzing the raw BIDS-converted respiration and cardiac traces.

## Statistical Analysis

1. [ISC_Group_Analyses.md](GroupStatistics/MovieRespiration_Stats/ISC_Group_Analyses.md) show you how to perform Inter-subject correlations (ISC) on the Movie and Respiration runs.

2. [Statistics.md](GroupStatistics/WNW_Stats/Statistics.md) will show how to extract the Visual-Audio FisherZ statistics, Degrees of Freedom (DOF), and Contrast-to-Noise Ratio (CNR) maps for the Visual-Audio and Word-NonWord conditions.

3. [WNW_Group_Map_Generation.md](FMRI_processing/WNW_Group_Map_Generation.md) shows you how to generate the final Vis-Aud and Word-Nonword group maps across the GLMs.

## Visualization

1. [Visualizations_for_Manuscript.md](Visualizations_for_Manuscript.md) gives you instructions on how to re-generate all of the figures, visual QC checks, and where to locate the figures after they've been generated.
