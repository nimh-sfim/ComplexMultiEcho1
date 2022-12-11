#!/bin/bash

# Template to warp all subject EPIs to the same grid template
# This group template will be used for the ISC correlations
# Ultimately, it will warp breathing/movie runs to same template for all subjects

subject=$1

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data
GroupDir=${rootdir}/GroupResults/GroupMaps
cd ${rootdir}/GroupResults/
if ! [ -d GroupISC/warped_files/ ]; then
    mkdir GroupISC/warped_files/
fi
cd GroupISC/warped_files/

orig_warped() {

    for task in 'breathing' 'movie'; do

        for run in 1 2 3; do

            if [ -d ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/ ]; then 
                # All files = middle echo (2nd echo), OC, and tedana denoised datasets for all movie/breathing runs
                second_echo=`ls ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/pb0?.${subject}.r01.e02.volreg+orig.HEAD`
                OC=`ls ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/pb0?.${subject}.r01.combine+orig.HEAD`
                ted_DN=`ls ${rootdir}/${subject}/afniproc_orig/${task}_run-${run}/${subject}.results/tedana_r01/dn_ts_OC.nii.gz`

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
                    3dNwarpApply -nwarp "${rootdir}/${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}/${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
                    -master ${GroupDir}/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
                    -source $source \
                    -prefix $prefix
                done
            fi
        done
    done
}

fisherz_warped() {
    rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
    GroupDir=${rootdir}GroupResults/
    within_subj_FisherZs=`ls ${GroupDir}GroupISC/IS_Correlations/Within_subjects/*.nii`
    cd ${rootdir}GroupResults/GroupISC/warped_files/

    for fisherz in $within_subj_FisherZs; do

        prefix="Nwarp_${fisherz##*/}"

        3dNwarpApply -nwarp "${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.qw_WARP.nii ${rootdir}${subject}/Proc_Anat/awpy/anat.un.aff.Xat.1D" \
        -master ${GroupDir}GroupMaps/alignment_EPIgrid_template_sub-01.nii.gz -dxyz 2 \
        -source $fisherz \
        -prefix $prefix
    done
}

case "$1" in
    (orig_warped) 
      orig_warped
      exit 0
      ;;
    (fisherz_warped)
      fisherz_warped
      exit 0
      ;;
esac

# Run analyses like so...
# bash warping_group_template.sh orig_warped
# bash warping_group_template.sh fisherz_warped




