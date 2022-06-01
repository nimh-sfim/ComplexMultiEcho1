# Instructions to process off-scanner data

## Set up directory structure

Set a subject ID: `snum=$01; sbj=sub-${snum}`

```sh
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
mkdir ${sbj}
cd ${sbj}
mkdir DataOffScanner Unprocessed
cd DataOffScanner
mkdir biopac DICOM psychopy
```

## Moving data to correct directories post-scan

1. Document scanner notes:

- Create a document named `${sbj}_ScanningNotes.txt` in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}`

2. Move PsychoPy logs & biopac .acq files to specified locations:

- Copy PsychoPy logs for all tasks to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/psychopy`
- For the WordNonword task:
  - To extract timing files for AFNI GLMS, run a similar command:

    `python [path to ComplexMultiEcho1 code repo]/PsychoPy/WordNonword/CreateEventTimesForGLM.py --sbjnum 3 --runnums 7 8 9 --rootdir /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/`

    Note: Look at the stdout of that script to confirm that there's little to no difference between expected and actual trial times, the TR is <1ms of 1.5sec, and the participant's behavioral response rates show some level of attention. `sub-??_CreateEventTimesForGLM.log` contains more details about responses during each run
- Copy biopac data to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}/DataOffScanner/biopac`

3. Document DICOM scanner information (contains PII):

- Put deidentified DICOM README-Study.txt in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}/DataOffScanner/DICOM`
- README-Study.txt has PII in the following fields at the top: Subject Name, Subject ID, Study Date, Study ID, Accession Number and the scan date is in the repeated "Organized" field

4. On a local computer where the DICOMs with PII are downloaded run a similar command:
    `python bespoke_cme.py --ignore 3 4 5 18 19 20 27 28 29 --start 2 ./DICOM ./tmp ${snum} > ${sbj}_dcm2nii_mapping.txt`

- Option parameters:
  - Ignore: ignored numbers are the mr_00?? directories that should not be reconstructed.
  - Start: DICOM volume at which to start?
- Data Requirements & Assumptions:
  - This script assumes the data are collected in the order: MPRAGE, 3 runs of WNW, movie, breathing, movie, breathing (If that's not the order, corrections may be necessary.)
  - This script requires having an up-to-date version of dcm2niix in the path (dcm2niix_afni is shipped with AFNI)
  - Output is piped to `dcm2nii_mapping.txt`. (That file should be viewed to make sure the mapping of DICOM to meaningful names was done correctly)

5. Transfer BIDS-ified files to Biowulf & add header information:

- Move BIDSified data to /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/UnProcessed
- Run `AddingSliceTiming.sh ${sbj}` to add slice timing information to the header. (The BIDSified data need the slice timing information in the nii file headers.)
- Delete DICOM data with PII from computer

```sh
chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
```

## Convert physiological BIOPAC Acqknowledge (.acq) files to BIDS format (.tsv.gz/.json)

(see Physiological_proc.README)

```sh
acq2bidsphysio --infile file.acq --bidsprefix full/path/to/outdir/sub-01_task-wnw_acq-b_run-1_physio
```
