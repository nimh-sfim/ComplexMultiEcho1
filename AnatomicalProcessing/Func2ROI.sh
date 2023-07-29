# Extract ROIs & Intersect with Functional contrasts

subj_id=$1

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat
mkdir StudyROIs
cd StudyROIs
ln -s ../aparc.a2009s+aseg_REN_gmrois.nii.gz ./

dset_orig="../aparc.a2009s+aseg_REN_gmrois.nii.gz"
dset_anatEPI=rois_anat_EPIgrid.nii.gz
 
dset_grid="../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig"

# ROIs are based on the findings presented in: 
# "Dough, tough, cough, rough: A “fast” fMRI localizer of component processes in reading"
#  Malins et al Neuropsychologia, 2016: https://doi.org/10.1016/j.neuropsychologia.2016.08.027
#
# ROIs for audio vs visual contrasts
# Primary auditory cortex (Roughly Heschl's gyrus) (audio > visual)
# 122   tiss__gm     ctx_lh_S_temporal_transverse
# 197   tiss__gm     ctx_rh_S_temporal_transverse
#
# Primary visual cortex (visual > audio)
# 92   tiss__gm     ctx_lh_S_calcarine
# 167   tiss__gm     ctx_rh_S_calcarine
#
# fusiform (visual word form area in left OT/fusiform) (visual words > nonwords)
# another part of bilateral fusiform showed nonwords>words)... might want to consider breaking up this ROI or creating 2 clusters 1 for positive & one for negative)
# 69   tiss__gm     ctx_lh_G_oc-temp_lat-fusifor
# 144   tiss__gm     ctx_rh_G_oc-temp_lat-fusifor
#
# visual word>nonword
# 121   tiss__gm     ctx_lh_S_temporal_sup
# 196   tiss__gm     ctx_rh_S_temporal_sup
#
# visal word>nonword
# 86   tiss__gm     ctx_lh_G_temporal_middle
# 161   tiss__gm     ctx_rh_G_temporal_middle
#
# visual word>nonword
# 60 ctx_lh_G_front_inf-Opercular + 62 ctx_lh_G_front_inf-Triangul
# 135 ctx_rh_G_front_inf-Opercular + 137 ctx_rh_G_front_inf-Triangul
#
# Other word vs nonword ROIs (less likely to be central ROIs for the contasts)
# superior parietal lobule
# 75   tiss__gm     ctx_lh_G_parietal_sup
# 150   tiss__gm     ctx_rh_G_parietal_sup
# 6   tiss__gm     Left-Cerebellum-Cortex
# 26   tiss__gm     Right-Cerebellum-Cortex
# 59   tiss__gm     ctx_lh_G_cuneus
# 134   tiss__gm     ctx_rh_G_cuneus
# 78   tiss__gm     ctx_lh_G_precuneus
# 153   tiss__gm     ctx_rh_G_precuneus
# 14   tiss__gm     Left-Hippocampus
# 31   tiss__gm     Right-Hippocampus
# 85   tiss__gm     ctx_lh_G_temporal_inf
# 160   tiss__gm     ctx_rh_G_temporal_inf
# 120   tiss__gm     ctx_lh_S_temporal_inf
# 195   tiss__gm     ctx_rh_S_temporal_inf
# 67   tiss__gm     ctx_lh_G_occipital_middle
# 142   tiss__gm     ctx_rh_G_occipital_middle


# ROIs is for Word-Nonword contrasts
# ROIidxWNW="69,144,121,196,86,161,60,135,75,150,6,26,59,134,78,153,14,31,85,160,120,195,67,142"
ROIidxWNW="121,196,60,135,86,161,60,135,78,153"
ROIidxWNWlist=(121 196 60 135 86 161 60 135 78 153)
# ROIidxWNWlabels=(ctx_lh_G_oc-temp_lat-fusifor ctx_rh_G_oc-temp_lat-fusifor ctx_lh_S_temporal_sup ctx_rh_S_temporal_sup \
#               ctx_lh_G_temporal_middle ctx_rh_G_temporal_middle ctx_lh_G_front_inf-OperTri ctx_rh_G_front_inf-OperTri \
#               ctx_lh_G_parietal_sup ctx_rh_G_parietal_sup Left-Cerebellum-Cortex Right-Cerebellum-Cortex \
#               ctx_lh_G_cuneus ctx_rh_G_cuneus ctx_lh_G_precuneus ctx_rh_G_precuneus \
#               Left-Hippocampus Right-Hippocampus ctx_lh_G_temporal_inf ctx_rh_G_temporal_inf \
#               ctx_lh_S_temporal_inf ctx_rh_S_temporal_inf ctx_lh_G_occipital_middle ctx_rh_G_occipital_middle)
ROIidxVis="92,167"
ROIidxVislist=(92 167)

ROIidxAud="122,197"
ROIidxAudlist=(122 197 )

# ROIidxVSlabels=(ctx_lh_S_temporal_transverse ctx_rh_S_temporal_transverse ctx_lh_S_calcarine ctx_rh_S_calcarine)

cat << EOF > FuncROI_Labels.lt
   <VALUE_LABEL_DTABLE
   ni_type="2*String"
   ni_dimen="200"
   pbar_name="ROI_i256">
   "0" "Unknown"
   "122" "L A1"
   "197" "R A1"
   "92" "L V1"
   "167" "R V1"
   "69" "L latFusiform"
   "144" "R latFusiform"
   "121" "lSTS"
   "196" "rSTS"
   "86" "lMTG"
   "161" "rMTG"
   "60" "lIFG"
   "135" "rIFG"
   "75" "lSPG"
   "150" "rSPG"
   "6" "lCerebrellum"
   "26" "rCerebellum"
   "59" "lCuneus"
   "134" "rCuneus"
   "78" "lPrecuneus"
   "153" "rPrecuneus"
   "14" "lHippocampus"
   "31" "rHippocampus"
   "85" "lITG"
   "160" "rITG"
   "120" "lITS"
   "195" "rITS"
   "67" "l Middle Occipital"
   "142" "r Middle Occipital"
   </VALUE_LABEL_DTABLE>
EOF

3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix tmp_WNW_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxWNW}>" \
    -master ${dset_grid}

#   60 is ctx_lh_G_front_inf-Opercular &  62 is ctx_lh_G_front_inf-Triangul
#     combining into 1 ROI with the index 60 that will still be labelled ctx_lh_G_front_inf-Opercular
#   135 is ctx_rh_G_front_inf-Opercular &  137 is ctx_rh_G_front_inf-Triangul
#     combining into 1 ROI with the index 135 that will still be labelled ctx_rh_G_front_inf-Opercular
3dcalc -a tmp_WNW_${dset_anatEPI}  -prefix tmp2_WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,62),60,a))' \
   -short 
3dcalc -a tmp2_WNW_${dset_anatEPI}  -prefix WNW_${dset_anatEPI} -overwrite \
   -expr 'int(ifelse(equals(a,137),135,a))' \
   -short 

rm tmp_WNW* tmp2_WNW*

3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix Vis_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxVis}>" \
    -master ${dset_grid}
 
3dAllineate -overwrite \
    -1Dmatrix_apply IDENTITY \
    -prefix Aud_${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}<${ROIidxAud}>" \
    -master ${dset_grid}


# re-attach labeltable
3drefit  -copytables "${dset_orig}" WNW_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_${dset_anatEPI}
# re-attach header property to use int-based colormap in AFNI GUI
3drefit -cmap INT_CMAP WNW_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_${dset_anatEPI}


# Dilate all ROIs and then recombine them with no overlapping voxels
for ROIidx in ${ROIidxVislist[@]}; do
   3dcalc -a Vis_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_Vis_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_Vis_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_Vis_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_Vis_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_Vis_${ROIidx}d2val_${dset_anatEPI} -overwrite
done

for ROIidx in ${ROIidxAudlist[@]}; do
   3dcalc -a Aud_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_Aud_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_Aud_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_Aud_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_Aud_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_Aud_${ROIidx}d2val_${dset_anatEPI} -overwrite
done

for ROIidx in ${ROIidxWNWlist[@]}; do
   3dcalc -a WNW_${dset_anatEPI} -expr "equals(a,${ROIidx})*${ROIidx}" \
      -prefix  tmp_WNW_${ROIidx}_${dset_anatEPI} -overwrite
   3dmask_tool -input tmp_WNW_${ROIidx}_${dset_anatEPI} \
      -dilate_input 2 -prefix tmp_WNW_${ROIidx}d2_${dset_anatEPI} \
      -overwrite 
   3dcalc -a tmp_WNW_${ROIidx}d2_${dset_anatEPI} -expr "ispositive(a)*${ROIidx}" \
       -prefix tmp_WNW_${ROIidx}d2val_${dset_anatEPI} -overwrite
done


# Identify all voxels that overlap
3dMean -overwrite -count -prefix ROI_overlap_${dset_anatEPI} tmp_Vis_*d2_${dset_anatEPI} tmp_Aud_*d2_${dset_anatEPI} tmp_WNW_*d2_${dset_anatEPI}

# Recombine all the ROIs for each group, and remove voxels in more than one ROI unless they were in the un-dilated ROI
3dMean -overwrite -sum -datum short -prefix tmp_Vis_d2recombined_${dset_anatEPI} tmp_Vis_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_Vis_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c Vis_${dset_anatEPI} \
   -overwrite -prefix Vis_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"

3dMean -overwrite -sum -datum short -prefix tmp_Aud_d2recombined_${dset_anatEPI} tmp_Aud_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_Aud_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c Aud_${dset_anatEPI} \
   -overwrite -prefix Aud_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"

3dMean -overwrite -sum -datum short -prefix tmp_WNW_d2recombined_${dset_anatEPI} tmp_WNW_*d2val_${dset_anatEPI}
3dcalc -short -a tmp_WNW_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
   -c WNW_${dset_anatEPI} \
   -overwrite -prefix WNW_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b) + c*isnegative(1.1-b)"


# 3dMean -overwrite -sum -datum short -prefix tmp_WNW_d2recombined_${dset_anatEPI} tmp_WNW_*d2val_${dset_anatEPI}
# 3dcalc -short -a tmp_WNW_d2recombined_${dset_anatEPI} -b ROI_overlap_${dset_anatEPI} \
#    -overwrite -prefix WNW_d2_${dset_anatEPI} -expr "a*ispositive(1.1-b)"

# re-attach labeltable
3drefit  -copytables "${dset_orig}" WNW_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Vis_d2_${dset_anatEPI}
3drefit  -copytables "${dset_orig}" Aud_d2_${dset_anatEPI}
# re-attach header property to use int-based colormap in AFNI GUI
3drefit -cmap INT_CMAP WNW_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Vis_d2_${dset_anatEPI}
3drefit -cmap INT_CMAP Aud_d2_${dset_anatEPI}

# Ugly way to get subset of ROIs just expected visual-audio contrast ROIs
# 3dcalc -a ${dset_anatEPI} -prefix VS_${dset_anatEPI} -overwrite -short \
#    -expr 'int(122*equals(a,122) + 197*equals(a,197) +92*equals(a,92) +167*equals(a,167))'

# Ugly way to get subset of ROIs just expected word-nonword contrast ROIs
# NOTE:

# 3dcalc -a ${dset_anatEPI} -prefix WNW_${dset_anatEPI} -overwrite -short \
#    -expr 'int(69*equals(a,69) + 144*equals(a,144) + 121*equals(a,121) + 196*equals(a,196) + 86*equals(a,86) + 161*equals(a,161) + 60*equals(a,60) + 60*equals(a,62) + 135*equals(a,135) + 135*equals(a,137) + 75*equals(a,75) + 150*equals(a,150) + 6*equals(a,6) + 26*equals(a,26) + 59*equals(a,59) + 134*equals(a,134) + 78*equals(a,78) + 153*equals(a,153) + 14*equals(a,14) + 31*equals(a,31) + 85*equals(a,85) + 160*equals(a,160) + 120*equals(a,120) + 195*equals(a,195) + 67*equals(a,67) + 142*equals(a,142) )'

# WNW functional clusters
echo "LOOK TO MAKE SURE SUBBRIK IS word-nonword TSTAT"
# 3dinfo -subbrick_info ../../GLMs/OC_mot/stats.${subj_id}.OC_mot_REML+orig'[31]'
3dinfo -subbrick_info ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig'[31]'
3dClusterize -inset ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig \
   -mask_from_hdr -ithr 31 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map WNW_Clusters -overwrite

# Vis-Aud functional clusters
echo "LOOK TO MAKE SURE SUBBRIK IS vis-aud TSTAT"
3dinfo -subbrick_info ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig'[35]'
3dClusterize -inset ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig \
   -mask_from_hdr -ithr 35 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map VisAud_Clusters  -overwrite

# intersect the anatomical ROIs and the functional contrasts
# Since int() always rounds down, the +0.5 makes sure any floating
#   point errors round to the correct value.

# Audio contrast should be negative for vis-audio
3dcalc -overwrite -prefix Aud_funcROI.${subj_id}.nii.gz \
   -a Aud_d2_${dset_anatEPI} -b VisAud_Clusters+orig \
   -c ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig'[35]' \
   -expr 'int(0.5+a*ispositive(b)*isnegative(c))' -short

# visual constrast should be positive for vis-audio
3dcalc -overwrite -prefix Vis_funcROI.${subj_id}.nii.gz \
   -a Vis_d2_${dset_anatEPI} -b VisAud_Clusters+orig \
   -c ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig'[35]' \
   -expr 'int(0.5+a*ispositive(b)*ispositive(c))' -short


# Only for word>nonword voxels
3dcalc -overwrite -prefix WNWfuncROI.${subj_id}.nii.gz \
   -a WNW_d2_${dset_anatEPI} -b WNW_Clusters+orig \
   -c ../../GLMs/optimally_combined_mot_csf_v23_c70_kundu_wnw/stats.${subj_id}.optimally_combined_mot_csf_v23_c70_kundu_wnw_REML+orig'[31]' \
   -expr 'int(0.5+a*ispositive(b)*ispositive(c))' -short


3dcalc -overwrite -prefix ${subj_id}.FuncROIs.nii.gz \
   -a Vis_funcROI.${subj_id}.nii.gz \
   -b Aud_funcROI.${subj_id}.nii.gz \
   -c WNWfuncROI.${subj_id}.nii.gz \
   -expr 'int(a+b+c+0.5)' -short


# attach more descriptive labeltable
# 3drefit  -copytables "${dset_orig}" ${subj_id}.FuncROIs.nii.gz
3drefit  -labeltable FuncROI_Labels.lt ${subj_id}.FuncROIs.nii.gz

# reattach header property to use int-based colormap in AFNI GUI
3drefit -cmap INT_CMAP ${subj_id}.FuncROIs.nii.gz


rm tmp_*.nii.gz
