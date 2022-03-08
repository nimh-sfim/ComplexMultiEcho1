#!/bin/bash

# A script designed to run afni_proc.py for QA analyses of each subject after scanning
# Note: This does not align to a template.
# Note: There is one call to afni_proc for the 3 WordNonword runs.
#   The remaining runs are all processed separately and aligned to the same grid
#   Ideally, I'd only do one EPI to ANAT alignment, but this was messy without alignment
#   to a template. It was easier to just re-run this step.
#   It would also have been possible to run all movie and breathing runs with one
#   afni_proc, but I think using separate statements and swarming should be faster
# Note: 3dTshift only works if the correct slice timing information was added into
#  the .nii files (see AddingSliceTiming.sh)
#
# Note: -tcat_remove_first_trs 0 for now, but might want to adjust timing files later
# Note: Removing last 5 TRs because those are the noise scans


# The input is the subject ID (i.e. sub-01)
subj_id=$1


rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/QuickQAProcess
cd ${rootdir}
origdir='../../Unprocessed/'

mkdir WNW
mkdir ./WNW/stimfiles
cp ../DataOffScanner/psychopy/*.1D ./WNW/stimfiles/

if [ -f ${subj_id}_QA_WNW_sbatch.txt ]; then
    echo Deleting and recreating ${subj_id}_QA_WNW_sbatch.txt
    rm ${subj_id}_QA_WNW_sbatch.txt
fi
touch ${subj_id}_QA_WNW_sbatch.txt



echo '#!/bin/sh' > ${subj_id}_QA_WNW_sbatch.txt
echo "module load afni" >> ${subj_id}_QA_WNW_sbatch.txt
echo "source /home/handwerkerd/InitConda.sh" >> ${subj_id}_QA_WNW_sbatch.txt
echo "cd ${rootdir}/WNW" >> ${subj_id}_QA_WNW_sbatch.txt
echo \
 "afni_proc.py -subj_id $subj_id" \\$'\n' \
 "  -blocks despike tshift align volreg mask combine scale regress" \\$'\n' \
 "  -copy_anat ${origdir}anat/${subj_id}_T1w.nii" \\$'\n' \
 "  -anat_has_skull yes" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-1_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-1_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-1_part-mag_bold.nii" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-2_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-2_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-2_part-mag_bold.nii" \\$'\n' \
 "  -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-3_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-2_echo-3_part-mag_bold.nii" \\$'\n' \
 "      ${origdir}func/${subj_id}_task-wnw_run-3_echo-3_part-mag_bold.nii" \\$'\n' \
 "  -echo_times 13.44 31.7 49.96 -reg_echo 2" \\$'\n' \
 "  -tcat_remove_first_trs 0" \\$'\n' \
 "  -tcat_remove_last_trs 5" \\$'\n' \
 "  -align_opts_aea -cost lpc+ZZ -check_flip" \\$'\n' \
 "  -volreg_align_to MIN_OUTLIER -volreg_align_e2a" \\$'\n' \
 "  -combine_method m_tedana" \\$'\n' \
 "  -regress_censor_motion 0.2 -regress_censor_outliers 0.05" \\$'\n' \
 "  -regress_stim_times ./stimfiles/VisProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/FalVisProc_Times.1D" \\$'\n'  \
 "                     ./stimfiles/AudProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/FalAudProc_Times.1D" \\$'\n' \
 "                     ./stimfiles/Keypress_Times.1D" \\$'\n' \
 "  -regress_stim_labels VisWord FalVisWord AudWord FalAudWord Keypress" \\$'\n' \
   -regress_basis_multi \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(4,1\)\' \'BLOCK\(1,1\)\' \\$'\n' \
 "  -regress_opts_3dD -jobs 8" \\$'\n' \
   -gltsym \'SYM: +VisWord -FalVisWord\' -glt_label 1 Vis-FalVis \\$'\n' \
   -gltsym \'SYM: +AudWord -FalAudWord\' -glt_label 2 Aud-FalAud \\$'\n' \
   -gltsym \'SYM: +AudWord +VisWord -FalAudWord -FalVisWord\' -glt_label 3 Word-NonWord \\$'\n' \
   -gltsym \'SYM: -AudWord +VisWord -FalAudWord +FalVisWord\' -glt_label 4 Vis-Aud \\$'\n' \
   -gltsym \'SYM: +Keypress\' -glt_label 5 Keypress \\$'\n' \
 "  -regress_est_blur_epits -regress_est_blur_errts" \\$'\n' \
 "  -regress_apply_mot_types demean deriv" \\$'\n' \
 "  -regress_reml_exec -html_review_style pythonic" \\$'\n' \
 "  -execute" \
    >> ${subj_id}_QA_WNW_sbatch.txt

# Note: This assignment of a jobid from sbatch works on biowulf, but not elsewhere.
#   See: https://hpc.nih.gov/docs/job_dependencies.html
WNWjobID=$(sbatch --time 6:00:00 --cpus-per-task=8 --mem=24G --error=slurm_QA_WNW.e --output=slurm_${subj_id}_QA_WNW.o ${subj_id}_QA_WNW_sbatch.txt)



# Creating a separate swarm for each potential movie or breathing


if [ -f ${subj_id}_QA_moviebreath_swarm.txt ]; then
    echo Deleting and recreating ${subj_id}_QA_moviebreath_swarm.txt
    rm ${subj_id}_QA_moviebreath_swarm.txt
fi
touch ${subj_id}_QA_moviebreath_swarm.txt

for runid in  movie_run-1 movie_run-2 movie_run-3 breathing_run-1 breathing_run-2 breathing_run-3 ; do
  cd ${rootdir} 
  if [ -f ../Unprocessed/func/${subj_id}_task-${runid}_echo-1_part-mag_bold.nii ]; then
    mkdir $runid
    echo "module load afni; \\"  >> ${subj_id}_QA_moviebreath_swarm.txt
    echo "source /home/handwerkerd/InitConda.sh; \\" >> ${subj_id}_QA_moviebreath_swarm.txt
    echo "cd ${rootdir}/${runid}; \\" >> ${subj_id}_QA_moviebreath_swarm.txt
    echo \
        "afni_proc.py -subj_id $subj_id" \\$'\n' \
        "  -blocks despike tshift align volreg mask combine regress" \\$'\n' \
        "  -copy_anat ../WNW/${subj_id}.results/${subj_id}_T1w_ns+orig" \\$'\n' \
        "  -anat_has_skull no" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-1_part-mag_bold.nii" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-2_part-mag_bold.nii" \\$'\n' \
        "  -dsets_me_echo ${origdir}func/${subj_id}_task-${runid}_echo-3_part-mag_bold.nii" \\$'\n' \
        "  -echo_times 13.44 31.7 49.96 -reg_echo 2" \\$'\n' \
        "  -tcat_remove_first_trs 0" \\$'\n' \
        "  -tcat_remove_last_trs 5" \\$'\n' \
        "  -align_epi_ext_dset ../WNW/${subj_id}.results/final_epi_vr_base_min_outlier+orig" \\$'\n' \
        "  -align_opts_aea -cost lpc+ZZ  -check_flip"  \\$'\n' \
        "  -volreg_align_to MIN_OUTLIER -volreg_align_e2a"  \\$'\n' \
        "  -combine_method m_tedana" \\$'\n' \
        "  -regress_censor_motion 0.2 -regress_censor_outliers 0.05" \\$'\n' \
        "  -regress_opts_3dD -jobs 8" \\$'\n' \
        "  -regress_est_blur_epits -regress_est_blur_errts" \\$'\n' \
        "  -regress_apply_mot_types demean deriv" \\$'\n' \
        "  -regress_reml_exec -html_review_style pythonic" \\$'\n' \
        "  -execute" \
        >> ${subj_id}_QA_moviebreath_swarm.txt

  fi
done

moviebreath_jobID=$(swarm --time 6:00:00 --dependency=afterok:${WNWjobID} -g 24 -t 8 -m afni --merge-output --job-name moviebreath ${subj_id}_QA_moviebreath_swarm.txt)

cd $rootdir
if [ -f ${subj_id}_QA_jobhist_sbatch.txt ]; then
    echo Deleting and recreating ${subj_id}_QA_jobhist_sbatch.txt
    rm ${subj_id}_QA_jobhist_sbatch.txt
fi
touch ${subj_id}_QA_jobhist_sbatch.txt

echo '#!/bin/sh' >> ${subj_id}_QA_jobhist_sbatch.txt
echo "jobhist ${WNWjobID} > ${subj_id}_jobhist_results.txt " >> ${subj_id}_QA_jobhist_sbatch.txt
echo "jobhist ${moviebreath_jobID} >> ${subj_id}_jobhist_results.txt " >> ${subj_id}_QA_jobhist_sbatch.txt

sbatch --dependency=afterany:${moviebreath_jobID} --time 00:30:00 --cpus-per-task=1 --partition=norm,quick ${subj_id}_QA_jobhist_sbatch.txt


#     echo "cat_matvec -ONELINE ../WNW/${subj_id}.results/${subj_id}_T1w_al_junk_mat.aff12.1D -I  > ${subj_id}_epi_al_T1w_mat.aff12.1D; \\" >> ${subj_id}_QA_moviebreath_swarm.txt

#        "  -align_opts_aea -check_flip -Allineate_opts -1Dparam_apply ${rootdir}/${runid}/${subj_id}_epi_al_T1w_mat.aff12.1D" \\$'\n' \
#        "  -volreg_base_dset ../WNW/${subj_id}.results/vr_base_min_outlier+orig" \\$'\n' \
#        "  -Allineate_opts -master ../WNW/${subj_id}.results/final_epi_vr_base_min_outlier+orig"  \\$'\n' \
