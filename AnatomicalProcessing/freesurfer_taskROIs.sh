#/bin/sh

# Given the correct grid, this will be used to generate ROIs to use for Contrast-to-noise and other measurements

# Explanations from https://doi.org/10.1016/j.neuropsychologia.2016.08.027

# ROIS used in Ramya's poster with explanations:

# ROIs for audio vs visual contrasts
# Primary auditory cortex (Roughly Heschl's gyrus) (audio > visual)
# 122   tiss__gm     ctx_lh_S_temporal_transverse
# 197   tiss__gm     ctx_rh_S_temporal_transverse

# Primary visual cortex (visual > audio)
# 92   tiss__gm     ctx_lh_S_calcarine
# 167   tiss__gm     ctx_rh_S_calcarine


# fusiform (visual word form area in left OT/fusiform) (visual words > nonwords)
# another part of bilateral fusiform showed nonwords>words)... might want to consider breaking up this ROI?)
# 69   tiss__gm     ctx_lh_G_oc-temp_lat-fusifor
# 144   tiss__gm     ctx_rh_G_oc-temp_lat-fusifor

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

# Additional ROIs for Word-Nonword contrast
# word>nonword
# 86   tiss__gm     ctx_lh_G_temporal_middle
# 161   tiss__gm     ctx_rh_G_temporal_middle

# 
# 85   tiss__gm     ctx_lh_G_temporal_inf
# 160   tiss__gm     ctx_rh_G_temporal_inf
# 120   tiss__gm     ctx_lh_S_temporal_inf
# 195   tiss__gm     ctx_rh_S_temporal_inf

# 121   tiss__gm     ctx_lh_S_temporal_sup
# 196   tiss__gm     ctx_rh_S_temporal_sup

# 67   tiss__gm     ctx_lh_G_occipital_middle
# 142   tiss__gm     ctx_rh_G_occipital_middle


# Once the ROI indices are selected, they can be converted to stand-alone ROIs using
# Here is a rough plan for how to do that

# ROIidxlist = [14 31 86 161]
# ROIidxlabels = [Left-Hippocampus Right-Hippocampus ctx_lh_G_temporal_middle ctx_rh_G_temporal_middle]
# # Make the desired ROI a stand-alone file:
# for each ROIidx in the list:
#   3dcalc -a aparc.a2009s+aseg_REN_gmrois.nii.gz'[ROIidxlist[ROIidx]]' -prefix tmpROI_[ROIidxlabels[ROIidx]].nii.gz
#   3drefit -sublabel  0 [ROIidxlabels[ROIidx] tmpROI_[ROIidxlabels[ROIidx]].nii.gz
# done
# # Put all the ROIs as subbriks in one file
# 3dTcat -prefix ROIs_anatres.nii.gz tmpROI*.nii.gz

# # Downsample to the EPI resolution
# 3dfractionize -template [Aligned EPI dataset.nii.gz] -input ROIs_anatres.nii.gz \
#   -prefix tmp_ROIs_EPIres.nii.gz -clip 0.33

# # Identify voxels that are in more than one ROI and remove them from all ROIs
# 3dTstat -nzcount -prefix tmp_ROIs_EPIres_nzcount.nii.gz tmp_ROIs_EPIres.nii.gz
# 3dcalc -a tmp_ROIs_EPIres_nzcount.nii.gz -b tmp_ROIs_EPIres.nii.gz \
#    -prefix ROIs_EPIres.nii.gz -expr 'b*equals(a,1)'


# 3dROIMaker might be useful for intersecting a functional contrast with anatomical ROIs