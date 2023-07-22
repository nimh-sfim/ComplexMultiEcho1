# For a given subject, make a directory for the GLM outputs and create a swarm file to run a bunch of GLMs

sbj=$1

########################################
#     WNW/Movie/Breathing analyses     #
########################################

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
if ! [ -d './GLMs']; then
  mkdir GLMs; else echo "GLM directory for subject ${sbj} exists"
fi
cd GLMs

if [ -f ${sbj}_rest_GLM_sbatch.txt ]; then
  echo Deleting and recreating ${sbj}_rest_GLM_sbatch.txt
  rm ${sbj}_rest_GLM_sbatch.txt
fi

touch ${sbj}_rest_GLM_sbatch.txt

rootdir=`pwd`

rest_ted_dir=tedana_v23_c70_kundu_r01;
task_ted_dir=tedana_v23_c70_kundu_r0?;

############################################
# 2nd echo with Mot/CSF (regular) #
############################################
cat << EOF > ${sbj}_GLM_sbatch_2nd_echo.txt
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_wnw \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task wnw
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-1/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_movie_run-1 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-2/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_movie_run-2 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-3/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_movie_run-3 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-1/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_breathing_run-1 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-2/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_breathing_run-2 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-3/${sbj}.results/ second_echo_mot_csf_v23_c70_kundu_breathing_run-3 \
    --inputfiles pb0?.${sbj}.r0?.e02.volreg_masked.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
EOF

############################################
# OC with Mot/CSF (regular) #
############################################
cat << EOF > ${sbj}_GLM_sbatch_OC.txt
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_wnw \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task wnw
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-1/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_movie_run-1 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-2/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_movie_run-2 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-3/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_movie_run-3 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-1/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_breathing_run-1 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-2/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_breathing_run-2 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-3/${sbj}.results/ optimally_combined_mot_csf_v23_c70_kundu_breathing_run-3 \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --include_motion --include_CSF \
    --task rest
EOF

############################################
# Tedana Regression with Mot/CSF (regular) #
############################################
cat << EOF > ${sbj}_GLM_sbatch_ted.txt
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_wnw \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task wnw
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-1/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_movie_run-1 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-2/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_movie_run-2 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-3/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_movie_run-3 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-1/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_breathing_run-1 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-2/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_breathing_run-2 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-3/${sbj}.results/ tedana_mot_csf_v23_c70_kundu_breathing_run-3 \
    --inputfiles ${task_ted_dir}/desc-optcomDenoised_bold.nii.gz \
    --include_motion --include_CSF \
    --task rest
EOF

#########################################################
# Combined Regressors 70 Components Kundu Decision Tree #
#########################################################

cat << EOF > ${sbj}_GLM_sbatch_CR.txt
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ combined_regressors_v23_c70_kundu_wnw \
    --inputfiles ${task_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${task_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${task_ted_dir}/${sbj}_Reg2ICA/${sbj}_wnw_run-?_c70_kundu_Combined_Metrics.csv \
    --task wnw \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-1/${sbj}.results/ combined_regressors_v23_c70_kundu_movie_run-1 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_movie_run-1_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-2/${sbj}.results/ combined_regressors_v23_c70_kundu_movie_run-2 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_movie_run-2_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/movie_run-3/${sbj}.results/ combined_regressors_v23_c70_kundu_movie_run-3 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_movie_run-3_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-1/${sbj}.results/ combined_regressors_v23_c70_kundu_breathing_run-1 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_breathing_run-1_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-2/${sbj}.results/ combined_regressors_v23_c70_kundu_breathing_run-2 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_breathing_run-2_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
source /home/handwerkerd/InitConda.sh; \
cd ${rootdir}; module load afni; \
  python3 /data/holnessmn/UpToDate_ComplexME/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
    $sbj ./ ../afniproc_orig/breathing_run-3/${sbj}.results/ combined_regressors_v23_c70_kundu_breathing_run-3 \
    --inputfiles ${rest_ted_dir}/desc-optcom_bold.nii.gz --scale_ts \
    --noise_regressors ${rest_ted_dir}/desc-ICA_mixing.tsv \
    --regressors_metric_table ${rest_ted_dir}/${sbj}_Reg2ICA/${sbj}_breathing_run-3_c70_kundu_Combined_Metrics.csv \
    --task rest \
    --denoising_type 'combined regressors'
EOF

swarm --time 12:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_GLM_sbatch_ted.txt
swarm --time 12:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_GLM_sbatch_CR.txt

########################
##### OLD analyses...... #####
########################

# cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${sbj}
# mkdir GLMs

# cd GLMs

# if [ -f ${sbj}_WNW_GLM_sbatch.txt ]; then
#     echo Deleting and recreating ${sbj}_WNW_GLM_sbatch.txt
#     rm ${sbj}_WNW_GLM_sbatch.txt
# fi
# touch ${sbj}_WNW_GLM_sbatch.txt

# rootdir=`pwd`

# cat << EOF > ${sbj}_WNW_GLM_sbatch.txt
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot_CSF \
#         --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
#         --include_motion --include_CSF --scale_ts
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ OC_mot \
#         --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
#         --include_motion --scale_ts
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ e2_mot_CSF \
#         --inputfiles pb0?.${sbj}.r0?.e02.volreg+orig.HEAD \
#         --include_motion --include_CSF --scale_ts
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ septedana_mot \
#         --inputfiles tedana_c75_r0?/dn_ts_OC.nii.gz \
#         --include_motion
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ septedana_mot_csf \
#         --inputfiles tedana_c75_r0?/dn_ts_OC.nii.gz \
#         --include_motion  --include_CSF
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ orthtedana_mot_csf \
#         --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
#         --include_motion  --include_CSF --scale_ts \
#         --noise_regressors tedana_c75_r0?/ica_mixing.tsv \
#         --regressors_metric_table tedana_c75_r0?/ica_metrics.tsv
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ orthtedana_mot \
#         --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
#         --include_motion --scale_ts \
#         --noise_regressors tedana_c75_r0?/ica_mixing.tsv \
#         --regressors_metric_table tedana_c75_r0?/ica_metrics.tsv
#     source /home/handwerkerd/InitConda.sh; \
#     cd ${rootdir}; module load afni; \
#       python /data/handwerkerd/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py \
#         $sbj ./ ../afniproc_orig/WNW/${sbj}.results/ combined_regressors \
#         --inputfiles tedana_c75_r0?/ts_OC.nii.gz \
#         --scale_ts \
#         --noise_regressors ../../../Regressors/RejectedComps/${sbj}_wnw_r0?_CombinedRejected_Rejected_ICA_Components.csv
# EOF

# swarm --time 6:00:00 -g 12 -t 8 -m afni --merge-output --job-name ${sbj}_GLMS ${sbj}_WNW_GLM_sbatch.txt




