
#/bin/sh

subj_id=$1

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat

cd $rootdir
sbatch --time=24:00:00 --cpus-per-task=8 --mem=16G --output=qwarp.out --error=qwarp.err \
    --wrap="cd ${rootdir}; module load afni; auto_warp.py -base MNI152_2009_template.nii.gz -input ${subj_id}_T1_masked.nii.gz -skull_strip_input no -skull_strip_base no"