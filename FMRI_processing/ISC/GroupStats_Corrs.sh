#!/bin/bash

# Group Statistics - excluded subject 04 (wrong TR)

rootdir=/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/
GroupDir=${rootdir}GroupResults/GroupMaps/
cd ${rootdir}GroupResults/GroupISC/

# 3dttest++ - Within Subjects
# 1 sample t-test to compare runs within each subject

# for condition in 'movie_A_x_movie_B' 'movie_A_x_resp_A1' 'movie_B_x_resp_A1' 'resp_A1_x_resp_A2'; do

Ttest_movie_A_x_movie_B() {

    if ! [ -d Group_Ttest/movie_A_x_movie_B/ ]; then
        mkdir Group_Ttest/movie_A_x_movie_B/ 
    fi
    out=Group_Ttest/movie_A_x_movie_B/

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all subjects (within) per dset & condition
        data=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/Tcorr_sub-??_movie_A_x_movie_B_${dset}.nii`

        # make Clust Sim directory (to contain lots of files!)
        clust_out=ClustSim_${dset}_movie_A_x_movie_B/
        if [ -d $clust_out ]; then
            mkdir $clust_out
        fi

        3dttest++ -dupe_ok -zskip -Clustsim     \
        -prefix_clustsim ${out}${clust_out}ClustSim_Group_${dset}_movie_A_x_movie_B -prefix ${out}Group_Ttest_Within_${dset}_movie_A_x_movie_B.nii \
        -setA $data

    done
}

Ttest_movie_A_x_resp_A1() {

    if ! [ -d Group_Ttest/movie_A_x_resp_A1/ ]; then
        mkdir Group_Ttest/movie_A_x_resp_A1/ 
    fi
    out=Group_Ttest/movie_A_x_resp_A1/

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all subjects (within) per dset & condition
        data=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/Tcorr_sub-??_movie_A_x_resp_A1_${dset}.nii`

        # make Clust Sim directory (to contain lots of files!)
        clust_out=ClustSim_${dset}_movie_A_x_resp_A1/
        if [ -d $clust_out ]; then
            mkdir $clust_out
        fi

        3dttest++ -dupe_ok -zskip -Clustsim     \
        -prefix_clustsim ${out}${clust_out}ClustSim_Group_${dset}_movie_A_x_resp_A1 -prefix ${out}Group_Ttest_Within_${dset}_movie_A_x_resp_A1.nii \
        -setA $data

    done
}

Ttest_movie_B_x_resp_A1() {

    if ! [ -d Group_Ttest/movie_B_x_resp_A1/ ]; then
        mkdir Group_Ttest/movie_B_x_resp_A1/ 
    fi
    out=Group_Ttest/movie_B_x_resp_A1/

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all subjects (within) per dset & condition
        data=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/Tcorr_sub-??_movie_B_x_resp_A1_${dset}.nii`

        # make Clust Sim directory (to contain lots of files!)
        clust_out=ClustSim_${dset}_movie_B_x_resp_A1/
        if [ -d $clust_out ]; then
            mkdir $clust_out
        fi

        3dttest++ -dupe_ok -zskip -Clustsim     \
        -prefix_clustsim ${out}${clust_out}ClustSim_Group_${dset}_movie_B_x_resp_A1 -prefix ${out}Group_Ttest_Within_${dset}_movie_B_x_resp_A1.nii \
        -setA $data

    done
}

Ttest_resp_A1_x_resp_A2() {

    if ! [ -d Group_Ttest/resp_A1_x_resp_A2/ ]; then
        mkdir Group_Ttest/resp_A1_x_resp_A2/ 
    fi
    out=Group_Ttest/resp_A1_x_resp_A2/

    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # make group maps for all subjects (within) per dset & condition
        data=`ls ${rootdir}GroupResults/GroupISC/IS_Correlations/Within_subjects/Tcorr_sub-??_resp_A1_x_resp_A2_${dset}.nii`

        # make Clust Sim directory (to contain lots of files!)
        clust_out=ClustSim_${dset}_resp_A1_x_resp_A2/
        if [ -d $clust_out ]; then
            mkdir $clust_out
        fi

        3dttest++ -dupe_ok -zskip -Clustsim     \
        -prefix_clustsim ${out}${clust_out}ClustSim_Group_${dset}_resp_A1_x_resp_A2 -prefix ${out}Group_Ttest_Within_${dset}_resp_A1_x_resp_A2.nii \
        -setA $data

    done
}


# 3dISC - Between Subjects

# simple ISC that generates an effect estimate (ISC value) & a t-statistic at each voxel
# might need to generate the variables (& their permutated forms)

# for condition in 'movie_A_x_movie_B' 'movie_B_x_movie_A' 'resp_A1_x_resp_A1' 'resp_A2_x_resp_A2'; do

ISC_movie_A_x_movie_B() {

    if ! [ -d Group_3dISC/movie_A_x_movie_B/ ]; then
    mkdir Group_3dISC/movie_A_x_movie_B/ 
    fi
    out=Group_3dISC/movie_A_x_movie_B/

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions

    # gather the files
    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -prefix Group_ISC_Stats_Between_${dset}_movie_A_x_movie_B.nii -jobs 12  \
        -mask ${GroupDir}GroupMask.nii.gz       \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_A_x_movie_B_${dset}.txt         "

        echo $command

        echo $command > groupISC_${dset}_movie_A_x_movie_B.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_${dset}_movie_A_x_movie_B.txt > stdout_groupISC_${dset}_movie_A_x_movie_B.txt

    done
}

ISC_movie_B_x_movie_A() {

    if ! [ -d Group_3dISC/movie_B_x_movie_A/ ]; then
    mkdir Group_3dISC/movie_B_x_movie_A/ 
    fi
    out=Group_3dISC/movie_B_x_movie_A/

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions

    # gather the files
    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -prefix Group_ISC_Stats_Between_${dset}_movie_B_x_movie_A.nii -jobs 12  \
        -mask ${GroupDir}GroupMask.nii.gz       \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @movie_B_x_movie_A_${dset}.txt         "

        echo $command

        echo $command > groupISC_${dset}_movie_B_x_movie_A.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_${dset}_movie_B_x_movie_A.txt > stdout_groupISC_${dset}_movie_B_x_movie_A.txt

    done
}

ISC_resp_A1_x_resp_A1() {

    if ! [ -d Group_3dISC/resp_A1_x_resp_A1/ ]; then
    mkdir Group_3dISC/resp_A1_x_resp_A1/ 
    fi
    out=Group_3dISC/resp_A1_x_resp_A1/

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions

    # gather the files
    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -prefix Group_ISC_Stats_Between_${dset}_resp_A1_x_resp_A1.nii -jobs 12  \
        -mask ${GroupDir}GroupMask.nii.gz       \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A1_x_resp_A1_${dset}.txt         "

        echo $command

        echo $command > groupISC_${dset}_resp_A1_x_resp_A1.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_${dset}_resp_A1_x_resp_A1.txt > stdout_groupISC_${dset}_resp_A1_x_resp_A1.txt

    done
}

ISC_resp_A2_x_resp_A2() {

    if ! [ -d Group_3dISC/resp_A2_x_resp_A2/ ]; then
    mkdir Group_3dISC/resp_A2_x_resp_A2/ 
    fi
    out=Group_3dISC/resp_A2_x_resp_A2/

    # In the ISC directory, there exists .txt files with the 2nd echo, OC, and ted_DN dataset tables for each of the conditions

    # gather the files
    for dset in '2nd_echo' 'OC' 'ted_DN'; do

        # generate the commands for ISC
        command="3dISC -prefix Group_ISC_Stats_Between_${dset}_resp_A2_x_resp_A2.nii -jobs 12  \
        -mask ${GroupDir}GroupMask.nii.gz       \
        -model  '1+(1|Subj1)+(1|Subj2)'         \
        -dataTable  @resp_A2_x_resp_A2_${dset}.txt         "

        echo $command

        echo $command > groupISC_${dset}_resp_A2_x_resp_A2.txt
        # execute the .txt file in tcsh and save output in another .txt file to read later
        nohup tcsh -x groupISC_${dset}_resp_A2_x_resp_A2.txt > stdout_groupISC_${dset}_resp_A2_x_resp_A2.txt

    done
}

# allows you to call the functions from command line (as the 1st argument)
case "$1" in
    (Ttest_movie_A_x_movie_B) 
      Ttest_movie_A_x_movie_B
      exit 0
      ;;
    (Ttest_movie_A_x_resp_A1) 
      Ttest_movie_A_x_resp_A1
      exit 0
      ;;
    (Ttest_movie_B_x_resp_A1) 
      Ttest_movie_B_x_resp_A1
      exit 0
      ;;
    (Ttest_resp_A1_x_resp_A2) 
      Ttest_resp_A1_x_resp_A2
      exit 0
      ;;
    (ISC_movie_A_x_movie_B) 
      ISC_movie_A_x_movie_B
      exit 0
      ;;
    (ISC_movie_B_x_movie_A) 
      ISC_movie_B_x_movie_A
      exit 0
      ;;
    (ISC_resp_A1_x_resp_A1) 
      ISC_resp_A1_x_resp_A1
      exit 0
      ;;
    (ISC_resp_A2_x_resp_A2) 
      ISC_resp_A2_x_resp_A2
      exit 0
      ;;
esac

# Run ALL analyses in swarm file (within & between)
# bash GroupStats_Corrs.sh Ttest_movie_A_x_movie_B
# bash GroupStats_Corrs.sh Ttest_movie_A_x_resp_A1
# bash GroupStats_Corrs.sh Ttest_movie_B_x_resp_A1
# bash GroupStats_Corrs.sh Ttest_resp_A1_x_resp_A2
# bash GroupStats_Corrs.sh ISC_movie_A_x_movie_B
# bash GroupStats_Corrs.sh ISC_movie_B_x_movie_A
# bash GroupStats_Corrs.sh ISC_resp_A1_x_resp_A1
# bash GroupStats_Corrs.sh ISC_resp_A2_x_resp_A2

