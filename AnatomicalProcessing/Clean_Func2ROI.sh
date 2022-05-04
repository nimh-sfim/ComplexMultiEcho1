# Extract ROIs & Intersect with Functional contrasts

subj_id=$1

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat
mkdir StudyROIs_clean
cp aparc.a2009s+aseg_REN_gmrois.nii.gz ./StudyROIs/
cd StudyROIs_clean

dset_orig="../aparc.a2009s+aseg_REN_gmrois.nii.gz"
dset_anatEPI=rois_anat_EPIgrig.nii.gz
 
dset_grid="../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig"


# 3dcopy -overwrite ../aparc.a2009s+aseg_REN_gmrois.nii.gz tmp_all_gmROIs.nii.gz

# # 60 is ctx_lh_G_front_inf-Opercular &  62 is ctx_lh_G_front_inf-Triangul
# # combining into 1 ROI with the index 60 that we'll call ctx_lh_G_front_inf-OperTri
# 3dcalc -a tmp_all_gmROIs.nii.gz -prefix tmp_all_gmROIs.nii.gz -overwrite -expr 'equals(a,62)*60 + not(equals(a,62))*a'

# # 135 is ctx_rh_G_front_inf-Opercular &  137 is ctx_rh_G_front_inf-Triangul
# # combining into 1 ROI with the index 60 that we'll call ctx_rh_G_front_inf-OperTri
# 3dcalc -a tmp_all_gmROIs.nii.gz -prefix tmp_all_gmROIs.nii.gz -overwrite -expr 'equals(a,137)*135 + not(equals(a,137))*a'

# get ROI indices
# ROIs is for Word-Nonword contrasts
ROIidxWNW=(  69 144 121 196 \
             86 161 60 135 \
             75 150 6 26 \
             59 134 78 153 \
             14 31 85 160 \
             120 195 67 142)

# ROIidxWNWlabels=(ctx_lh_G_oc-temp_lat-fusifor ctx_rh_G_oc-temp_lat-fusifor ctx_lh_S_temporal_sup ctx_rh_S_temporal_sup \
#               ctx_lh_G_temporal_middle ctx_rh_G_temporal_middle ctx_lh_G_front_inf-OperTri ctx_rh_G_front_inf-OperTri \
#               ctx_lh_G_parietal_sup ctx_rh_G_parietal_sup Left-Cerebellum-Cortex Right-Cerebellum-Cortex \
#               ctx_lh_G_cuneus ctx_rh_G_cuneus ctx_lh_G_precuneus ctx_rh_G_precuneus \
#               Left-Hippocampus Right-Hippocampus ctx_lh_G_temporal_inf ctx_rh_G_temporal_inf \
#               ctx_lh_S_temporal_inf ctx_rh_S_temporal_inf ctx_lh_G_occipital_middle ctx_rh_G_occipital_middle)

ROIidxVS=(122 197 92 167)
# ROIidxVSlabels=(ctx_lh_S_temporal_transverse ctx_rh_S_temporal_transverse ctx_lh_S_calcarine ctx_rh_S_calcarine)


# Put all ROIs and labels in one list
ROIidxlist=(${ROIidxVS[@]} ${ROIidxWNW[@]})
# ROIidxlabels=(${ROIidxVSlabels[@]} ${ROIidxWNWlabels[@]})

echo Length ROIidxlist is ${#ROIidxlist[@]}
echo Length ROIidxlabels is ${#ROIidxlabels[@]}

3dAllineate \
    -1Dmatrix_apply IDENTITY \
    -prefix ${dset_anatEPI}  \
    -final NN \
    -source "${dset_orig}[${ROIidxlist}]" \
    -master ${dst_grid}
 
# reattach labeltable: shouldn't matter that it is full, and you just have a subset
3drefit  -copytables "${dset_orig}" ${dset_anatEPI}
# reattach header property to use int-based colormap in AFNI GUI
3drefit -cmap INT_CMAP ${dset_anatEPI}

# Ugly manually reduce to just expected visual-audio contrast ROIs
3dcalc -a ${dset_anatEPI} -prefix VS_${dset_anatEPI} -overwrite -short \
   -expr 'int(122*equals(a,122) + 197*equals(a,197) +92*equals(a,92) +167*equals(a,167))'

# Ugly manually reduce to just expected word-nonword contrast ROIs
3dcalc -a ${dset_anatEPI} -prefix WNW_${dset_anatEPI} -overwrite -short \
   -expr 'int(69*equals(a,69) + 144*equals(a,144) + 121*equals(a,121) + 196*equals(a,196) ' \
         '+ 86*equals(a,86) + 161*equals(a,161) + 60*equals(a,60) + 60*equals(a,62) + 135*equals(a,135) + 135*equals(a,137)' \
         '+ 75*equals(a,75) + 150*equals(a,150) + 6*equals(a,6) + 26*equals(a,26) ' \
         '+ 59*equals(a,59) + 134*equals(a,134) + 78*equals(a,78) + 153*equals(a,153) + ' \
         '+ 14*equals(a,14) + 31*equals(a,31) + 85*equals(a,85) + 160*equals(a,160) + ' \
         '+ 120*equals(a,120) + 195*equals(a,195) + 67*equals(a,67) + 142*equals(a,142) ))'




# WNW clusters
echo "LOOK TO MAKE SURE SUBBRIK IS word-nonword TSTAT"
3dinfo -subbrick_info ../../GLMs/OC_mot/stats.${subj_id}.OC_mot_REML+orig'[31]'
3dClusterize -inset ../../GLMs/OC_mot/stats.${subj_id}.OC_mot_REML+orig \
   -mask_from_hdr -ithr 31 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map WNW_Clusters -overwrite

# Vis-Aud clusters
echo "LOOK TO MAKE SURE SUBBRIK IS vis-aud TSTAT"
3dinfo -subbrick_info ../../GLMs/OC_mot/stats.${subj_id}.OC_mot_REML+orig'[35]'
3dClusterize -inset ../../GLMs/OC_mot/stats.${subj_id}.OC_mot_REML+orig \
   -mask_from_hdr -ithr 35 \
   -bisided p=0.01 \
   -NN 1 -clust_nvox 5 \
   -pref_map VisAud_Clusters  -overwrite

# intersect the anatomical ROIs and the functional contrasts
# Since int() always rounds down, the +0.5 makes sure any floating
#   point errors round to the correct value.
3calc -overwrite -prefix VSfuncROI.${subj_id}.nii.gz \
   -a VS_${dset_anatEPI} -b VS_Clusters+orig \
   -expr 'int(0.5+ispositive(abs(b)-3.3)*a)' -short

3calc -overwrite -prefix WNWfuncROI.${subj_id}.nii.gz \
   -a WNW_${dset_anatEPI} -b WNW_Clusters+orig \
   -expr 'int(0.5+ispositive(abs(b)-3.3)*a)' -short

3dcalc -overwrite -prefix ${subj_id}.FuncROIs.nii.gz \
   -a VSfuncROI.${subj_id}.nii.gz \
   -b WNWfuncROI.${subj_id}.nii.gz \
   -expr 'int(a+b+0.5)' -short


# reattach labeltable: shouldn't matter that it is full, and you just have a subset
3drefit  -copytables "${dset_orig}" ${subj_id}.FuncROIs.nii.gz
# reattach header property to use int-based colormap in AFNI GUI
3drefit -cmap INT_CMAP ${subj_id}.FuncROIs.nii.gz
