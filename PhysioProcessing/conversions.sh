# conversions file for acq2bidsphysio

echo "Enter: subj task run date \nEx: sub-07 wnw 1 2022-04-07T09_35_21"
read sub task run date

acq2bidsphysio --infile ComplexMultiEcho${date}.acq --bidsprefix /Users/holnessmn/Desktop/BIDS_conversions/${sub}_physios/${sub}_task-${task}_run-${run}_physio
