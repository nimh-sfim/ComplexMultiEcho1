# GroupMask Creation File

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
GroupDir=${rootdir}GroupResults/GroupMaps/
cd ${rootdir}GroupResults/GroupISC/

if ! [ -d group_mask/ ]; then
    mkdir group_mask/
fi
out=group_mask/

tot_subjs=23

# Creating a binarized mask for the group statistics:

for sub in {01..23}; do
    # use the OC data (masked) & first brick as a starting point & change all data to 1's (bool(x)=True=1), no data to 0's (bool(x)=False=0) -> binarize
    3dcalc -a ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/pb0?.sub-${sub}.r01.combine+orig.HEAD'[0]' -expr 'notzero(a)' -prefix ${out}sub-${sub}_mask.nii.gz
done

# gather individual binarized subject masks
masks=`ls ${out}sub*_mask.nii.gz`

# Concatenate all of the created subject masks
3dTcat -prefix ${out}Concatenated_sbj_masks_All.nii.gz $masks
# add all of the masks together to create a group mask
3dTstat -sum -prefix ${out}Group_mask_sum.nii.gz Concatenated_sbj_masks_All.nii.gz
# binarize the group mask by substracting the sum [of 1's] of the (total num of subjs - 1) = (22) from the existing value, which should be the sum of 1's * tot_subjs (23)
# thus if done correctly, inside the mask should be 1's (23-22=1, which is > 0), and outside the mask should be 0's (0 if x <= 0)
3dcalc -a Group_mask_sum.nii.gz -expr 'ispositive(a-(${tot_subjs}-1))' -prefix ${out}Group_Mask.nii.gz

echo "The final group mask is 'Group_Mask.nii.gz' "

# Apply each subject's mask to its own 2nd echo data - native
second_echoes=`ls ${rootdir}sub-??/afniproc_orig/*_run-*/sub-??.results/pb0?.sub-??.r01.e02.volreg+orig.HEAD`

# put the masked files right back in their home afni directory
for e2 in $second_echoes; do
    filename=`basename $e2`
    dirname=`dirname $e2`
    sub=${filename:9:2}
    3dTstat -mask ${out}sub-${sub}_mask.nii.gz -prefix ${dirname}${filename::-10}_masked.nii.gz
done

# sbatch time=06:00:00 GroupMask_MH.sh