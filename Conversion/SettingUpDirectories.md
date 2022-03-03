# Initial setup of directories for a subject

These are instructions to make data from various sources all end up in appropriate places with consistent names

## Set up directory structure

Set a subject ID like `snum=$01; sbj=sbj-${snum}`

```sh
{
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
mkdir ${sbj}
cd ${sbj}
mkdir DataOffScanner QuickQAProcess Unprocessed
cd DataOffScanner
mkdir biopac DICOM psychopy
}
```

## Other things to move after scan is done

- Copy biopac data to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/biopac`

- Copy PsycoPy logs for all tasks to `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/psychopy`

- Put deidentified DICOM README-Study.txt in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/DataOffScanner/DICOM`
  - README-Study.txt has PII in the following fields at the top: Subject Name, Subject ID, Study Date, Study ID, Accession Number and the scan date is in the repeated "Organized" field

- Create a document named `${sbj}_ScanningNotes.txt` in `/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}`

- On a local computer were the DICOMs with PII are downloaded run something like:
    `python bespoke_cme.py --ignore 3 4 5 18 19 20 27 28 29 --start 2 ../DataOffScanner/DICOM ./ ${snum} > dcm2nii_mapping.txt`
  - The ignored numbers are the mr_00?? directories taht should not be reconstructed.
  - This script assumed the data are collected in the order: MPRAGE, 3 runs of WNW, movie, breathing, movie, breathing
  - If that's not the order, corrections may be necessary
  - This script requires having an up-to-date version of dcm2niix in the path (dcm2niix_afni is shipped with AFNI)
  - Output is piped to `dcm2nii_mapping.txt` That file should be viewed to make sure the mapping of DICOM to meaningful names was done correctly

- Move BIDSified data to /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/${sbj}/Data/UnProcessed

- Delete DICOM data with PII from computer

```sh
{
chgrp -R SFIM /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
chmod -R 2770 /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
}
```
