#!/bin/bash

# Template to warp all subject EPIs to the same grid template
# This group template will be used for the ISC correlations
# Ultimately, it will warp breathing/movie runs to same template for all subjects

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir=${rootdir}/GroupResults/GroupMaps
cd ${rootdir}/GroupResults/
if ! [ -d GroupISC/warped_files/ ]; then
    mkdir GroupISC/warped_files/
fi
cd GroupISC/warped_files/

orig_warped() {

    mkdir -p orig_warped/; cd orig_warped/;
    
    for task in 'breathing' 'movie'; do

        for run in 1 2 3; do

            if [ -d ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/ ]; then 
                # All files = middle echo (2nd echo), OC, and tedana denoised datasets for all movie/breathing runs
                second_echo=`ls ${rootdir}/GroupResults/GroupISC/group_mask/${subject}_task-${task}_run-${run}_2nd_echo_masked.nii.gz`
                ted_DN=`ls ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/tedana_r01/dn_ts_OC.nii.gz`
                OC=`ls ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/tedana_r01/ts_OC.nii.gz`

                # 1 source map for each dtype (2nd echo, OC, and tedana DN)
                for dtype in 'second_echo' 'OC' 'ted_DN'; do
                    # create the source list & prefix list
                    if [ $dtype == 'second_echo' ]; then
                        source=$second_echo
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_2nd_echo.nii";
                    elif [ $dtype == 'OC' ]; then
                        source=$OC
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_OC.nii"
                    elif [ $dtype == 'ted_DN' ]; then
                        source=$ted_DN
                        prefix="Nwarp_${subject}_task-${task}_run-${run}_ted_DN.nii";
                    fi

                    # 3dNWarp: each subject uses its own affine matrix file to warp to subject-01's base
                    # Run 3dNWarpApply with multiple input files & multiple output files
                    # 3dNwarpApply command - takes all the datasets for movie/breathing runs as source & uses the affine matrix (in 4D & 1D form) for each subject to warp those datasets to the alignment EPI grid template base (sub-01 in this case), then outputs an aligned OC file for each subject
                    3dNwarpApply -overwrite -nwarp "${rootdir}/${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}/${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
                    -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
                    -source $source \
                    -prefix $prefix
                done
            fi
        done
    done
}

fishwarp_movie_A_x_movie_B() {
    rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
    mkdir -p FisherZs_warped/movie_A_x_movie_B; cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/warped_files/FisherZs_warped/movie_A_x_movie_B;

    fisherzs=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/movie_A_x_movie_B/*.nii`

    for f in $fisherzs; do
        basef=`basename $f`; subject=${basef:6:6};
        prefix="Nwarp_${f##*/}"
        
        echo $subject;

        3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -source $f \
        -prefix $prefix
    done
}

fishwarp_movie_A_x_resp_A1() {
    rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
    mkdir -p FisherZs_warped/movie_A_x_resp_A1; cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/warped_files/FisherZs_warped/movie_A_x_resp_A1;

    fisherzs=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/movie_A_x_resp_A1/*.nii`

    for f in $fisherzs; do
        basef=`basename $f`; subject=${basef:6:6};
        prefix="Nwarp_${f##*/}"

        3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -source $f \
        -prefix $prefix
    done
}

fishwarp_movie_B_x_resp_A1() {
    rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
    mkdir -p FisherZs_warped/movie_B_x_resp_A1; cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/warped_files/FisherZs_warped/movie_B_x_resp_A1;

    fisherzs=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/movie_B_x_resp_A1/*.nii`

    for f in $fisherzs; do
        basef=`basename $f`; subject=${basef:6:6};
        prefix="Nwarp_${f##*/}"

        3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -source $f \
        -prefix $prefix
    done
}

fishwarp_resp_A1_x_resp_A2() {
    rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
    mkdir -p FisherZs_warped/resp_A1_x_resp_A2; cd /data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/GroupResults/GroupISC/warped_files/FisherZs_warped/resp_A1_x_resp_A2;

    fisherzs=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/resp_A1_x_resp_A2/*.nii`

    for f in $fisherzs; do
        basef=`basename $f`; subject=${basef:6:6};
        prefix="Nwarp_${f##*/}"

        3dNwarpApply -overwrite -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -source $f \
        -prefix $prefix
    done
}

case "$1" in
    (orig_warped)
      subject=$2; 
      orig_warped $subject
      exit 0
      ;;
    (fishwarp_movie_A_x_movie_B)
      fishwarp_movie_A_x_movie_B
      exit 0
      ;;
    (fishwarp_movie_A_x_resp_A1)
      fishwarp_movie_A_x_resp_A1
      exit 0
      ;;
    (fishwarp_movie_B_x_resp_A1)
      fishwarp_movie_B_x_resp_A1
      exit 0
      ;;
    (fishwarp_resp_A1_x_resp_A2)
      fishwarp_resp_A1_x_resp_A2
      exit 0
      ;;
esac

# Run analyses in parallel in Swarm file -> Parallel_jobs.swarm
# bash warping_group_template.sh orig_warped sub-??
# bash warping_group_template.sh fishwarp_movie_A_x_movie_B
# bash warping_group_template.sh fishwarp_movie_A_x_resp_A1
# bash warping_group_template.sh fishwarp_movie_B_x_resp_A1
# bash warping_group_template.sh fishwarp_resp_A1_x_resp_A2




