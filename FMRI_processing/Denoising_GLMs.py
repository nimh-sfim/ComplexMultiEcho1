# WORK IN PROGRESS

# Script to run GLMs with multiple options for the denoising parameters and to
# organize the outputs and distinct postprocessing steps in unique directories

from argparse import ArgumentParser
import os
from shutil import move
from subprocess import run
import glob



def main():
    # Argument Parsing
    parser = ArgumentParser(
        description="Run GLMs for the Word Nonword task with specific noise regressors"
    )

    parser.add_argument("SUBJ", help="Subject identifier (01, NOT sub-01)")
    parser.add_argument("OUTDIR", help="Output directory (full path or relative to where command was called from)")
    parser.add_argument("INPUTDIR", help="The directory where the optimally combined time series to use in the GLM are located. (full path or relative to OUTDIR)")
    
    parser.add_argument("LABEL", help="Descriptive label for this analysis, and subdirectory of OUTDIR where files will go")
    parser.add_argument("--noise_regressors", help="Name of tsv file with the noise regressors to use. Include full path or relative path from OUTDIR",
        default=None)
    parser.add_argument(
        "--inputsfx", type=str, required=False, default="scale",
        help="The suffix of the file type to use. Default=scale (i.e. pb06.sub-??.r0?.scale+orig)"
    )
    parser.add_argument(
        "--include_motion", action="store_true",
        help="Add motion and motderiv regressors to the GLM"
    )
    parser.add_argument(
        "--inclue_CSF", action="store_true",
        help="Add CSF regressors to the GLM"
    ) 
    

    args = parser.parse_args()

    # TODO: Initialize this all into a class like in the Denoising pilot
    subj = args.subjid
    input_dir = args.INPUTDIR
    out_dir = args.OUTDIR
    regressors = args.noise_regressors
    GLMlabel = args.LABEL
    input_sfx = args.inputsfx
    include_motion = args.include_motion
    include_CSF = args.include_CSF

    if not os.path.exists(out_dir):
        raise OSError(f"OUTDIR {out_dir} not found")
    else:
        os.chdir(out_dir)
        if not os.path.exists(GLMlabel):
            os.mkdir(GLMlabel)

    # Check if orig_dir exists
    if not os.path.exists(input_dir):
        raise OSError(f"ORIGDIR {input_dir} not found")


    # TODO: These paths need to be adjusted so that when 3dDeconvolve is run the point to the right locations
    #       from insize the out_dir/label subdirectory
    # Create file names by finding them in orig_dir
    file_targets = os.join(input_dir, f"pb0?.{subj}.r0?.{input_sfx}+orig.HEAD")
    input_files = glob.glob(file_targets)
    if not input_files:
        raise OSError(f"{file_targets} not found")
    elif len(input_files) != 3:
        raise OSError(f"{input_files} found. Should be 3 files")
    else:
        print(f"Running GLM using {input_files} input files")


    if regressors:
        if not os.path.isfile(regressors):
            raise OSError(f"NOISE_REGRESSORS {regressors} not found")

    os.chdir(GLMlabel)

    GLMstatement = generate_GLM_statement(subj, GLMlabel, input_files, regressors)

    # Censored time point indices in ktrs
    # ktrs is a weird name, but probably easier to keep the same name
    # as used in AFNI
    # TODO: We might want to test running with less censoring to see if certain methods
    #   can handle less censoring. In that case, we can add a function to edit the censor file
    censorfile = os.join.path(input_dir, f"censor_{subj}_combined_2.1D")
    ktrs = run(f"1d_tool.py -infile  {censorfile} -show_trs_uncensored encoded", 
                capture_output=True)

    post_statements = generate_post_GLM_statements(subj, GLMlabel)



    create_and_run_glm(GLMstatement, post_statements)



def generate_GLM_statement(subj, GLMlabel, input_files, censorfile, regressors, include_motion, include_CSF):
    """
    Generate the GLM statement given the desired inputs and regressors
    
    """


    GLMstatement = (
        f"3dDeconvolve -input {input_files} \\",
        f"   -censor {censorfile} \\"
    )
    if (include_CSF):
        GLMstatement.append(
            "  -ortvec ROIPC.FSvent.r01.1D ROIPC.FSvent.r01  \\",
            "  -ortvec ROIPC.FSvent.r02.1D ROIPC.FSvent.r02  \\",
            "  -ortvec ROIPC.FSvent.r03.1D ROIPC.FSvent.r03  \\"
        )
    if (include_motion):
        GLMstatement.append(
            "  -ortvec mot_demean.r01.1D mot_demean_r01  \\",
            "  -ortvec mot_demean.r01.1D mot_demean_r02  \\",
            "  -ortvec mot_demean.r01.1D mot_demean_r03  \\"
            "  -ortvec mot_demean.r01.1D mot_deriv_r01  \\",
            "  -ortvec mot_demean.r01.1D mot_deriv_r02  \\",
            "  -ortvec mot_demean.r01.1D mot_deriv_r03  \\"
        )
    if(regressors):
        GLMstatement.append(
            f"  -ortvec {regressors} \\"

    GLMstatement.append(
        "  -polort 4                                             \\",
        "  -num_stimts 5                                         \\",
        f"  -stim_times 1 stimuli/ {subj}_VisProc_Times.1D 'BLOCK(4,1)'    \\",
        "  -stim_label 1 VisWord                                         \\",
        f"  -stim_times 2 stimuli/ {subj}_FalVisProc_Times.1D 'BLOCK(4,1)' \\",
        "  -stim_label 2 FalVisWord                                      \\",
        f"  -stim_times 3 stimuli/ {subj}_AudProc_Times.1D 'BLOCK(4,1)'    \\",
        "  -stim_label 3 AudWord                                         \\",
        f"  -stim_times 4 stimuli/ {subj}_FalAudProc_Times.1D 'BLOCK(4,1)' \\",
        "  -stim_label 4 FalAudWord                                      \\",
        f"  -stim_times 5 stimuli/ {subj}_Keypress_Times.1D 'BLOCK(1,1)'   \\",
        "  -stim_label 5 Keypress                                        \\",
        "  -jobs 8                                                       \\",
        "  -gltsym 'SYM: +VisWord -FalVisWord'                           \\",
        "  -glt_label 1 Vis-FalVis                                       \\",
        "  -gltsym 'SYM: +AudWord -FalAudWord'                           \\",
        "  -glt_label 2 Aud-FalAud                                       \\",
        "  -gltsym 'SYM: +AudWord +VisWord -FalAudWord -FalVisWord'      \\",
        "  -glt_label 3 Word-NonWord                                     \\",
        "  -gltsym 'SYM: -AudWord +VisWord -FalAudWord +FalVisWord'      \\",
        "  -glt_label 4 Vis-Aud                                          \\",
        "  -fout -tout -rout -x1D X.xmat.1D -xjpeg X.jpg                       \\",
        "  -x1D_uncensored X.nocensor.xmat.1D                            \\",
        f"  -fitts fitts.{subj}                                            \\",
        f"  -errts errts.{subj}                                          \\",
        f"  -bucket stats.{subj} \\",
        f"  -cbucket cbucket.{subj} \\",
        "  -x1D_stop", # this option means 3dDeconvolve doesn't run, but it does generate the files needed for 3dREMLfit
        " ",
        "# display degrees of freedom info from X-matrix",
        "1d_tool.py -show_df_info -infile X.xmat.1D |& tee out.df_info.txt",
        " ",
        "# -- execute the 3dREMLfit script, written by 3dDeconvolve --",
        "tcsh -x stats.REML_cmd"
    )

    return(GLMstatement)



    def post_statements = generate_post_GLM_statements(subj, GLMlabel):
    """
    Something similar to generate_GLM_statement but for everything that should happen afterwards

    """

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


    def  create_and_run_glm(GLMstatement, post_statements):
        """
        Write GLMstatement and post_statementes to one shell script in
        the output directory.
        Submit that file using sbatch in this function
        """