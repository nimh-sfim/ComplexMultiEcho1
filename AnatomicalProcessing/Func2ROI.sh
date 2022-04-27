# Extract ROIs & Intersect with Functional

# needs --20g mem

subj_id=$1

cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/Proc_Anat
mkdir StudyROIs
cp aparc.a2009s+aseg_REN_gmrois.nii.gz ./StudyROIs/
cd StudyROIs

3dcopy -overwrite ../aparc.a2009s+aseg_REN_gmrois.nii.gz tmp_all_gmROIs.nii.gz


# 60 is ctx_lh_G_front_inf-Opercular &  62 is ctx_lh_G_front_inf-Triangul
# combining into 1 ROI with the index 60 that we'll call ctx_lh_G_front_inf-OperTri
3dcalc -a tmp_all_gmROIs.nii.gz -prefix tmp_all_gmROIs.nii.gz -overwrite -expr 'equals(a,62)*60 + not(equals(a,62))*a'


# 135 is ctx_rh_G_front_inf-Opercular &  137 is ctx_rh_G_front_inf-Triangul
# combining into 1 ROI with the index 60 that we'll call ctx_rh_G_front_inf-OperTri
3dcalc -a tmp_all_gmROIs.nii.gz -prefix tmp_all_gmROIs.nii.gz -overwrite -expr 'equals(a,137)*135 + not(equals(a,137))*a'


# get ROI indices
# ROIs is for Word-Nonword contrasts
ROIidxWNW=(  69 144 121 196 \
             86 161 60 135 \
             75 150 6 26 \
             59 134 78 153 \
             14 31 85 160 \
             120 195 67 142)

ROIidxWNWlabels=(ctx_lh_G_oc-temp_lat-fusifor ctx_rh_G_oc-temp_lat-fusifor ctx_lh_S_temporal_sup ctx_rh_S_temporal_sup \
              ctx_lh_G_temporal_middle ctx_rh_G_temporal_middle ctx_lh_G_front_inf-OperTri ctx_rh_G_front_inf-OperTri \
              ctx_lh_G_parietal_sup ctx_rh_G_parietal_sup Left-Cerebellum-Cortex Right-Cerebellum-Cortex \
              ctx_lh_G_cuneus ctx_rh_G_cuneus ctx_lh_G_precuneus ctx_rh_G_precuneus \
              Left-Hippocampus Right-Hippocampus ctx_lh_G_temporal_inf ctx_rh_G_temporal_inf \
              ctx_lh_S_temporal_inf ctx_rh_S_temporal_inf ctx_lh_G_occipital_middle ctx_rh_G_occipital_middle)

ROIidxVS=(122 197 92 167)
ROIidxVSlabels=(ctx_lh_S_temporal_transverse ctx_rh_S_temporal_transverse ctx_lh_S_calcarine ctx_rh_S_calcarine)


####

ROIidxlist=(${ROIidxVS[@]} ${ROIidxWNW[@]})
ROIidxlabels=(${ROIidxVSlabels[@]} ${ROIidxWNWlabels[@]})
# ROIidxlist=(122 197 92 167 \
#              69 144 121 196 \
#              86 161 60 135 \
#              75 150 6 26 \
#              59 134 78 153 \
#              14 31 85 160 \
#              120 195 67 142)

# get ROI labels
# ROIidxlabels=(ctx_lh_S_temporal_transverse ctx_rh_S_temporal_transverse ctx_lh_S_calcarine ctx_rh_S_calcarine \
#               ctx_lh_G_oc-temp_lat-fusifor ctx_rh_G_oc-temp_lat-fusifor ctx_lh_S_temporal_sup ctx_rh_S_temporal_sup \
#               ctx_lh_G_temporal_middle ctx_rh_G_temporal_middle ctx_lh_G_front_inf-OperTri ctx_rh_G_front_inf-OperTri \
#               ctx_lh_G_parietal_sup ctx_rh_G_parietal_sup Left-Cerebellum-Cortex Right-Cerebellum-Cortex \
#               ctx_lh_G_cuneus ctx_rh_G_cuneus ctx_lh_G_precuneus ctx_rh_G_precuneus \
#               Left-Hippocampus Right-Hippocampus ctx_lh_G_temporal_inf ctx_rh_G_temporal_inf \
#               ctx_lh_S_temporal_inf ctx_rh_S_temporal_inf ctx_lh_G_occipital_middle ctx_rh_G_occipital_middle)

echo Length ROIidxlist is ${#ROIidxlist[@]}
echo Length ROIidxlabels is ${#ROIidxlabels[@]}

numROIs=${#ROIidxlist[@]}

# Make the desired ROI a stand-alone file:
for ((idx=0; $idx<${numROIs}; idx++)); do
    echo idx $idx ROIidx  ${ROIidxlist[$idx]} label ${ROIidxlabels[$idx]}
    3dcalc -overwrite -a tmp_all_gmROIs.nii.gz  \
    -expr 'equals(a, '${ROIidxlist[$idx]}')' -prefix tmpROI_${ROIidxlabels[$idx]}.nii.gz
    3drefit -sublabel 0 ${ROIidxlabels[$idx]} tmpROI_${ROIidxlabels[$idx]}.nii.gz

    # downsample to EPI resolution and voxel space
    3dfractionize -overwrite -clip 0.33 \
       -template ../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig \
       -input tmpROI_${ROIidxlabels[$idx]}.nii.gz \
       -prefix tmpROI_EPIres_${ROIidxlabels[$idx]}.nii.gz
done

# Put all the ROIs as subbriks in one file
3dTcat -overwrite -prefix tmp_ROIs_EPIres.nii.gz tmpROI_EPIres_*.nii.gz


# Identify voxels that are in more than one ROI and remove them from all ROIs
3dTstat -overwrite -nzcount -prefix tmp_ROIs_EPIres_nzcount.nii.gz tmp_ROIs_EPIres.nii.gz

3dcalc -overwrite -a tmp_ROIs_EPIres_nzcount.nii.gz \
-prefix ROI_1vox_per_mask.nii.gz -expr '1*equals(a,1)'


for ((idx=0; $idx<${numROIs}; idx++)); do
    echo idx $idx ROIidx  ${ROIidxlist[$idx]} label ${ROIidxlabels[$idx]}
    3dcalc -a tmpROI_EPIres_${ROIidxlabels[$idx]}.nii.gz \
       -b ROI_1vox_per_mask.nii.gz \
       -expr '(ispositive(a)*ispositive(b)*'${ROIidxlist[$idx]}')' \
       -prefix tmpROI_nooverlap_EPIres_${ROIidxlabels[$idx]}.nii.gz \
       -overwrite
done

if [ -f tmpROI_nooverlap_EPIres_all.nii.gz ]; then
  rm tmpROI_nooverlap_EPIres_all.nii.gz
fi
3dTcat -prefix tmpROI_nooverlap_EPIres_all.nii.gz tmpROI_nooverlap_EPIres_*.nii.gz
3dTstat -overwrite -sum -prefix ROIs_EPIres.nii.gz tmpROI_nooverlap_EPIres_all.nii.gz 


# Make functional masks for Visual-Audio




# Create Functional ROIs:
# PRECAUTIONS: no 2 ROIs overlapping (same voxels), 
# intersect the functional contrast (Stats.REML) w/ anatomical ROIs
# inset = 3D volume of values (functionally-derived values like Stats.REML)
# threshold for dataset values (use p < 0.001?)
# volthr = minimum number of voxels for an ROI (want at least 5 voxels)
# refset -> has labletable?
# output: map of ROIs

# NOTE CURRENTLY RUNNING ON THE DENOISED STATS FILE. WILL WANT TO USE OPTIMALLY COMBINED OR 2nd ECHO
# NOTE THRESHOLD IS ARBITRARY t>3

# cp ../aparc.a2009s+aseg_REN_all.niml.lt ./ROIs_EPIres.niml.lt

# word-nonword T-stat: 23 visual-audio T-stat: 26
# 3dROIMaker -overwrite  -inset ../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig'[23]' \
#   -refset ROIs_EPIres.nii.gz -thresh 3.3 -volthr 5 -prefix WordnonWord_FuncROIs

# 3dROIMaker -overwrite  -inset ../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig'[26]' \
#   -refset ROIs_EPIres.nii.gz -thresh 3.3 -volthr 5 -prefix VisAud_FuncROIs

# make functional masks for Word-nonword contrast
for ((idx=0; $idx<${#ROIidxWNW[@]}; idx++)); do
    echo idx $idx ROIidx  ${ROIidxWNW[$idx]} label ${ROIidxWNWlabels[$idx]}
    3dcalc -overwrite -a ../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig'[23]' \
   -b tmpROI_nooverlap_EPIres_${ROIidxWNWlabels[$idx]}.nii.gz \
   -expr 'ispositive(abs(a)-3.3)*b' \
   -prefix tmpfuncROI_${ROIidxWNWlabels[$idx]}.nii.gz
done

# make functional masks for vis-aud contrast
for ((idx=0; $idx<${#ROIidxVS[@]}; idx++)); do
    echo idx $idx ROIidx  ${ROIidxVS[$idx]} label ${ROIidxVSlabels[$idx]}
    3dcalc -overwrite -a ../../afniproc_orig/WNW/${subj_id}.results/stats.${subj_id}_REML+orig'[26]' \
   -b tmpROI_nooverlap_EPIres_${ROIidxVSlabels[$idx]}.nii.gz \
   -expr 'int(0.5+ispositive(abs(a)-3.3)*b))' -short \
   -prefix tmpfuncROI_${ROIidxVSlabels[$idx]}.nii.gz
done

# Combine all the function ROIS into one mask
if [ -f tmpfuncROI_EPIres_all.nii.gz ]; then
  rm tmpfuncROI_EPIres_all.nii.gz
fi
3dTcat -prefix tmpfuncROI_EPIres_all.nii.gz tmpfuncROI_*.nii.gz
3dTstat -overwrite -sum -prefix ROIs_FuncLocalized.nii.gz tmpfuncROI_EPIres_all.nii.gz