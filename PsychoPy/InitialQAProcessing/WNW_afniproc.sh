# A hacky script designed to run afni_proc.py on TechScan_900
# Note: -tcat_remove_first_trs 0 for now, but might want to adjust timing files later
# Note: Removing last 5 TRs because those are the noise scans

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/TechPhantomScans/TechScan_900/QuickQAProcess

origdir='../Unprocessed/sub-T01/'
subj_id='sub-T01'

afni_proc.py -subj_id $subj_id \
   -blocks despike tshift align volreg mask combine scale regress \
   -copy_anat ${origdir}anat/${subj_id}_T1w.nii \
   -anat_has_skull yes\
   -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-1_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-2_echo-1_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-3_echo-1_part-mag_bold.nii \
   -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-2_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-2_echo-2_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-3_echo-2_part-mag_bold.nii \
   -dsets_me_echo ${origdir}func/${subj_id}_task-wnw_run-1_echo-3_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-2_echo-3_part-mag_bold.nii \
       ${origdir}func/${subj_id}_task-wnw_run-3_echo-3_part-mag_bold.nii \
   -echo_times 13.44 31.7 49.96 -reg_echo 2 \
   -tcat_remove_first_trs 0 \
   -tcat_remove_last_trs 5 \
   -align_opts_aea -cost lpc+ZZ -check_flip \
   -volreg_align_to MIN_OUTLIER -volreg_align_e2a \
   -combine_method m_tedana \
  -regress_censor_motion 0.2 -regress_censor_outliers 0.05 \
  -regress_stim_times ./stimfiles/VisProc_Times.1D \
                      ./stimfiles/FalVisProc_Times.1D  \
                      ./stimfiles/AudProc_Times.1D \
                      ./stimfiles/FalAudProc_Times.1D \
                      ./stimfiles/Keypress_Times.1D \
  -regress_stim_labels VisWord FalVisWord AudWord FalAudWord Keypress \
  -regress_basis_multi 'BLOCK(4,1)' 'BLOCK(4,1)' 'BLOCK(4,1)' 'BLOCK(4,1)' 'BLOCK(1,1)' \
  -regress_opts_3dD \
  -gltsym 'SYM: +VisWord -FalVisWord' -glt_label 1 Vis-FalVis \
  -gltsym 'SYM: +AudWord -FalAudWord' -glt_label 2 Aud-FalAud \
  -gltsym 'SYM: +AudWord +VisWord -FalAudWord -FalVisWord' -glt_label 3 Word-NonWord \
  -gltsym 'SYM: -AudWord +VisWord -FalAudWord +FalVisWord' -glt_label 4 Vis-Aud \
  -gltsym 'SYM: +Keypress' -glt_label 5 Keypress \
  -regress_est_blur_epits -regress_est_blur_errts \
  -regress_apply_mot_types demean deriv \
  -regress_reml_exec -html_review_style pythonic \
  -execute
   

# Confirm later that this won't need to be manually specified
#    -tshift_opts_ts -tpattern alt+z