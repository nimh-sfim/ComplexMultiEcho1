# Initial setup of directories for a subject

These are instructions to make data from various sources all end up in appropriate places with consistent names

## Set up directory structure

Set a subject ID like `snum=$01; sbj=sub-${snum}`

```sh
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
mkdir ${sbj}
cd ${sbj}
mkdir DataOffScanner Unprocessed
cd DataOffScanner
mkdir biopac DICOM psychopy
```

## Other things to move after scan is done

- Create a document named `${sbj}_ScanningNotes.txt` in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}`

- Copy PsycoPy logs for all tasks to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/psychopy`
  - For the WordNonword task run script to extract timing files for AFNI GLMS running something like:

    `python [path to ComplexMultiEcho1 code repo]/PsychoPy/WordNonword/CreateEventTimesForGLM.py --sbjnum 3 --runnums 7 8 9 --rootdir /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/`

    Look at the stdout of that script to confirm that there's little to no difference between expect and actual trial times, the TR is <1ms of 1.5sec, and the participant's behavioral response rates show some level of attention. `sub-??_CreateEventTimesForGLM.log` containes more details about responses during each run

- Copy biopac data to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}/DataOffScanner/biopac`

- Put deidentified DICOM README-Study.txt in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/DICOM`
  - README-Study.txt has PII in the following fields at the top: Subject Name, Subject ID, Study Date, Study ID, Accession Number and the scan date is in the repeated "Organized" field

- On a local computer were the DICOMs with PII are downloaded run something like:
    `python bespoke_cme.py --ignore 3 4 5 18 19 20 27 28 29 --start 2 ../DataOffScanner/DICOM ./ ${snum} > ${sbj}_dcm2nii_mapping.txt`
  - The ignored numbers are the mr_00?? directories taht should not be reconstructed.
  - This script assumed the data are collected in the order: MPRAGE, 3 runs of WNW, movie, breathing, movie, breathing
  - If that's not the order, corrections may be necessary
  - This script requires having an up-to-date version of dcm2niix in the path (dcm2niix_afni is shipped with AFNI)
  - Output is piped to `dcm2nii_mapping.txt` That file should be viewed to make sure the mapping of DICOM to meaningful names was done correctly

- Move BIDSified data to /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/UnProcessed

- The BIDSified data need the slice timing information in the nii file headers. Run `AddingSliceTiming.sh ${sbj}` to add that information to the header

- Delete DICOM data with PII from computer

```sh
chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
```

## Converting BIOPAC .acq to .tsv.gz/.json

```sh
acq2bidsphysio --infile file.acq --bidsprefix full/path/to/outdir/sub-01_task-wnw_acq-b_run-1_physio
```
