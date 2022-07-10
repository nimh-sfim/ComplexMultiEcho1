## Processing off-scanner data
---
<br>

### <b>Set up the directory structure</b> <br><br>
Define the subject ID
```
snum=$01; sbj=sub-${snum}
```

<br>Create the directories for the off-scanner and converted data
```sh
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
mkdir ${sbj}
cd ${sbj}
mkdir DataOffScanner Unprocessed
cd DataOffScanner
mkdir biopac DICOM psychopy
```
<br><br>

### <b>Move data to correct directories post-scan</b> <br><br>

<br>Create a document for scanning notes
```
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}
touch ${sbj}_ScanningNotes.txt
```

<br>Move PsychoPy logs & biopac .acq files to specified locations
```
cp -R *.log /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/psychopy/
cp -R *.acq /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}/DataOffScanner/biopac/
```

<br>Extract timing files for AFNI GLMs & check the stdout and log file
* <font size="1">Look at the stdout of that script to confirm that there's little to no difference between expected and actual trial times, the TR is <1ms of 1.5sec, and the participant's behavioral response rates show some level of attention.</font>
```
python [path to ComplexMultiEcho1 code repo]/PsychoPy/WordNonword/CreateEventTimesForGLM.py --sbjnum 3 --runnums 7 8 9 --rootdir /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
cat sub-??_CreateEventTimesForGLM.log
```

<br>Document DICOM scanner information which contains PII<br>
* <font size="1">README-Study.txt has PII in the following fields at the top: Subject Name, Subject ID, Study Date, Study ID, Accession Number and the scan date is in the repeated "Organized" field. Must be deidentified first!!!</font>
```
mv README-Study.txt /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/DICOM/
```

<br>Convert the DICOM files to BIDS LOCALLY<br>
<b>bespoke_cme.py</b>
```
python bespoke_cme.py --ignore 3 4 5 18 19 20 27 28 29 --start 2 ./DICOM ./tmp ${snum} > ${sbj}_dcm2nii_mapping.txt
```
<br><br>
Script `bespoke_cme.py` Options:
* ignore: ignored numbers are the "mr_00??" directories that should NOT be reconstructed
* start: DICOM volume at which to start

<br><br>
Additional Requirements:
* Data must be collected in the following order: MPRAGE, 3 runs of WNW, movie, breathing, movie, breathing
* Must have an up-to-date version of dcm2niix in the path (Note: dcm2niix_afni is shipped with Afni)
* Output is piped to `dcm2nii_mapping.txt` (Note: view this file to ensure DICOM was mapped correctly)

<br><br>
Transfer BIDS files to Biowulf
```
mv *.nii.gz /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/UnProcessed/
```

<br>Add slice timing information to the BIDS Nifti headers with [AddingSliceTiming.sh](AddingSliceTiming.sh)
```
AddingSliceTiming.sh ${sbj}
```

<br>Delete DICOM data with PII from computer
```
rm -r mr_00??
```

<br>Change the permissions for the Data directory
```sh
chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
```
<br><br>
### <b>Convert physiological BIOPAC Acqknowledge (.acq) files to BIDS format (.tsv.gz/.json)</b>

<br>see  `../PhysioProcessing/Physiological_Proc.md`
<br><br>s

```
acq2bidsphysio --infile file.acq --bidsprefix full/path/to/outdir/sub-01_task-wnw_acq-b_run-1_physio
```
