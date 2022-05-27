# Get acquisition times from func Unprocessed data

echo "Enter: subj task run \nEx: sub-07 wnw 1"
read sub task run

root=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sub}/Unprocessed/func/
jq .AcquisitionTime $root${sub}_task-${task}_run-${run}_echo-1_part-mag_bold.js$



