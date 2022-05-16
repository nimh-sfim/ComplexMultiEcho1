# The nii.gz files from tedana are read as in tlrc space even though they are in orig space
# The following code should correct them to orig space


sublist=(01 02 03 04 05 06 07 08 09 10 11 12 13)

runlist=(01 02 03)

tedanalist=(tedana_c75)



for subidx in ${sublist[@]}; do
 subj=sub-${subidx}
 for tedanaver in ${tedanalist[@]}; do
  for run in ${runlist[@]}; do

   cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj}/afniproc_orig/WNW/${subj}.results/${tedanaver}_r${run}
   echo `pwd`
   for file in `ls *.nii.gz`; do
     echo $file
     template=`3dAttribute TEMPLATE_SPACE dn_ts_OC.nii.gz`
     if [ $template = 'TLRC~' ]; then
       3drefit -view orig -space ORIG $file
     else
       echo $file already orig
     fi
   done
  done
 done
done
