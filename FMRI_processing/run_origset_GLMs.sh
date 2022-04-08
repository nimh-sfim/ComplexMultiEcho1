### Going to turn this into a python script, but this is my starting point

#!/bin/tcsh -xef

# to execute via bash: 
#   tcsh -xef proc.sub-06 2>&1 | tee output.proc.sub-06

# After run_afniproc.sh is finished, we want to run other GLMs based on the output of AFNIproc.
# This script sets up and runs the early few GLMs we want to run on the WordNonword data


subj_id=$1

RunJobs=1

rootdir=/Volumes/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/${subj_id}/afniproc_orig/GLMs
mkdir $rootdir
cd $rootdir

# note TRs that were not censored
set ktrs = `1d_tool.py -infile censor_${subj}_combined_2.1D               \
                       -show_trs_uncensored encoded`


# ------------------------------
# run the regression analysis
3dDeconvolve -input pb06.$subj.r*.scale+orig.HEAD                         \
    -censor censor_${subj}_combined_2.1D                                  \
    -ortvec ROIPC.FSvent.r01.1D ROIPC.FSvent.r01                          \
    -ortvec ROIPC.FSvent.r02.1D ROIPC.FSvent.r02                          \
    -ortvec ROIPC.FSvent.r03.1D ROIPC.FSvent.r03                          \
    -ortvec mot_demean.r01.1D mot_demean_r01                              \
    -ortvec mot_demean.r02.1D mot_demean_r02                              \
    -ortvec mot_demean.r03.1D mot_demean_r03                              \
    -ortvec mot_deriv.r01.1D mot_deriv_r01                                \
    -ortvec mot_deriv.r02.1D mot_deriv_r02                                \
    -ortvec mot_deriv.r03.1D mot_deriv_r03                                \
    -polort 4                                                             \
    -num_stimts 5                                                         \
    -stim_times 1 stimuli/sub-06_VisProc_Times.1D 'BLOCK(4,1)'            \
    -stim_label 1 VisWord                                                 \
    -stim_times 2 stimuli/sub-06_FalVisProc_Times.1D 'BLOCK(4,1)'         \
    -stim_label 2 FalVisWord                                              \
    -stim_times 3 stimuli/sub-06_AudProc_Times.1D 'BLOCK(4,1)'            \
    -stim_label 3 AudWord                                                 \
    -stim_times 4 stimuli/sub-06_FalAudProc_Times.1D 'BLOCK(4,1)'         \
    -stim_label 4 FalAudWord                                              \
    -stim_times 5 stimuli/sub-06_Keypress_Times.1D 'BLOCK(1,1)'           \
    -stim_label 5 Keypress                                                \
    -jobs 8                                                               \
    -gltsym 'SYM: +VisWord -FalVisWord'                                   \
    -glt_label 1 Vis-FalVis                                               \
    -gltsym 'SYM: +AudWord -FalAudWord'                                   \
    -glt_label 2 Aud-FalAud                                               \
    -gltsym 'SYM: +AudWord +VisWord -FalAudWord -FalVisWord'              \
    -glt_label 3 Word-NonWord                                             \
    -gltsym 'SYM: -AudWord +VisWord -FalAudWord +FalVisWord'              \
    -glt_label 4 Vis-Aud                                                  \
    -fout -tout -x1D X.xmat.1D -xjpeg X.jpg                               \
    -x1D_uncensored X.nocensor.xmat.1D                                    \
    -fitts fitts.$subj                                                    \
    -errts errts.${subj}                                                  \
    -bucket stats.$subj


# display degrees of freedom info from X-matrix
1d_tool.py -show_df_info -infile X.xmat.1D |& tee out.df_info.txt

# -- execute the 3dREMLfit script, written by 3dDeconvolve --
tcsh -x stats.REML_cmd 


# if 3dREMLfit fails, terminate the script
if ( $status != 0 ) then
    echo '---------------------------------------'
    echo '** 3dREMLfit error, failing...'
    exit
endif

# This is the noise of the residual
3dTstat -stdev -prefix rm.noise.all errts.${subj}_REML+orig"[$ktrs]"


# possibly useful
1dcat X.nocensor.xmat.1D'[15]' > ideal_VisWord.1D



# NEED TO CORRECT ACF FITS, but might be able to reduce a bit
# ============================ blur estimation =============================
# compute blur estimates
touch blur_est.$subj.1D   # start with empty file

# create directory for ACF curve files
mkdir files_ACF

# -- estimate blur for each run in epits --
touch blur.epits.1D

# restrict to uncensored TRs, per run
foreach run ( $runs )
    set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \
                          -show_trs_run $run`
    if ( $trs == "" ) continue
    3dFWHMx -detrend -mask full_mask.$subj+orig                           \
            -ACF files_ACF/out.3dFWHMx.ACF.epits.r$run.1D                 \
            all_runs.$subj+orig"[$trs]" >> blur.epits.1D
end

# compute average FWHM blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.epits.1D'{0..$(2)}'\'` )
echo average epits FWHM blurs: $blurs
echo "$blurs   # epits FWHM blur estimates" >> blur_est.$subj.1D

# compute average ACF blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.epits.1D'{1..$(2)}'\'` )
echo average epits ACF blurs: $blurs
echo "$blurs   # epits ACF blur estimates" >> blur_est.$subj.1D

# -- estimate blur for each run in errts --
touch blur.errts.1D

# restrict to uncensored TRs, per run
foreach run ( $runs )
    set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \
                          -show_trs_run $run`
    if ( $trs == "" ) continue
    3dFWHMx -detrend -mask full_mask.$subj+orig                           \
            -ACF files_ACF/out.3dFWHMx.ACF.errts.r$run.1D                 \
            errts.${subj}+orig"[$trs]" >> blur.errts.1D
end

# compute average FWHM blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.errts.1D'{0..$(2)}'\'` )
echo average errts FWHM blurs: $blurs
echo "$blurs   # errts FWHM blur estimates" >> blur_est.$subj.1D

# compute average ACF blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.errts.1D'{1..$(2)}'\'` )
echo average errts ACF blurs: $blurs
echo "$blurs   # errts ACF blur estimates" >> blur_est.$subj.1D

# -- estimate blur for each run in err_reml --
touch blur.err_reml.1D

# restrict to uncensored TRs, per run
foreach run ( $runs )
    set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \
                          -show_trs_run $run`
    if ( $trs == "" ) continue
    3dFWHMx -detrend -mask full_mask.$subj+orig                           \
            -ACF files_ACF/out.3dFWHMx.ACF.err_reml.r$run.1D              \
            errts.${subj}_REML+orig"[$trs]" >> blur.err_reml.1D
end

# compute average FWHM blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.err_reml.1D'{0..$(2)}'\'` )
echo average err_reml FWHM blurs: $blurs
echo "$blurs   # err_reml FWHM blur estimates" >> blur_est.$subj.1D

# compute average ACF blur (from every other row) and append
set blurs = ( `3dTstat -mean -prefix - blur.err_reml.1D'{1..$(2)}'\'` )
echo average err_reml ACF blurs: $blurs
echo "$blurs   # err_reml ACF blur estimates" >> blur_est.$subj.1D


# add 3dClustSim results as attributes to any stats dset
mkdir files_ClustSim

# run Monte Carlo simulations using method 'ACF'
set params = ( `grep ACF blur_est.$subj.1D | tail -n 1` )
3dClustSim -both -mask full_mask.$subj+orig -acf $params[1-3]             \
           -cmd 3dClustSim.ACF.cmd -prefix files_ClustSim/ClustSim.ACF

# run 3drefit to attach 3dClustSim results to stats
set cmd = ( `cat 3dClustSim.ACF.cmd` )
$cmd stats.$subj+orig stats.${subj}_REML+orig