
cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/

if [ -f WNW_tedana_sbatch.txt ]; then
    echo Deleting and recreating WNW_tedana_sbatch.txt
    rm WNW_tedana_sbatch.txt
fi
touch WNW_tedana_sbatch.txt

rootdir=`pwd`

sublist=(01 02 03 04 05 06 07 08 09 10)
runlist=(01 02 03)
echo_times="13.44 31.7 49.96"

for subidx in ${sublist[@]}; do
  subj=sub-${subidx}
  for run in ${runlist[@]}; do
cat << EOF >> WNW_tedana_sbatch.txt
 source ~/InitConda.sh; \
  cd ${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results/; \
  tedana -d pb0?.$subj.r$run.e*.volreg+orig.HEAD \
  -e $echo_times \
  --mask full_mask.$subj+orig.HEAD \
  --tedpca kic \
  --out-dir tedana_kic_r$run --convention orig
EOF
 done
done
for subidx in ${sublist[@]}; do
 subj=sub-${subidx}
 for run in ${runlist[@]}; do
cat << EOF >> WNW_tedana_sbatch.txt
 source ~/InitConda.sh; \
  cd ${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results/; \
  tedana -d pb0?.$subj.r$run.e*.volreg+orig.HEAD \
  -e $echo_times \
  --mask full_mask.$subj+orig.HEAD \
  --tedpca mdl \
  --out-dir tedana_mdl_r$run --convention orig
EOF
 done
done
for subidx in ${sublist[@]}; do
 subj=sub-${subidx}
 for run in ${runlist[@]}; do
cat << EOF >> WNW_tedana_sbatch.txt
 source ~/InitConda.sh; \
  cd ${rootdir}/${subj}/afniproc_orig/WNW/${subj}.results/; \
  tedana -d pb0?.$subj.r$run.e*.volreg+orig.HEAD \
  -e $echo_times \
  --mask full_mask.$subj+orig.HEAD \
  --tedpca kundu \
  --out-dir tedana_kundu_r$run --convention orig
EOF
  done
done


# swarm --time 6:00:00 -g 12 -t 8 -b 6 -m afni --merge-output --job-name tedana_pca WNW_tedana_sbatch.txt
