#!/bin/sh

# sbatch --gres=lscratch:500 -c 16 -J GroupMVM --mail-type=ALL -t 12:00:00 --mem=16G --partition=quick,norm GroupStatMaps.sh

module load afni
module load R


rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir="${rootdir}/GroupResults/GroupMaps/Final_WNW_3dMVM_Group_Maps"
sbjmaps="${rootdir}/GroupResults/GroupMaps/sbj_maps/"

if ! [ -d $GroupDir ]; then
   mkdir $GroupDir
fi

cd $GroupDir

GLMlist=(second_echo_mot_csf_v23_c70_kundu_wnw optimally_combined_mot_csf_v23_c70_kundu_wnw tedana_mot_csf_v23_c70_kundu_wnw combined_regressors_v23_c70_kundu_wnw)

# To run group analysis. 
# This script calls 3dMVM on the smoothed statistical maps you created before (per subject and GLM)
for GLM in ${GLMlist[@]}; do
   3dMVM -prefix ./sm.WNW_VA_Group_${GLM}.nii.gz -jobs 16                                \
   -overwrite                                                                             \
   -bsVars 1                                                                              \
   -wsVars "sense*wnw"                                                                    \
   -SS_type 3                                                                             \
   -num_glt 4                                                                             \
   -mask ../GroupMask.nii.gz                                                              \
   -gltLabel 1 Word-NonWord -gltCode 1 'wnw : 1*word -1*nonword'                          \
   -gltLabel 2 Vis-Aud -gltCode 2 'sense : 1*visual -1*audio'                             \
   -gltLabel 3 Vis_Word-NonWord -gltCode 3 'sense : 1*visual wnw : 1*word -1*nonword'     \
   -gltLabel 4 Aud_Word-NonWord -gltCode 4 'sense : 1*audio wnw : 1*word -1*nonword'      \
   -dataTable                                                                             \
   Subj  sense  wnw     InputFile                                                         \
   01   audio  word    ${sbjmaps}sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   01   audio  nonword ${sbjmaps}sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   01   visual word    ${sbjmaps}sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   01   visual nonword ${sbjmaps}sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   02   audio  word    ${sbjmaps}sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   02   audio  nonword ${sbjmaps}sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   02   visual word    ${sbjmaps}sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   02   visual nonword ${sbjmaps}sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   03   audio  word    ${sbjmaps}sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   03   audio  nonword ${sbjmaps}sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   03   visual word    ${sbjmaps}sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   03   visual nonword ${sbjmaps}sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   04   audio  word    ${sbjmaps}sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   04   audio  nonword ${sbjmaps}sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   04   visual word    ${sbjmaps}sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   04   visual nonword ${sbjmaps}sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   05   audio  word    ${sbjmaps}sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   05   audio  nonword ${sbjmaps}sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   05   visual word    ${sbjmaps}sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   05   visual nonword ${sbjmaps}sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   06   audio  word    ${sbjmaps}sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   06   audio  nonword ${sbjmaps}sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   06   visual word    ${sbjmaps}sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   06   visual nonword ${sbjmaps}sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   07   audio  word    ${sbjmaps}sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   07   audio  nonword ${sbjmaps}sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   07   visual word    ${sbjmaps}sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   07   visual nonword ${sbjmaps}sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   08   audio  word    ${sbjmaps}sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   08   audio  nonword ${sbjmaps}sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   08   visual word    ${sbjmaps}sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   08   visual nonword ${sbjmaps}sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   09   audio  word    ${sbjmaps}sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   09   audio  nonword ${sbjmaps}sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   09   visual word    ${sbjmaps}sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   09   visual nonword ${sbjmaps}sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   10   audio  word    ${sbjmaps}sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   10   audio  nonword ${sbjmaps}sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   10   visual word    ${sbjmaps}sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   10   visual nonword ${sbjmaps}sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   11   audio  word    ${sbjmaps}sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   11   audio  nonword ${sbjmaps}sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   11   visual word    ${sbjmaps}sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   11   visual nonword ${sbjmaps}sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   12   audio  word    ${sbjmaps}sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   12   audio  nonword ${sbjmaps}sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   12   visual word    ${sbjmaps}sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   12   visual nonword ${sbjmaps}sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   13   audio  word    ${sbjmaps}sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   13   audio  nonword ${sbjmaps}sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   13   visual word    ${sbjmaps}sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   13   visual nonword ${sbjmaps}sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   14   audio  word    ${sbjmaps}sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   14   audio  nonword ${sbjmaps}sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   14   visual word    ${sbjmaps}sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   14   visual nonword ${sbjmaps}sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   15   audio  word    ${sbjmaps}sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   15   audio  nonword ${sbjmaps}sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   15   visual word    ${sbjmaps}sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   15   visual nonword ${sbjmaps}sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   16   audio  word    ${sbjmaps}sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   16   audio  nonword ${sbjmaps}sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   16   visual word    ${sbjmaps}sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   16   visual nonword ${sbjmaps}sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   17   audio  word    ${sbjmaps}sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   17   audio  nonword ${sbjmaps}sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   17   visual word    ${sbjmaps}sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   17   visual nonword ${sbjmaps}sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   18   audio  word    ${sbjmaps}sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   18   audio  nonword ${sbjmaps}sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   18   visual word    ${sbjmaps}sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   18   visual nonword ${sbjmaps}sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   19   audio  word    ${sbjmaps}sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   19   audio  nonword ${sbjmaps}sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   19   visual word    ${sbjmaps}sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   19   visual nonword ${sbjmaps}sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   20   audio  word    ${sbjmaps}sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   20   audio  nonword ${sbjmaps}sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   20   visual word    ${sbjmaps}sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   20   visual nonword ${sbjmaps}sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   21   audio  word    ${sbjmaps}sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   21   audio  nonword ${sbjmaps}sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   21   visual word    ${sbjmaps}sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   21   visual nonword ${sbjmaps}sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   22   audio  word    ${sbjmaps}sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   22   audio  nonword ${sbjmaps}sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   22   visual word    ${sbjmaps}sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   22   visual nonword ${sbjmaps}sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   23   audio  word    ${sbjmaps}sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   23   audio  nonword ${sbjmaps}sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   23   visual word    ${sbjmaps}sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   23   visual nonword ${sbjmaps}sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   24   audio  word    ${sbjmaps}sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   24   audio  nonword ${sbjmaps}sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   24   visual word    ${sbjmaps}sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   24   visual nonword ${sbjmaps}sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   25   audio  word    ${sbjmaps}sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   25   audio  nonword ${sbjmaps}sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   25   visual word    ${sbjmaps}sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   25   visual nonword ${sbjmaps}sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   
done
