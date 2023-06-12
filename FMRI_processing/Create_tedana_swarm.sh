# tedana was run as part of afni_proc. 
# This script reruns tedana with the newest version (v23.0.1 with added logging of the MA-PCA subsampling value)
# Component selection still seems to be an issue with these data. For each run, two component selection options
# are used: MA=PCA with the KIC criterion and a fixed number of 70 components for each run.
# The fixed components is not ideal, but it should allow ICA to converge for all runs and will avoid runs
# where the estimate from KIC is implausibly too large or small



cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/

swarmname=tedana_rerun_swarm.txt
if [ -f $swarmname ]; then
    echo Deleting and recreating WNW_tedana_sbatch.txt
    rm $swarmname
fi
touch $swarmname

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
# rootdir=/Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data

numsbj=25

echo_times="13.44 31.7 49.96"

for subidx in $(seq -f "%02g" 1 $numsbj); do
  subj=sub-${subidx}
  rundir=( "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-1/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/breathing_run-1/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/breathing_run-2/${subj}.results"           
          "${rootdir}/${subj}/afniproc_orig/breathing_run-3/${subj}.results" )
  maskname="full_mask.$subj+orig.HEAD"
  runnum=( 01 02 03 01 01 01 01 01 01)

  echo ${rundir[@]}

  for ridx in $(seq -f "%g" 0 8); do
     if [ -d ${rundir[$ridx]} ]; then
       echo "Setting up ${rundir[$ridx]}/pb0?.$subj.r${runnum[$ridx]}.e??.volreg+orig.HEAD"
cat << EOF >> $swarmname
source ~/InitConda.sh; cd ${rundir[$ridx]}; \\
  tedana -d pb0?.$subj.r${runnum[$ridx]}.e??.volreg+orig.HEAD \\
    --tedpca 70 --out-dir tedana_v23_c70_kundu_r${runnum[$ridx]} \\
    --tree kundu -e $echo_times --mask $maskname --overwrite; \\
  tedana -d pb0?.$subj.r${runnum[$ridx]}.e??.volreg+orig.HEAD \\
    --tedpca kic --out-dir tedana_v23_kic_kundu_r${runnum[$ridx]} \\
    --tree kundu -e $echo_times --mask $maskname --overwrite; \\
  tedana -d pb0?.$subj.r${runnum[$ridx]}.e??.volreg+orig.HEAD \\
    --mix tedana_v23_kic_kundu_r${runnum[$ridx]}/desc-ICA_mixing.tsv \\
    --out-dir tedana_v23_kic_minimal_r${runnum[$ridx]} \\
    --tree minimal -e $echo_times --mask $maskname --overwrite; \\
  tedana -d pb0?.$subj.r${runnum[$ridx]}.e??.volreg+orig.HEAD \\
    --mix tedana_v23_c70_kundu_r${runnum[$ridx]}/desc-ICA_mixing.tsv \\
    --out-dir tedana_v23_c70_minimal_r${runnum[$ridx]} \\
    --tree minimal -e $echo_times --mask $maskname  --overwrite
EOF
     fi
  done
done


# Don't want to accidentally run
# swarm -f $swarmname -g 24 -t 8 -b 4 --merge-output --job-name tedana23 --logdir swarm_calls --time 01:00:00 --partition quick,norm 


# Checking outputs after swarm is run
for subidx in $(seq -f "%02g" 1 $numsbj); do
  subj=sub-${subidx}
  rundir=( "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-1/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/movie_run-2/${subj}.results" 
          "${rootdir}/${subj}/afniproc_orig/breathing_run-1/${subj}.results"
          "${rootdir}/${subj}/afniproc_orig/breathing_run-2/${subj}.results"           
          "${rootdir}/${subj}/afniproc_orig/breathing_run-3/${subj}.results" )
  maskname="full_mask.$subj+orig.HEAD"
  runnum=( 01 02 03 01 01 01 01 01 01)

  # echo ${rundir[@]}

  for ridx in $(seq -f "%g" 0 8); do
     if [ -d ${rundir[$ridx]} ]; then
       if [ -f ${rundir[$ridx]}/tedana_v23_kic_kundu_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz ] ; then
         tmp=`ls -lh ${rundir[$ridx]}/tedana_v23_kic_kundu_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz | awk '{print $6  $5  $4  $7}'`
         echo $tmp ${rundir[$ridx]} kic kundu
       else
         echo Not found ${rundir[$ridx]} kic kundu
       fi
       if [ -f ${rundir[$ridx]}/tedana_v23_kic_minimal_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz ] ; then
         tmp=`ls -lh ${rundir[$ridx]}/tedana_v23_kic_minimal_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz | awk '{print $6  $5  $4  $7}'`
         echo $tmp ${rundir[$ridx]} kic minimal
       else
         echo Not found ${rundir[$ridx]} kic minimal
       fi
       if [ -f ${rundir[$ridx]}/tedana_v23_c70_kundu_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz ] ; then
         tmp=`ls -lh ${rundir[$ridx]}/tedana_v23_c70_kundu_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz | awk '{print $6  $5  $4  $7}'`
         echo $tmp ${rundir[$ridx]} c70 kundu
       else
         echo Not found ${rundir[$ridx]} c70 kundu
       fi
       if [ -f ${rundir[$ridx]}/tedana_v23_c70_minimal_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz ] ; then
         tmp=`ls -lh ${rundir[$ridx]}/tedana_v23_c70_minimal_r${runnum[$ridx]}/desc-optcomDenoised_bold.nii.gz | awk '{print $6  $5  $4  $7}'`
         echo $tmp ${rundir[$ridx]} c70 minimal
       else
         echo Not found ${rundir[$ridx]} c70 minimal
       fi
    fi
  done
done
