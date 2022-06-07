# Instructions to process off-scanner data


## Set up directory structure

1. Set a subject ID
```
snum=$01; sbj=sub-${snum}
```

2. Create the directories for the off-scanner and converted data

```sh
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
mkdir ${sbj}
cd ${sbj}
mkdir DataOffScanner Unprocessed
cd DataOffScanner
mkdir biopac DICOM psychopy
```

## Moving data to correct directories post-scan:

1. Create a document for scanning notes
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}
touch ${sbj}_ScanningNotes.txt
```

2. Move PsychoPy logs & biopac .acq files to specified locations
```
cp -R *.log /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/psychopy/
cp -R *.acq /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}/DataOffScanner/biopac/
```

3. Extract timing files for AFNI GLMs & check the stdout and log file
(Note: Look at the stdout of that script to confirm that there's little to no difference between expected and actual trial times, the TR is <1ms of 1.5sec, and the participant's behavioral response rates show some level of attention.)
```
python [path to ComplexMultiEcho1 code repo]/PsychoPy/WordNonword/CreateEventTimesForGLM.py --sbjnum 3 --runnums 7 8 9 --rootdir /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
cat sub-??_CreateEventTimesForGLM.log
```

4. Document DICOM scanner information (contains PII)
(Note: README-Study.txt has PII in the following fields at the top: Subject Name, Subject ID, Study Date, Study ID, Accession Number and the scan date is in the repeated "Organized" field. Must be deidentified first!!!)
```
mv README-Study.txt /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/DICOM/
```

5. (LOCAL) Convert the DICOM files to BIDS
### bespoke_cme.py
```
python bespoke_cme.py --ignore 3 4 5 18 19 20 27 28 29 --start 2 ./DICOM ./tmp ${snum} > ${sbj}_dcm2nii_mapping.txt
```

Options:
-- ignore: ignored numbers are the "mr_00??" directories that should NOT be reconstructed
-- start: DICOM volume at which to start

Assumptions:
1. Data must be collected in the following order: MPRAGE, 3 runs of WNW, movie, breathing, movie, breathing
2. Must have an up-to-date version of dcm2niix in the path (Note: dcm2niix_afni is shipped with Afni)
3. Output is piped to `dcm2nii_mapping.txt` (Note: view this file to ensure DICOM was mapped correctly)

6. Transfer BIDS files to Biowulf
```
mv *.nii.gz /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/UnProcessed/
```

7. Add slice timing information to the BIDS Nifti headers
### AddingSliceTiming.sh
```
AddingSliceTiming.sh ${sbj}
```

8. Delete DICOM data with PII from computer
```
rm -r mr_00??
```

9. Change the permissions for the Data directory
```sh
chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
```

## Convert physiological BIOPAC Acqknowledge (.acq) files to BIDS format (.tsv.gz/.json)

see [Physiological_Proc.md]

```
acq2bidsphysio --infile file.acq --bidsprefix full/path/to/outdir/sub-01_task-wnw_acq-b_run-1_physio
```
