#!/bin/bash

# Script to 3dTcorrelate the movie/breathing runs

# voxel-wise ISC within & between 2 subjects

# Once the OC files are warped, then we can correlate them across subjects (inter-subject correlation)

# NOTE: sub-04's TR is 1.519, note says to consider interpolation for ISC*

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
warpDir=${rootdir}GroupResults/GroupISC/warped_files/
cd ${rootdir}GroupResults/GroupISC/
if ! [ -d IS_Correlations ]; then
    mkdir IS_Correlations
fi
cd IS_Correlations/

# Native Correlations - Within subjects
if ! [ -d Within_subjects ]; then
    mkdir Within_subjects/
fi

# Gather all of the files & organize

# Gather breathing files - task A (all runs)
for sub in {01..23}; do
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/breathing_run-2/ ]; then
        tmpr2=` ls ${rootdir}sub-${sub}/afniproc_orig/breathing_run-2/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/breathing_run-2/sub-${sub}.results/*combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/breathing_run-2/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
    elif [ -d ${rootdir}sub-${sub}/afniproc_orig/breathing_run-1/ ]; then
        tmpr1=` ls ${rootdir}sub-${sub}/afniproc_orig/breathing_run-1/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/breathing_run-1/sub-${sub}.results/*combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/breathing_run-1/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
    fi
    breathing_files_r2+=(" $tmpr2 ")
    breathing_files_r1+=(" $tmpr1 ")
done

# Gathering only certain files for movie (order was counterbalanced among subjects)
# Gather all the movie runs - task A
task_A_run1="01 02 06 08 10 12 13 16 18 20 22"
for sub in $task_A_run1; do 
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/ ]; then
        tmp=` ls ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/*.sub-${sub}.r01.combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
        movie_A_run1+=" $tmp "
    fi
done

task_A_run2="03 04 05 07 09 11 15 17 19 21 23"
for sub in $task_A_run2; do 
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/ ]; then
        tmp=` ls ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/*.sub-${sub}.r01.combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
        movie_A_run2+=" $tmp "
    fi
done

movie_A=("$movie_A_run1 $movie_A_run2")

# Gather all the movie runs - task B
task_B_run1="03 04 05 07 09 11 15 17 19 21 23"
for sub in $task_B_run1; do 
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/ ]; then
        tmp=` ls ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/*.sub-${sub}.r01.combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-1/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
        movie_B_run1+=" $tmp "
    fi
done

task_B_run2="01 02 06 08 10 12 13 16 18 20 22"
for sub in $task_B_run2; do 
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/ ]; then
        tmp=` ls ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/*.sub-${sub}.r01.combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-2/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
        movie_B_run2+=" $tmp "
    fi
done

movie_B=("$movie_B_run1 $movie_B_run2")

# Forget about analyses for task C... for now...
task_C_run3="05 11 12 16 18 21"
for sub in $task_C_run3; do 
    if [ -d ${rootdir}sub-${sub}/afniproc_orig/movie_run-3/ ]; then
        tmp=` ls ${rootdir}sub-${sub}/afniproc_orig/movie_run-3/sub-${sub}.results/pb0?.sub-${sub}.r01.e02.volreg+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-3/sub-${sub}.results/*.sub-${sub}.r01.combine+orig.HEAD ${rootdir}sub-${sub}/afniproc_orig/movie_run-3/sub-${sub}.results/tedana_r01/dn_ts_OC.nii.gz `
        movie_C_run3+=" $tmp "
    fi
done

movie_C=("$movie_C_run3")


movie_A_x_movie_B() {
    # movie A vs movie B
    for file in $movie_A; do
        subject=`basename ${file:0:58}`
        fname1="movie_A"
        for file2 in $movie_B; do
            subject2=`basename ${file2:0:58}`
            fname2="movie_B"
            # check if subjects are equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" == "$subject2" ] && [ "${file: -17}" == "${file2: -17}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -17}, ${file2: -17}
                if [ ${file: -17} == ".volreg+orig.HEAD" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -17} == "combine+orig.HEAD" ]; then 
                    suffix="OC"
                elif [ ${file: -17} == "1/dn_ts_OC.nii.gz" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Within_subjects/Tcorr_${subject}_task-${fname1}_x_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

movie_A_x_resp_A1() {
    # movie A vs resp A1
    for file in $movie_A; do
        subject=`basename ${file:0:58}`
        fname1="movie_A"
        for file2 in $breathing_files_r1; do
            subject2=`basename ${file2:0:58}`
            fname2="resp_A1"
            # check if subjects are equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" == "$subject2" ] && [ "${file: -17}" == "${file2: -17}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -17}, ${file2: -17}
                if [ ${file: -17} == ".volreg+orig.HEAD" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -17} == "combine+orig.HEAD" ]; then 
                    suffix="OC"
                elif [ ${file: -17} == "1/dn_ts_OC.nii.gz" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Within_subjects/Tcorr_${subject}_task-${fname1}_x_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

movie_B_x_resp_A1() {
    # movie B vs resp A1
    for file in $movie_B; do
        subject=`basename ${file:0:58}`
        fname1="movie_B"
        for file2 in $breathing_files_r1; do
            subject2=`basename ${file2:0:58}`
            fname2="resp_A1"
            # check if subjects are equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" == "$subject2" ] && [ "${file: -17}" == "${file2: -17}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -17}, ${file2: -17}
                if [ ${file: -17} == ".volreg+orig.HEAD" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -17} == "combine+orig.HEAD" ]; then 
                    suffix="OC"
                elif [ ${file: -17} == "1/dn_ts_OC.nii.gz" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Within_subjects/Tcorr_${subject}_task-${fname1}_x_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

resp_A1_x_resp_A2() {
    # resp A1 vs resp A2
    for file in $breathing_files_r1; do
        subject=`basename ${file:0:58}`
        fname1="resp_A1"
        for file2 in $breathing_files_r2; do
            subject2=`basename ${file2:0:58}`
            fname2="resp_A2"
            # check if subjects are equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" == "$subject2" ] && [ "${file: -17}" == "${file2: -17}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -17}, ${file2: -17}
                if [ ${file: -17} == ".volreg+orig.HEAD" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -17} == "combine+orig.HEAD" ]; then 
                    suffix="OC"
                elif [ ${file: -17} == "1/dn_ts_OC.nii.gz" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Within_subjects/Tcorr_${subject}_task-${fname1}_x_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

# Afterwards: Run warping_FisherZs.sh for each subject
# THEN 3dttest++

# Group space correlations - Between Subjects (Warped)

# if ! [ -d Between_subjects ]; then
#     mkdir Between_subjects/
# fi

# # Gather all of the files & organize

# # Gather breathing files - task A (all runs)
# for sub in {01..23}; do
#     tmpr1=` ls ${warpDir}Nwarp_sub-??_task-breathing_run-1_*.nii `
#     tmpr2=` ls ${warpDir}Nwarp_sub-??_task-breathing_run-2_*.nii `
#     breathing_files_r1_warped=" $tmpr1 "
#     breathing_files_r2_warped=" $tmpr2 "
# done

# # Gathering only certain files for movie (order was counterbalanced among subjects)
# # Gather all the movie runs - task A
# task_A_run1="01 02 06 08 10 12 13 16 18 20 22"
# for sub in $task_A_run1; do 
#     tmp=` ls ${warpDir}Nwarp_sub-${sub}_task-movie_run-1_*.nii `
#     movie_A_run1_warped+=" $tmp "
# done

# task_A_run2="03 04 05 07 09 11 15 17 19 21 23"
# for sub in $task_A_run2; do 
#     tmp=` ls ${warpDir}Nwarp_sub-${sub}_task-movie_run-2_*.nii `
#     movie_A_run2_warped+=" $tmp "
# done

# movie_A_warped="$movie_A_run1_warped $movie_A_run2_warped"

# # Gather all the movie runs - task B
# task_B_run1="03 04 05 07 09 11 15 17 19 21 23"
# for sub in $task_B_run1; do 
#     tmp=` ls ${warpDir}Nwarp_sub-${sub}_task-movie_run-1_*.nii `
#     movie_B_run1_warped+=" $tmp "
# done

# task_B_run2="01 02 06 08 10 12 13 16 18 20 22"
# for sub in $task_B_run2; do 
#     tmp=` ls ${warpDir}Nwarp_sub-${sub}_task-movie_run-2_*.nii `
#     movie_B_run2_warped+=" $tmp "
# done

# movie_B_warped="$movie_B_run1_warped $movie_B_run2_warped"

# # Forget about analyses for task C... for now...
# task_C_run3="05 11 12 16 18 21"
# for sub in $task_C_run3; do 
#     tmp=` ls ${warpDir}Nwarp_sub-${sub}_task-movie_run-3_*.nii `
#     movie_C_run3_warped+=" $tmp "
# done

# movie_C_warped="$movie_C_run3_warped"

movie_A_x_movie_B_between() {
    # movie A vs movie B 
    for file in $movie_A_warped; do
        base=`basename $file`; subject=${base:6:6}
        fname1="movie_A"
        for file2 in $movie_B_warped; do
            base2=`basename $file2`; subject2=${base2:6:6}
            fname2="movie_B"
            # check if subjects are NOT equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" != "$subject2" ] && [ "${file: -6}" == "${file2: -6}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -6}, ${file2: -6}
                if [ ${file: -6} == "ho.nii" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -6} == "OC.nii" ]; then 
                    suffix="OC"
                elif [ ${file: -6} == "DN.nii" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Between_subjects/Tcorr_Nwarp_${subject}_task-${fname1}_x_${subject2}_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

movie_B_x_movie_A_between() {
    # movie B vs movie A 
    for file in $movie_B_warped; do
        base=`basename $file`; subject=${base:6:6}
        fname1="movie_B"
        for file2 in $movie_A_warped; do
            base2=`basename $file2`; subject2=${base2:6:6}
            fname2="movie_A"
            # check if subjects are NOT equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" != "$subject2" ] && [ "${file: -6}" == "${file2: -6}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -6}, ${file2: -6}
                if [ ${file: -6} == "ho.nii" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -6} == "OC.nii" ]; then 
                    suffix="OC"
                elif [ ${file: -6} == "DN.nii" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Between_subjects/Tcorr_Nwarp_${subject}_task-${fname1}_x_${subject2}_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

resp_A1_x_resp_A1_between() {
    # resp A1 vs resp A1 
    for file in $breathing_files_r1_warped; do
        base=`basename $file`; subject=${base:6:6}
        fname1="resp_A1"
        for file2 in $breathing_files_r1_warped; do
            base2=`basename $file2`; subject2=${base2:6:6}
            fname2="resp_A1"
            # check if subjects are NOT equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" != "$subject2" ] && [ "${file: -6}" == "${file2: -6}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -6}, ${file2: -6}
                if [ ${file: -6} == "ho.nii" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -6} == "OC.nii" ]; then 
                    suffix="OC"
                elif [ ${file: -6} == "DN.nii" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Between_subjects/Tcorr_Nwarp_${subject}_task-${fname1}_x_${subject2}_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}

resp_A2_x_resp_A2_between() {
    # resp A2 vs resp A2 
    for file in $breathing_files_r2_warped; do
        base=`basename $file`; subject=${base:6:6}
        fname1="resp_A2"
        for file2 in $breathing_files_r2_warped; do
            base2=`basename $file2`; subject2=${base2:6:6}
            fname2="resp_A2"
            # check if subjects are NOT equal & task (last of filename) is equal (only want to correlate data of similar types)
            if [ "$subject" != "$subject2" ] && [ "${file: -6}" == "${file2: -6}" ]; then
                echo $subject, $subject2, $fname1, $fname2, ${file: -6}, ${file2: -6}
                if [ ${file: -6} == "ho.nii" ]; then
                    suffix="2nd_echo"
                elif [ ${file: -6} == "OC.nii" ]; then 
                    suffix="OC"
                elif [ ${file: -6} == "DN.nii" ]; then 
                    suffix="ted_DN"
                fi
                3dTcorrelate -pearson -Fisher -polort 4 -prefix Between_subjects/Tcorr_Nwarp_${subject}_task-${fname1}_x_${subject2}_${fname2}_${suffix}.nii $file $file2
            fi
        done
    done
}
# THEN 3dISC

# allows you to call the functions from command line (as the 1st argument)
case "$1" in
    (movie_A_x_movie_B) 
      movie_A_x_movie_B
      exit 0
      ;;
    (movie_A_x_resp_A1)
      movie_A_x_resp_A1
      exit 0
      ;;
    (movie_B_x_resp_A1)
      movie_B_x_resp_A1
      exit 0
      ;;
    (resp_A1_x_resp_A2)
      resp_A1_x_resp_A2
      exit 0
      ;;
    (movie_A_x_movie_B_between) 
      movie_A_x_movie_B_between
      exit 0
      ;;
    (movie_B_x_movie_A_between)
      movie_B_x_movie_A_between
      exit 0
      ;;
    (resp_A1_x_resp_A1_between)
      resp_A1_x_resp_A1_between
      exit 0
      ;;
    (resp_A2_x_resp_A2_between)
      resp_A2_x_resp_A2_between
      exit 0
      ;;
esac

# Run Analyses in swarm file
# Within
# bash ISC_correlations.sh movie_A_x_movie_B
# bash ISC_correlations.sh movie_A_x_resp_A1
# bash ISC_correlations.sh movie_B_x_resp_A1
# bash ISC_correlations.sh resp_A1_x_resp_A2

# Between
# bash ISC_correlations.sh movie_A_x_movie_B_between
# bash ISC_correlations.sh movie_B_x_movie_A_between
# bash ISC_correlations.sh resp_A1_x_resp_A1_between
# bash ISC_correlations.sh resp_A2_x_resp_A2_between



