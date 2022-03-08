# dcm2niix doesn't place the multiband slice timing information in the nii file headers
# This is a problem because AFNI's 3dTshift looks for that information. This script
# pulls the slice timing information from the json files and add it to the nii headers


module load afni

subj_id=$1

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Unprocessed/func
niifiles=`ls *bold.nii`
for file in ${niifiles[@]}; do
  abids_tool.py -add_slice_times -input ${file}
done

