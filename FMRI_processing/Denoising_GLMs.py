# Script to run GLMs with multiple options for the denoising parameters and to
# organize the outputs and distinct postprocessing steps in unique directories

# Sample line for running: 
#   python ~/code/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py sub-01 ./ ../afniproc_orig/WNW/sub-01.results/ test --include_motion --include_CSF


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
        "--inputfiles", type=str, required=False, default="tedana_r0?/ts_OC.nii.gz",
        help="The file names, with ? wildcards for the 3 runs of WNW data to input. Default=tedana_r0?/ts_OC.nii.gz"
    )
    parser.add_argument(
        "--scale_ts", action="store_true",
        help="Scale inputted data time series as done in afni_preproc"
    )
    parser.add_argument(
        "--include_motion", action="store_true",
        help="Add motion and motderiv regressors to the GLM"
    )
    parser.add_argument(
        "--include_CSF", action="store_true",
        help="Add CSF regressors to the GLM"
    ) 
    parser.add_argument(
        "--dontrunscript", action="store_true",
        help="This program will run the GLM script by default. use this option to just generate the script, but not run it"
    ) 

    args = parser.parse_args()

    # TODO: Consider initializing this all into a class like in the Denoising pilot
    subj = args.SUBJ
    input_dir = args.INPUTDIR
    out_dir = args.OUTDIR
    regressors = args.noise_regressors
    GLMlabel = args.LABEL
    inputfiles = args.inputfiles
    scale_ts = args.scale_ts
    include_motion = args.include_motion
    include_CSF = args.include_CSF

    dontrunscript = args.dontrunscript

    # Make sure key files & directories exist and create output directory
    if not os.path.exists(out_dir):
        raise OSError(f"OUTDIR {out_dir} not found")
    else:
        os.chdir(out_dir)
        if not os.path.exists(GLMlabel):
            os.mkdir(GLMlabel)

    # Check if orig_dir exists
    if not os.path.exists(input_dir):
        raise OSError(f"ORIGDIR {input_dir} not found")
    else:
        input_dir = os.path.abspath(input_dir)


    # Find fMRI files for GLM in input_dir
    file_targets = os.path.join(input_dir, inputfiles)
    input_files = sorted(glob.glob(file_targets))
    if not input_files:
        raise OSError(f"{file_targets} not found")
    elif len(input_files) != 3:
        raise OSError(f"{input_files} found. Should be 3 files")
    else:
        print(f"Running GLM using {input_files} input files")


    if regressors:
        if not os.path.isfile(regressors):
            raise OSError(f"NOISE_REGRESSORS {regressors} not found")
        else:
            regressors = os.path.abspath(regressors)

    os.chdir(GLMlabel)


    # TODO: We might want to test running with less censoring to see if certain methods
    #   can handle less censoring. In that case, we can add a function to create new
    #   censor files based on different censoring thresholds
    censorfile = os.path.abspath(os.path.join(input_dir, f"censor_{subj}_combined_2.1D"))


    FullStatement = [
        "#!/bin/tcsh -xef",
        ""
    ]
    # Save the scaled time series in the directory with the GLM output
    #  and point input_files to the new file names
    if scale_ts:
        maskfile = os.path.join(os.path.dirname(censorfile), f"full_mask.{subj}+orig")
        scale_statement, input_files = scale_time_series(subj, GLMlabel, input_files, maskfile)
        FullStatement.extend(scale_statement)


    



    # One function to generate the GLM, which includes all of the conditional logic based on inputs
    FullStatement.extend(generate_GLM_statement(subj, GLMlabel, input_files, censorfile, regressors=regressors, 
                    include_motion=include_motion, include_CSF=include_CSF))
    
    # Generate fixed commands for everything after the GLM
    FullStatement.extend(generate_post_GLM_statements(subj, GLMlabel, censorfile))

    # Put all commands into one script file and run it.
    create_and_run_glm(subj, GLMlabel, FullStatement, dontrunscript=dontrunscript)



def scale_time_series(subj, GLMlabel, input_files, maskfile):
    """
    Save the scaled time series in the directory with the GLM output
    and return the new file names
    """

    new_input_files = []
    scale_statement = []
    for idx, fname in enumerate(input_files):
        outfile = f"scaled_{subj}_{GLMlabel}"
        scale_statement.extend([
            f"3dTstat -prefix rm.mean_r{idx+1} {fname}",
            f"if [ -f rm.mean_r{idx+1}+tlrc.HEAD ]; then",
            f"   3drefit -view orig -space ORIG rm.mean_r{idx+1}+tlrc",
            f"fi",
            f"3dcalc -a {fname} -b rm.mean_r{idx+1}+orig \\",
            f"  -c {maskfile} \\",
            f"-expr 'c * min(200, a/b*100)*step(a)*step(b)' \\",
            f"-prefix {outfile}",
            ""
        ])
        new_input_files.append(f"{outfile}+orig")

    return scale_statement, new_input_files

def generate_GLM_statement(subj, GLMlabel, input_files, censorfile, regressors=None, include_motion=False, include_CSF=False):
    """
    Generate the GLM statement given the desired inputs and regressors
    
    """

    input_dir = os.path.dirname(censorfile)

    GLMstatement = ["3dDeconvolve -input \\"]    

    for i in input_files:
        GLMstatement.append(i + " \\")
    GLMstatement.append(
        f"   -censor {censorfile} \\"
    )

    if (include_CSF):
        GLMstatement.extend([
            f"  -ortvec {input_dir}/ROIPC.FSvent.r01.1D ROIPC.FSvent.r01  \\",
            f"  -ortvec {input_dir}/ROIPC.FSvent.r02.1D ROIPC.FSvent.r02  \\",
            f"  -ortvec {input_dir}/ROIPC.FSvent.r03.1D ROIPC.FSvent.r03  \\"
        ])
    if (include_motion):
        GLMstatement.extend([
            f"  -ortvec {input_dir}/mot_demean.r01.1D mot_demean_r01  \\",
            f"  -ortvec {input_dir}/mot_demean.r02.1D mot_demean_r02  \\",
            f"  -ortvec {input_dir}/mot_demean.r03.1D mot_demean_r03  \\",
            f"  -ortvec {input_dir}/mot_deriv.r01.1D mot_deriv_r01  \\",
            f"  -ortvec {input_dir}/mot_deriv.r02.1D mot_deriv_r02  \\",
            f"  -ortvec {input_dir}/mot_deriv.r03.1D mot_deriv_r03  \\"
        ])
    if(regressors):
        GLMstatement.extend(
            f"  -ortvec {regressors} \\"
        )

    GLMstatement.extend([
        "  -polort 4                                             \\",
        "  -num_stimts 5                                         \\",
        f"  -stim_times 1 {input_dir}/stimuli/{subj}_VisProc_Times.1D 'BLOCK(4,1)'    \\",
        "  -stim_label 1 VisWord                                         \\",
        f"  -stim_times 2 {input_dir}/stimuli/{subj}_FalVisProc_Times.1D 'BLOCK(4,1)' \\",
        "  -stim_label 2 FalVisWord                                      \\",
        f"  -stim_times 3 {input_dir}/stimuli/{subj}_AudProc_Times.1D 'BLOCK(4,1)'    \\",
        "  -stim_label 3 AudWord                                         \\",
        f"  -stim_times 4 {input_dir}/stimuli/{subj}_FalAudProc_Times.1D 'BLOCK(4,1)' \\",
        "  -stim_label 4 FalAudWord                                      \\",
        f"  -stim_times 5 {input_dir}/stimuli/{subj}_Keypress_Times.1D 'BLOCK(1,1)'   \\",
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
        f"  -fitts fitts.{subj}.{GLMlabel}                                            \\",
        f"  -errts errts.{subj}.{GLMlabel}                                          \\",
        f"  -bucket stats.{subj}.{GLMlabel} \\",
        f"  -cbucket cbucket.{subj}.{GLMlabel} \\",
        "  -x1D_stop", # this option means 3dDeconvolve doesn't run, but it does generate the files needed for 3dREMLfit
        " ",
        "# display degrees of freedom info from X-matrix",
        "1d_tool.py -show_df_info -infile X.xmat.1D |& tee out.df_info.txt",
        " ",
        "# -- execute the 3dREMLfit script, written by 3dDeconvolve --",
        "tcsh -x stats.REML_cmd",
        "",
        ""
    ])

    return(GLMstatement)



def generate_post_GLM_statements(subj, GLMlabel, censorfile):
    """
    Something similar to generate_GLM_statement but for everything that should happen afterwards
    including making the TSNR maps, calculating the blur/smoothness estimates,
    calculating the FDR statistical thresholds for clusters

    """

    input_dir = os.path.dirname(censorfile)

    maskfile = os.path.join(input_dir, f"full_mask.{subj}+orig")
    allrunsfile = os.path.join(input_dir, f"all_runs.{subj}+orig")

    post_GLMstatements = [
        "# note TRs that were not censored",
        f"set ktrs = `1d_tool.py -infile {censorfile}  \\",
        "                    -show_trs_uncensored encoded`",
        "",
        "# --------------------------------------------------",
        "# create a temporal signal to noise ratio dataset",
        "#    signal: if 'scale' block, mean should be 100",
        "#    noise : compute standard deviation of errts",
        f"3dTstat -mean -prefix rm.signal.all {allrunsfile}\"[$ktrs]\"",
        f"3dTstat -stdev -prefix rm.noise.all errts.{subj}.{GLMlabel}_REML+orig\"[$ktrs]\"",
        "3dcalc -a rm.signal.all+orig                                              \\",
        "    -b rm.noise.all+orig                                               \\",
        f"    -expr 'a/b' -prefix TSNR.{subj}.{GLMlabel}",
        ""
    ]

    post_GLMstatements.extend([
        "# ---------------------------------------------------",
        "# compute and store GCOR (global correlation average)",
        "# (sum of squares of global mean of unit errts)",
        f"3dTnorm -norm2 -prefix rm.errts.unit errts.{subj}.{GLMlabel}_REML+orig",
        f"3dmaskave -quiet -mask {maskfile} rm.errts.unit+orig            \\",
        "        > mean.errts.unit.1D",
        "3dTstat -sos -prefix - mean.errts.unit.1D\\\' > out.gcor.1D",
        "echo \"-- GCOR = `cat out.gcor.1D`\"",
        "",
        "# ---------------------------------------------------",
        "# compute correlation volume",
        "# (per voxel: correlation with masked brain average)",
        f"3dmaskave -quiet -mask {maskfile} errts.{subj}.{GLMlabel}_REML+orig       \\",
        "        > mean.errts.1D",
        f"3dTcorr1D -prefix corr_brain errts.{subj}.{GLMlabel}_REML+orig mean.errts.1D",
        ""
    ])

    post_GLMstatements.extend([
        "# ============================ blur estimation =============================",
        "# compute blur estimates",
        "",
        "# set list of runs",
        "set runs = (`count -digits 2 1 3`)",
        "",
        f"touch blur_est.{subj}.{GLMlabel}.1D   # start with empty file",
        "# create directory for ACF curve files",
        "mkdir files_ACF",
        "# -- estimate blur for each run in epits --",
        "touch blur.epits.1D",
        "# restrict to uncensored TRs, per run",
        "foreach run ( $runs )",
        "   set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \\",
        "                  -show_trs_run $run` ",
        "   if ( $trs == "" ) continue",
        f"   3dFWHMx -detrend -mask {maskfile} \\",
        "       -ACF files_ACF/out.3dFWHMx.ACF.epits.r$run.1D  \\",
        f"        {allrunsfile}\"[$trs]\" >> blur.epits.1D",
        "end",
        "",
        "# compute average FWHM blur (from every other row) and append",
        "set blurs = ( `3dTstat -mean -prefix - blur.epits.1D'{0..$(2)}'\\'` )",
        "echo average epits FWHM blurs: $blurs",
        f"echo \"$blurs   # epits FWHM blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        "",
        "# compute average ACF blur (from every other row) and append",
        "set blurs = ( `3dTstat -mean -prefix - blur.epits.1D'{1..$(2)}'\\'` )",
        "echo average epits ACF blurs: $blurs",
        f"echo \"$blurs   # epits ACF blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        "",
        # "# -- estimate blur for each run in errts --",
        # "touch blur.errts.1D",
        # "",
        # "# restrict to uncensored TRs, per run",
        # "foreach run ( $runs )",
        # "    set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \\",
        # "                        -show_trs_run $run`",
        # "    if ( $trs == \"\" ) continue",
        # f"    3dFWHMx -detrend -mask {maskfile}                           \\",
        # "            -ACF files_ACF/out.3dFWHMx.ACF.errts.r$run.1D                 \\",
        # f"            errts.{subj}.{GLMlabel}+orig\"[$trs]\" >> blur.errts.1D",
        # "end",
        # "",
        # "# compute average FWHM blur (from every other row) and append",
        # "set blurs = ( `3dTstat -mean -prefix - blur.errts.1D'{0..$(2)}'\\'` )",
        # "echo average errts FWHM blurs: $blurs",
        # f"echo \"$blurs   # errts FWHM blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        # "",
        # "# compute average ACF blur (from every other row) and append",
        # "set blurs = ( `3dTstat -mean -prefix - blur.errts.1D'{1..$(2)}'\\'` )",
        # "echo average errts ACF blurs: $blurs",
        # f"echo \"$blurs   # errts ACF blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        # "",
        "# -- estimate blur for each run in err_reml --",
        "touch blur.err_reml.1D",
        "",
        "# restrict to uncensored TRs, per run",
        "foreach run ( $runs )",
        "    set trs = `1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded  \\",
        "                        -show_trs_run $run`",
        "    if ( $trs == "" ) continue",
        f"    3dFWHMx -detrend -mask {maskfile}                           \\",
        "            -ACF files_ACF/out.3dFWHMx.ACF.err_reml.r$run.1D              \\",
        f"            errts.{subj}.{GLMlabel}_REML+orig\"[$trs]\" >> blur.err_reml.1D",
        "end",
        "",
        "# compute average FWHM blur (from every other row) and append",
        "set blurs = ( `3dTstat -mean -prefix - blur.err_reml.1D'{0..$(2)}'\\'` )",
        "echo average err_reml FWHM blurs: $blurs",
        f"echo \"$blurs   # err_reml FWHM blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        "",
        "# compute average ACF blur (from every other row) and append",
        "set blurs = ( `3dTstat -mean -prefix - blur.err_reml.1D'{1..$(2)}'\\'` )",
        "echo average err_reml ACF blurs: $blurs",
        "echo \"$blurs   # err_reml ACF blur estimates\" >> blur_est.{subj}.{GLMlabel}.1D",
        ""
    ])

    post_GLMstatements.extend([
        "# add 3dClustSim results as attributes to any stats dset",
        "mkdir files_ClustSim",
        "",
        "# run Monte Carlo simulations using method 'ACF'",
        f"set params = ( `grep ACF blur_est.{subj}.{GLMlabel}.1D | tail -n 1` )",
        f"3dClustSim -both -mask {maskfile} -acf $params[1-3]             \\",
        "        -cmd 3dClustSim.ACF.cmd -prefix files_ClustSim/ClustSim.ACF",
        "",
        "# run 3drefit to attach 3dClustSim results to stats",
        "set cmd = ( `cat 3dClustSim.ACF.cmd` )",
        f"$cmd stats.{subj}.{GLMlabel}+orig stats.{subj}.{GLMlabel}_REML+orig"
    ])

    return(post_GLMstatements)

def  create_and_run_glm(subj, GLMlabel, Fullstatement, dontrunscript=False):
    """
    Write GLMstatement and post_statements to one shell script in
    the output directory.
    Submit that file using sbatch in this function
    """


    # Fullstatement = GLMstatement + post_GLMstatements
    # print(*Fullstatement, sep="\n")

    OutFile = f"{subj}.{GLMlabel}_cmd.sh"
    with open(OutFile, "w") as ofile:
        ofile.write("\n".join(Fullstatement))
    print(os.getcwd())
    if not dontrunscript:
        run(["tcsh", "-xef", f"{subj}.{GLMlabel}_cmd.sh", "2>&1", "|", "tee" f"output.proc.{subj}.{GLMlabel}"])


if __name__ == '__main__':
    main()