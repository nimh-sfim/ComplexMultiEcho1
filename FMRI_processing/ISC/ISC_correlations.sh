#!/bin/bash

# Script to 3dTcorrelate the warped OC files for movie/breathing

# Once the OC files are warped, then we can correlate them across subjects (inter-subject correlation)

# NOTE: sub-04's TR is 1.519, note says to consider interpolation for ISC*

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/
cd ${rootdir}
if ! [ -d IS_Correlations ]; then
    mkdir IS_Correlations
fi
out=IS_Correlations/

# Gather all of the files & organize
for dset in OC 2nd_echo ted_DN; do

    # Gather breathing files - task A (all runs)
    breathing_files_r1_warped+=`ls Nwarp_sub-??_task-breathing_run-1_${dset}.nii `
    breathing_files_r2_warped+=`ls Nwarp_sub-??_task-breathing_run-2_${dset}.nii `

    breathing_files_r1+=`ls sub-??_task-breathing_run-1_${dset}.nii `
    breathing_files_r2+=`ls sub-??_task-breathing_run-2_${dset}.nii `

    # Gathering only certain files for movie (order was counterbalanced among subjects)
    # Gather all the movie runs - task A
    task_A_run1 = 01 02 06 08 10 12 13 16 18 20 22
    for sub in $task_A_run1; do 
        for dset in OC 2nd_echo ted_DN; do
            movie_A_run1_warped+=`ls Nwarp_sub-${sub}_task-movie_run-1_${dset}.nii `
            movie_A_run1+=`ls sub-${sub}_task-movie_run-1_${dset}.nii `
        done
    done

    task_A_run2 = 03 04 05 07 09 11 15 17 19 21 23
    for sub in $task_A_run2; do 
        movie_A_run2_warped+=`ls Nwarp_sub-${sub}_task-movie_run-2_${dset}.nii `
        movie_A_run2+=`ls sub-${sub}_task-movie_run-2_${dset}.nii `
    done

    movie_A_warped+=`echo $movie_A_run1_warped $movie_A_run2_warped`
    movie_A+=`echo $movie_A_run1 $movie_A_run2`

    # Gather all the movie runs - task B
    task_B_run1 = 03 04 05 07 09 11 15 17 19 21 23
    for sub in $task_B_run1; do 
        movie_B_run1_warped+=`ls Nwarp_sub-${sub}_task-movie_run-1_${dset}.nii `
        movie_B_run1+=`ls sub-${sub}_task-movie_run-1_${dset}.nii `
    done

    task_B_run2 = 01 02 06 08 10 12 13 16 18 20 22
    for sub in $task_B_run2; do 
        movie_B_run2_warped+=`ls Nwarp_sub-${sub}_task-movie_run-2_${dset}.nii `
        movie_B_run2+=`ls sub-${sub}_task-movie_run-2_${dset}.nii `
    done

    movie_B_warped+=`echo $movie_B_run1_warped $movie_B_run2_warped`
    movie_B+=`echo $movie_B_run1 $movie_B_run2`

    # Forget about analyses for task C... for now...
    task_C_run3 = 05 11 12 16 18 21
    for sub in $task_C_run3; do 
        movie_C_run3_warped+=`ls Nwarp_sub-${sub}_task-movie_run-3_${dset}.nii `
        movie_C_run3+=`ls sub-${sub}_task-movie_run-3_${dset}.nii `
    done

    movie_C_warped+=`echo $movie_C_run3_warped `
    movie_C+=`echo $movie_C_run3 `

done

# Native Correlations - Within subjects
# movie A vs movie B
for file in `echo $movie_A`
    subject=${file:0:6}
    for file2 in `echo $movie_B`
        subject2=${file2:0:6}
        # check if subjects are equal & task (last of filename) is equal (only want to correlate data of similar types)
        if [ $subject == $subject2 ] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# movie A vs resp A1
for file in `echo $movie_A`
    subject=${file:0:6}
    for file2 in `echo $breathing_files_r1`
        subject2=${file2:0:6}
        if [ $subject == $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# movie B vs resp A1
for file in `echo $movie_B`
    subject=${file:0:6}
    for file2 in `echo $breathing_files_r1`
        subject2=${file2:0:6}
        if [ $subject == $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# resp A1 vs resp A2
for file in `echo $breathing_files_r1`
    subject=${file:0:6}
    for file2 in `echo $breathing_files_r2`
        subject2=${file2:0:6}
        if [ $subject == $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# Afterwards: Nwarpapply to FisherZ maps (THEN group statistics)

# Group space correlations - Between Subjects (Warped)

# movie A vs movie B 
for file in `echo $movie_A_warped`
    subject=${file:0:6}
    for file2 in `echo $movie_B_warped`
        subject2=${file2:0:6}
        if [ $subject != $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# movie B vs movie A 
for file in `echo $movie_B_warped`
    subject=${file:0:6}
    for file2 in `echo $movie_A_warped`
        subject2=${file2:0:6}
        if [ $subject != $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# resp A1 vs resp A1 
for file in `echo $breathing_files_r1_warped`
    subject=${file:0:6}
    for file2 in `echo $breathing_files_r1_warped`
        subject2=${file2:0:6}
        if [ $subject != $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done

# resp A2 vs resp A2 
for file in `echo $breathing_files_r2_warped`
    subject=${file:0:6}
    for file2 in `echo $breathing_files_r2_warped`
        subject2=${file2:0:6}
        if [ $subject != $subject2] && [ ${file::-6} == ${file2::-6} ]; then
            3dTcorrelate -pearson -Fisher -polort 4 -prefix $out/Tcorr_${file::-4}_X_${file2::-4}.nii $file $file2
        fi
    done
done
