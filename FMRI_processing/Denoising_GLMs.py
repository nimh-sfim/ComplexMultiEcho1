# Script to run GLMs with multiple options for the denoising parameters and to
# organize the outputs and distinct postprocessing steps in unique directories

# Sample line for running: 
#   python ~/code/nimh-sfim/ComplexMultiEcho1/FMRI_processing/Denoising_GLMs.py sub-01 ./ ../afniproc_orig/WNW/sub-01.results/ test --include_motion --include_CSF


from argparse import ArgumentParser
import os
from shutil import move, rmtree
from subprocess import run
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def main():
    # Argument Parsing
    parser = ArgumentParser(
        description="Run GLMs for the Word Nonword task with specific noise regressors"
    )

    parser.add_argument("SUBJ", help="Subject identifier (01, NOT sub-01)")
    parser.add_argument("OUTDIR", help="Output directory (full path or relative to where command was called from)")
    parser.add_argument("INPUTDIR", help="The directory where the optimally combined time series to use in the GLM are located. (full path or relative to OUTDIR)")
    
    parser.add_argument("LABEL", help="Descriptive label for this analysis, and subdirectory of OUTDIR where files will go")
    parser.add_argument("--noise_regressors", help="Name of csv or tsv file with the noise regressors to use. Include full path or relative path from OUTDIR",
        default=None)
    parser.add_argument("--regressors_metric_table", 
        help=("Name of tsv file with a metric table (similar to tedana) that includes a \'classification\' column "
            " and, for each row in the noise_regressors files, there's a corresponding row. If included, "
            "this option will create a new noise_regressors file in the output directory that only contains "
            "the time series of rejected components"),
        default=None)
    parser.add_argument(
        "--inputfiles", type=str, required=False, default="tedana_r0?/ts_OC.nii.gz",
        help="The file names, with ? wildcards for the 3 runs of WNW data to input. Relative to INPUTDIR. Default=tedana_r0?/ts_OC.nii.gz"
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
    regressors_metric_table = args.regressors_metric_table
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
        if os.path.exists(GLMlabel):
            print(f"{GLMlabel} subdirectory exists. Deleting directory and contents")
            rmtree(GLMlabel)
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
        regressor_targets = os.path.join(input_dir, regressors)
        regressor_files = sorted(glob.glob(regressor_targets))
        if not regressor_files:
            raise OSError(f"{regressor_targets} not found")
        elif len(input_files) != 3:
            raise OSError(f"{regressor_files} found. Should be 3 files")
        if regressors_metric_table:
            regressors_metric_targets = os.path.join(input_dir, regressors_metric_table)
            regressors_metric_table_files = sorted(glob.glob(regressors_metric_targets))
            if not regressors_metric_table_files:
                raise OSError(f"{regressors_metric_targets} not found")
            elif len(input_files) != 3:
                raise OSError(f"{regressors_metric_table_files} found. Should be 3 files")   
            print(f"Using inputted regressor files: {regressor_files}")
            print(f"Using inputted component metric table files: {regressors_metric_table_files}")
            combined_regressors = parse_metric_table(GLMlabel, regressor_files, metric_table_files=regressors_metric_table_files)
        else:
            print(f"Using inputted regressor files: {regressor_files}")
            combined_regressors = parse_metric_table(GLMlabel, regressor_files)
    else:
        combined_regressors = None

    os.chdir(GLMlabel)


    # TODO: We might want to test running with less censoring to see if certain methods
    #   can handle less censoring. In that case, we can add a function to create new
    #   censor files based on different censoring thresholds
    censorfile = os.path.abspath(os.path.join(input_dir, f"censor_{subj}_combined_2.1D"))


    FullStatement = [
        "#!/bin/tcsh -xef",
        "",
        f"cd {os.getcwd()}",
        f"echo Running {GLMlabel} in {os.getcwd()}",
        ""
    ]

    # Save the scaled time series in the directory with the GLM output
    #  and point input_files to the new file names
    if scale_ts:
        maskfile = os.path.join(os.path.dirname(censorfile), f"full_mask.{subj}+orig")
        scale_statement, input_files = scale_time_series(subj, GLMlabel, input_files, maskfile)
        FullStatement.extend(scale_statement)


    



    # One function to generate the GLM, which includes all of the conditional logic based on inputs
    FullStatement.extend(generate_GLM_statement(subj, GLMlabel, input_files, censorfile, regressors=combined_regressors, 
                    include_motion=include_motion, include_CSF=include_CSF))
    
    # Generate fixed commands for everything after the GLM
    FullStatement.extend(generate_post_GLM_statements(subj, GLMlabel, censorfile))

    # Put all commands into one script file and run it.
    create_and_run_glm(subj, GLMlabel, FullStatement, dontrunscript=dontrunscript)


def parse_metric_table(GLMlabel, regressor_files, metric_table_files=None):
    """
    INPUT:
    GLMlabel: The string that labels the subdirectory where the file should be written out
    regressor_files: List of 3 tsv files containing all a time series for each component for each run (i.e. the ICA mixing matrix)
    regressors_metric_table: List of 3 tsv files containing a row for each component in regressors
       Must include a column labeled 'classification'.

    OUTPUT:
    regressors: The absolute path to one regressor file containin the noise regressor time series for each run
    If regressors_metric_table=None, then this is just the combination of the 3 files in regressor_files
    If regressors_metrics_table lists 3 files then:
        Create a new noise regressors tsv file for components where 'classification'=='rejected' in the 
        regressors_metric_table. This file will be saved in the GLMs outputted subdirectory.
        regressors: An absolute path to the new noise_regressors file name.
           If no components are classified as rejected, then regressors=None
    """

    ica_mixing = []
    ica_metrics = []
    reject_idx = []
    n_vols = np.zeros(3, dtype=int)
    n_rej_comps = np.zeros(3, dtype=int)

    for idx in range(3):
        tmpsfx = regressor_files[idx].split('.')[-1]
        if tmpsfx == 'csv':
            sep=','
        elif tmpsfx == 'tsv':
            sep='\t'
        else:
            raise ValueError(f"Suffix of {regressor_files[idx]} is {tmpsfx}. Should be csv or tsv")
        ica_mixing.append(pd.read_csv(regressor_files[idx], sep=sep))
        print(f"Run {idx+1} Size of ICA mixing matrix: {(ica_mixing[idx]).shape}")
        n_vols[idx] = (ica_mixing[idx]).shape[0]

        if not isinstance(metric_table_files, type(None)):
            tmpsfx = metric_table_files[idx].split('.')[-1]
            if tmpsfx == 'csv':
                sep=','
            elif tmpsfx == 'tsv':
                sep='\t'
            else:
                raise ValueError(f"Suffix of {metric_table_files[idx]} is {tmpsfx}. Should be csv or tsv")
            ica_metrics.append(pd.read_csv(metric_table_files[idx], sep=sep))
            print(f"Run {idx+1} Size of ICA metrics table: {(ica_metrics[idx]).shape}")

            if (ica_mixing[idx]).shape[1] != (ica_metrics[idx]).shape[0]:
                raise ValueError(f"Different number of components in the mixing matrics ({(ica_mixing[idx]).shape[1]}) vs the metrics table ({(ica_metrics[idx]).shape[0]})")

            reject_idx.append(list(np.squeeze(np.argwhere(((ica_metrics[idx])['classification']=='rejected').values))))
            n_rej_comps[idx] = len(reject_idx[idx])
        else:
            print(f"ica_metrics is none {ica_metrics}")
            n_rej_comps[idx] = (ica_mixing[idx]).shape[1]

    Rejected_Timeseries = np.zeros((n_vols.sum(), n_rej_comps.sum()))


    column_labels = []
    print(f"Number of volumes per run {n_vols}")
    print(f"Number of rejected components per run {n_rej_comps}")
    # Run 1
    print(f"1: 0:{n_vols[0]}, 0:{n_rej_comps[0]}")
    if not isinstance(metric_table_files, type(None)):
        tmp_DF = (ica_mixing[0]).iloc[:,reject_idx[0]]
    else:
        tmp_DF = ica_mixing[0]
    tmp_cols = tmp_DF.columns
    column_labels.extend(["r01-" + s for s in tmp_cols])
    Rejected_Timeseries[0:n_vols[0], 0:n_rej_comps[0]] = tmp_DF.to_numpy(dtype=float)

    # Run 2
    print(f"2: {n_vols[0]}:{(n_vols[:2].sum())}, {n_rej_comps[0]}:{(n_rej_comps[:2].sum())}")
    if not isinstance(metric_table_files, type(None)):
        tmp_DF = (ica_mixing[1]).iloc[:,reject_idx[1]]
    else:
        tmp_DF = ica_mixing[1]
    tmp_cols = tmp_DF.columns
    column_labels.extend(["r02-" + s for s in tmp_cols])
    Rejected_Timeseries[n_vols[0]:(n_vols[:2].sum()), n_rej_comps[0]:(n_rej_comps[:2].sum())] = tmp_DF.to_numpy()
    # Run 3
    print(f"3: {(n_vols[:2].sum())}:{(n_vols.sum())}, {(n_rej_comps[:2].sum())}:{(n_rej_comps.sum())}")
    if not isinstance(metric_table_files, type(None)):
        tmp_DF = (ica_mixing[2]).iloc[:,reject_idx[2]]
    else:
        tmp_DF = ica_mixing[2]
    tmp_cols = tmp_DF.columns
    column_labels.extend(["r03-" + s for s in tmp_cols])
    Rejected_Timeseries[(n_vols[:2].sum()):(n_vols.sum()), (n_rej_comps[:2].sum()):(n_rej_comps.sum())] = tmp_DF.to_numpy()

    Rejected_Component_Timeseries = pd.DataFrame(data=Rejected_Timeseries, columns=column_labels)
    outfilename = os.path.join(GLMlabel, "Rejected_ICA_Components")
    Rejected_Component_Timeseries.to_csv(f"{outfilename}.tsv", header=True, index=False, sep='\t')
    regressors = os.path.abspath(f"{outfilename}.tsv")
    
    return regressors

def scale_time_series(subj, GLMlabel, input_files, maskfile):
    """
    Save the scaled time series in the directory with the GLM output
    and return the new file names
    """

    new_input_files = []
    scale_statement = []
    for idx, fname in enumerate(input_files):
        outfile = f"scaled_{subj}_{GLMlabel}_r{idx+1}"
        scale_statement.extend([
            f"3dTstat -overwrite -prefix rm.mean_r{idx+1} {fname}",
            f"if ( -f rm.mean_r{idx+1}+tlrc.HEAD ) then",
            f"   3drefit -view orig -space ORIG rm.mean_r{idx+1}+tlrc",
            f"endif",
            f"3dcalc -overwrite -a {fname} \\",
            f"  -b rm.mean_r{idx+1}+orig \\",
            f"  -c {maskfile} \\",
            f"  -expr 'c * min(200, a/b*100)*step(a)*step(b)' \\",
            f"  -prefix {outfile}",
            ""
            f"if ( -f {outfile}+tlrc.HEAD ) then",
            f"   3drefit -view orig -space ORIG {outfile}+tlrc",
            f"endif",          
        ])
        new_input_files.append(f"{outfile}+orig")

    return scale_statement, new_input_files

def generate_GLM_statement(subj, GLMlabel, input_files, censorfile, regressors=None, include_motion=False, include_CSF=False):
    """
    Generate the GLM statement given the desired inputs and regressors
    
    """

    input_dir = os.path.dirname(censorfile)

    GLMstatement = ["3dDeconvolve -overwrite -input \\"]    

    for i in input_files:
        GLMstatement.append(i + " \\")
    
    GLMstatement.append(
        f"   -censor {censorfile} \\"
    )

    if (include_CSF):
        print("Including default CSF regressors")
        GLMstatement.extend([
            f"  -ortvec {input_dir}/ROIPC.FSvent.r01.1D ROIPC.FSvent.r01  \\",
            f"  -ortvec {input_dir}/ROIPC.FSvent.r02.1D ROIPC.FSvent.r02  \\",
            f"  -ortvec {input_dir}/ROIPC.FSvent.r03.1D ROIPC.FSvent.r03  \\"
        ])
    
    # TODO: Currently no WM option, but might want to consider adding
    # if (include_WM):
    #     print("Including default White matter regressor")
    #     GLMstatement.append(
    #         f"  -ortvec {input_dir}/mean.ROI.FSWe.1D ROI.We[would need to make for the 3 runs separately].r01  \\",
    #     )

    if (include_motion):
        print("Including default motion regressors")
        GLMstatement.extend([
            f"  -ortvec {input_dir}/mot_demean.r01.1D mot_demean_r01  \\",
            f"  -ortvec {input_dir}/mot_demean.r02.1D mot_demean_r02  \\",
            f"  -ortvec {input_dir}/mot_demean.r03.1D mot_demean_r03  \\",
            f"  -ortvec {input_dir}/mot_deriv.r01.1D mot_deriv_r01  \\",
            f"  -ortvec {input_dir}/mot_deriv.r02.1D mot_deriv_r02  \\",
            f"  -ortvec {input_dir}/mot_deriv.r03.1D mot_deriv_r03  \\"
        ])
    if(regressors):
        print(f"Including custom regressors in {regressors}")
        GLMstatement.append(
            f"  -ortvec {regressors} combined_ort_vec \\"
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
        f"3dTstat -overwrite -mean -prefix signal.all {allrunsfile}\"[$ktrs]\"",
        f"3dTstat -overwrite -stdev -prefix noise.all errts.{subj}.{GLMlabel}_REML+orig\"[$ktrs]\"",
        "3dcalc -overwrite  -a signal.all+orig                                              \\",
        "    -b noise.all+orig                                               \\",
        f"    -expr 'a/b' -prefix TSNR.{subj}.{GLMlabel}",
        ""
    ]

    post_GLMstatements.extend([
        "# ---------------------------------------------------",
        "# compute and store GCOR (global correlation average)",
        "# (sum of squares of global mean of unit errts)",
        f"3dTnorm -overwrite -norm2 -prefix rm.errts.unit errts.{subj}.{GLMlabel}_REML+orig",
        f"3dmaskave -quiet -mask {maskfile} rm.errts.unit+orig            \\",
        "        > mean.errts.unit.1D",
        "3dTstat -overwrite -sos -prefix - mean.errts.unit.1D\\\' > out.gcor.1D",
        "echo \"-- GCOR = `cat out.gcor.1D`\"",
        "",
        "# ---------------------------------------------------",
        "# compute correlation volume",
        "# (per voxel: correlation with masked brain average)",
        f"3dmaskave -quiet -mask {maskfile} errts.{subj}.{GLMlabel}_REML+orig       \\",
        "        > mean.errts.1D",
        f"3dTcorr1D -overwrite -prefix corr_brain errts.{subj}.{GLMlabel}_REML+orig mean.errts.1D",
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
        f"3dClustSim -overwrite -both -mask {maskfile} -acf $params[1-3]             \\",
        "        -cmd 3dClustSim.ACF.cmd -prefix files_ClustSim/ClustSim.ACF",
        "",
        "# run 3drefit to attach 3dClustSim results to stats",
        "set cmd = ( `cat 3dClustSim.ACF.cmd` )",
        f"$cmd stats.{subj}.{GLMlabel}_REML+orig",
        "",
        "echo Removing intermediate files",
        "rm rm.*",
        "",
        "echo Compress the scaled time series",
        "gzip scaled*BRIK"
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