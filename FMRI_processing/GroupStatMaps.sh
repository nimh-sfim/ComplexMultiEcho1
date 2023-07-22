#!/bin/sh

# sbatch --gres=lscratch:500 -c 16 -J GroupMVM --mail-type=ALL -t 2:00:00 --mem=16G --partition=quick,norm GroupStatMaps.sh

module load afni
module load R/4.1.0


rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir="${rootdir}/GroupResults/GroupMaps/sbj_maps"

cd $GroupDir

# GLMlist=(e2_mot_CSF OC_mot_CSF orthtedana_mot_csf combined_regressors)
GLMlist=(CR_tedana_v23_c70_kundu_wnw RR_tedana_v23_c70_kundu_wnw reg_tedana_v23_c70_kundu_wnw)

# To run group analysis. 
for GLM in ${GLMlist[@]}; do
   3dMVM -prefix ../sm.WNW_VA_Group_${GLM}.nii.gz -jobs 16                                \
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
   01   audio  word    sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   01   audio  nonword sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   01   visual word    sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   01   visual nonword sm.stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   02   audio  word    sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   02   audio  nonword sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   02   visual word    sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   02   visual nonword sm.stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   03   audio  word    sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   03   audio  nonword sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   03   visual word    sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   03   visual nonword sm.stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   04   audio  word    sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   04   audio  nonword sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   04   visual word    sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   04   visual nonword sm.stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   05   audio  word    sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   05   audio  nonword sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   05   visual word    sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   05   visual nonword sm.stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   06   audio  word    sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   06   audio  nonword sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   06   visual word    sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   06   visual nonword sm.stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   07   audio  word    sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   07   audio  nonword sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   07   visual word    sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   07   visual nonword sm.stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   08   audio  word    sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   08   audio  nonword sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   08   visual word    sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   08   visual nonword sm.stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   09   audio  word    sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   09   audio  nonword sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   09   visual word    sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   09   visual nonword sm.stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   10   audio  word    sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   10   audio  nonword sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   10   visual word    sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   10   visual nonword sm.stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   11   audio  word    sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   11   audio  nonword sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   11   visual word    sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   11   visual nonword sm.stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   12   audio  word    sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   12   audio  nonword sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   12   visual word    sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   12   visual nonword sm.stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   13   audio  word    sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   13   audio  nonword sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   13   visual word    sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   13   visual nonword sm.stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   14   audio  word    sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   14   audio  nonword sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   14   visual word    sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   14   visual nonword sm.stats.sub-14.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   15   audio  word    sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   15   audio  nonword sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   15   visual word    sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   15   visual nonword sm.stats.sub-15.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   16   audio  word    sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   16   audio  nonword sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   16   visual word    sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   16   visual nonword sm.stats.sub-16.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   17   audio  word    sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   17   audio  nonword sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   17   visual word    sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   17   visual nonword sm.stats.sub-17.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   18   audio  word    sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   18   audio  nonword sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   18   visual word    sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   18   visual nonword sm.stats.sub-18.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   19   audio  word    sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   19   audio  nonword sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   19   visual word    sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   19   visual nonword sm.stats.sub-19.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   20   audio  word    sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   20   audio  nonword sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   20   visual word    sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   20   visual nonword sm.stats.sub-20.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   21   audio  word    sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   21   audio  nonword sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   21   visual word    sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   21   visual nonword sm.stats.sub-21.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   22   audio  word    sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   22   audio  nonword sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   22   visual word    sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   22   visual nonword sm.stats.sub-22.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   23   audio  word    sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   23   audio  nonword sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   23   visual word    sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   23   visual nonword sm.stats.sub-23.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   24   audio  word    sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   24   audio  nonword sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   24   visual word    sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   24   visual nonword sm.stats.sub-24.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
   25   audio  word    sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
   25   audio  nonword sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
   25   visual word    sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
   25   visual nonword sm.stats.sub-25.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   


#    3dMVM -prefix ../WNW_VA_Group_${GLM}.nii.gz -jobs 16                              \
#    -overwrite                                                                             \
#    -bsVars 1                                                                              \
#    -wsVars "sense*wnw"                                                                    \
#    -SS_type 3                                                                             \
#    -num_glt 4                                                                             \
#    -mask ../GroupMask.nii.gz                                                       \
#    -gltLabel 1 Word-NonWord -gltCode 1 'wnw : 1*word -1*nonword'                           \
#    -gltLabel 2 Vis-Aud -gltCode 2 'sense : 1*visual -1*audio'                              \
#    -gltLabel 3 Vis_Word-NonWord -gltCode 3 'sense : 1*visual wnw : 1*word -1*nonword'      \
#    -gltLabel 4 Aud_Word-NonWord -gltCode 4 'sense : 1*audio wnw : 1*word -1*nonword'       \
#    -dataTable                                                                             \
#    Subj  sense  wnw     InputFile                                                         \
#    01   audio  word    stats.sub-01.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    01   audio  nonword stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    01   visual word    stats.sub-01.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    01   visual nonword stats.sub-01.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    02   audio  word    stats.sub-02.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    02   audio  nonword stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    02   visual word    stats.sub-02.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    02   visual nonword stats.sub-02.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    03   audio  word    stats.sub-03.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    03   audio  nonword stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    03   visual word    stats.sub-03.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    03   visual nonword stats.sub-03.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    04   audio  word    stats.sub-04.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    04   audio  nonword stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    04   visual word    stats.sub-04.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    04   visual nonword stats.sub-04.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    05   audio  word    stats.sub-05.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    05   audio  nonword stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    05   visual word    stats.sub-05.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    05   visual nonword stats.sub-05.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    06   audio  word    stats.sub-06.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    06   audio  nonword stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    06   visual word    stats.sub-06.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    06   visual nonword stats.sub-06.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    07   audio  word    stats.sub-07.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    07   audio  nonword stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    07   visual word    stats.sub-07.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    07   visual nonword stats.sub-07.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    08   audio  word    stats.sub-08.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    08   audio  nonword stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    08   visual word    stats.sub-08.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    08   visual nonword stats.sub-08.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    09   audio  word    stats.sub-09.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    09   audio  nonword stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    09   visual word    stats.sub-09.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    09   visual nonword stats.sub-09.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    10   audio  word    stats.sub-10.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    10   audio  nonword stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    10   visual word    stats.sub-10.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    10   visual nonword stats.sub-10.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    11   audio  word    stats.sub-11.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    11   audio  nonword stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    11   visual word    stats.sub-11.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    11   visual nonword stats.sub-11.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    12   audio  word    stats.sub-12.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    12   audio  nonword stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    12   visual word    stats.sub-12.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    12   visual nonword stats.sub-12.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   \
#    13   audio  word    stats.sub-13.${GLM}_REML_tlrc.nii.gz['AudWord#0_Coef']      \
#    13   audio  nonword stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalAudWord#0_Coef']   \
#    13   visual word    stats.sub-13.${GLM}_REML_tlrc.nii.gz['VisWord#0_Coef']      \
#    13   visual nonword stats.sub-13.${GLM}_REML_tlrc.nii.gz['FalVisWord#0_Coef']   
done
