"""Get the timing data from the Psychopy scripts into BIDS & AFNI formats."""

import ast
import fnmatch
import glob
import logging
import os
import re
from argparse import ArgumentParser

import numpy as np
import pandas as pd

logger = logging.getLogger("GENERAL")


def main():
    # Argument Parsing
    parser = ArgumentParser(
        description=(
            "Gets the timing data from the Psychopy csv and log files "
            "for the WordNonword task and outputs AFNI-friendly "
            "stimulus timing files"
        )
    )
    parser.add_argument("--sbjnum", type=int, help="The subject number (i.e. 1)")
    parser.add_argument(
        "--run_nums",
        type=int,
        nargs="+",
        required=True,
        default=[],
        help="3 Run numbers for Word Nonword task in execution order",
    )
    parser.add_argument(
        "--rootdir",
        help="Directory path until the subjectID",
        required=False,
        default="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/",
    )

    parser.add_argument(
        "--psychopydir",
        help="Directory path until the psychopy directory (relevant to root or full path)",
        required=False,
        default=False,
    )

    parser.add_argument(
        "--outputdir",
        help="Directory path for output files",
        required=False,
        default=False,
    )
    args = parser.parse_args()

    sbjnum = f"{args.sbjnum:0>2}"
    sbjid = f"sub-{sbjnum}"
    if args.psychopydir:
        full_root_dir = args.psychopydir
        if not os.path.exists(full_root_dir):
            full_root_dir = os.path.join(args.rootdir, args.psychopydir)
    else:
        full_root_dir = os.path.join(args.rootdir, sbjid, "DataOffScanner/psychopy/")

    try:
        os.chdir(full_root_dir)
    except OSError:
        print(f"{full_root_dir} does not exist or is not accessible")
        raise

    if args.outputdir:
        if not os.path.exists(args.outputdir):
            logger.error(
                f"Output directory {args.outputdir} does not exist or is not accessible"
            )
            raise ValueError(
                f"Output directory {args.outputdir} does not exist or is not accessible"
            )
    else:
        args.outputdir = full_root_dir

    # setting up the logger
    log_handler = logging.FileHandler(
        f"{os.path.join(args.outputdir, f'{sbjid}_CreateEventTimesForGLM.log')}",
        mode="w",
    )
    log_formatter = logging.Formatter("%(levelname)-8s\t%(message)s")
    log_handler.setFormatter(log_formatter)
    logger.root.addHandler(log_handler)
    logger.root.setLevel(logging.INFO)

    logger.info(f"Running CreateEventTimesForGLM on {sbjid}")
    logger.info(f"psychopy logs in {full_root_dir}")

    run_nums = args.run_nums
    logger.info(f"Processing {len(run_nums)} runs in order: {run_nums}")

    get_all_trial_timing(sbjnum, run_nums, outputdir=args.outputdir)


def parse_trial_string(full_string):
    """
    Parse a specific string format from the PsychoPy log files and extract relevant information.

    Parameters
    ----------
    full_string : str
        The string to parse, expected to contain an OrderedDict(...) structure.
        Example:
        "OrderedDict([('Run', 3.0), ('TrialN', 2.0), ('ProcedureID', 3), ('Procedure', 'FalVisProc'), ('Font', 'Wingdings'), ('ITISec', 8.0), ('target1', 'twizy'), ('target2', '`uly'), ('target3', '^izk'), ('target4', '`ozk'), ('Expected_Response', 0), ('StartSec', 27.0), ('thisITI', 9.0)])"

    Returns
    -------
    dict
        A dictionary containing the extracted information:
        {
            'Run': float,
            'TrialN': float,
            'ProcedureID': int,
            'Procedure': str,
            'Font': str,
            'ITISec': float,
            'target1': str,
            'target2': str,
            'target3': str,
            'target4': str,
            'Expected_Response': int,
            'StartSec': float,
            'thisITI': float
        }
    """
    result = {}

    # Extract the OrderedDict(...) contents
    od_match = re.search(r"OrderedDict\((\[.*\])\)", full_string)
    if od_match:
        # Safely evaluate the list-of-tuples literal
        pairs = ast.literal_eval(od_match.group(1))
        for key, value in pairs:
            result[key] = value

    return result


def load_simplify_csv(filepath, data_summary_dict):
    """
    Load a CSV file and simplify its contents by removing unnecessary columns.

    Parameters
    ----------
    filepath : str
        The path to the CSV file to be loaded.
    data_summary_dict : dict
        A dictionary to store summary information extracted from the CSV file.
        Inputted dict will just contain the run acquisition order.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the simplified contents of the CSV file.
    """
    # Load the CSV file into a DataFrame
    full_run_df = pd.read_csv(filepath)

    data_summary_dict["participant_id"] = f"sub-{full_run_df['ID'].iloc[0]:0>2}"
    data_summary_dict["Run"] = full_run_df["Run"].iloc[2]
    data_summary_dict["Experiment Name"] = full_run_df["expName"].iloc[0]

    logger.info(
        f"Subject: {data_summary_dict['participant_id']}, Run: {data_summary_dict['Run']}, Experiment Name: {data_summary_dict['Experiment Name']}"
    )

    data_summary_dict["global trigger time csv"] = np.round(
        full_run_df["global trigger time"].iloc[1], decimals=5
    )
    data_summary_dict["global time trial 1 csv"] = np.round(
        full_run_df["global time"].iloc[2], decimals=5
    )
    data_summary_dict["global trigger trial 1 diff"] = np.round(
        (
            data_summary_dict["global time trial 1 csv"]
            - data_summary_dict["global trigger time csv"]
        ),
        decimals=5,
    )

    data_summary_dict["frame rate (mean)"] = np.round(
        full_run_df["frameRate"].mean(), decimals=5
    )
    data_summary_dict["frame rate (std)"] = np.round(
        full_run_df["frameRate"].std(), decimals=5
    )

    logger.info(
        f"frameRate mean, std: {data_summary_dict['frame rate (mean)']}, {data_summary_dict['frame rate (std)']}"
    )

    # Initializing all Correct responses to opposite
    # This is done so that, if no key is pressed during a trial,
    # trials with no expected response default to True and
    # trials with an expected response default to False
    full_run_df["Expected_Response"] = list(
        full_run_df["Expected_Response"].to_numpy(dtype=bool)
    )
    full_run_df["Correct Response"] = list(
        full_run_df["Expected_Response"].to_numpy() == False
    )

    full_run_df["keypress time"] = np.nan
    full_run_df["key pressed"] = ""

    # Simplify the DataFrame by dropping unnecessary columns & columns with PII
    # Also reordering columns to make it easier to read and understand
    columns_to_keep = [
        "Run",
        "TrialN",
        "ProcedureID",
        "Procedure",
        "StartSec",
        "stim1_time",
        "stim2_time",
        "stim3_time",
        "stim4_time",
        "Expected_Response",
        "Correct Response",
        "keypress time",
        "Font",
        "target1",
        "target2",
        "target3",
        "target4",
        "key pressed",
        "thisITI",
        "ITISec",
    ]

    simplified_df = full_run_df[columns_to_keep]

    simplified_df.rename(
        columns={
            "StartSec": "TrialStartSecExpected",
            "ITISec": "ITI before TR adjustment",
            "thisITI": "ITI divisible by TR",
            "target1": "stim1",
            "target2": "stim2",
            "target3": "stim3",
            "target4": "stim4",
        },
        inplace=True,
    )
    # Drop the first two rows which are not actual trials & just contain the global trigger time
    simplified_df.drop([0, 1], inplace=True)
    simplified_df.reset_index(drop=True, inplace=True)

    data_summary_dict["Real - expected trial time start (mean sec)"] = np.round(
        np.mean(simplified_df["stim1_time"] - simplified_df["TrialStartSecExpected"]),
        decimals=5,
    )
    data_summary_dict["Real - expected trial time start (std sec)"] = np.round(
        np.std(simplified_df["stim1_time"] - simplified_df["TrialStartSecExpected"]),
        decimals=5,
    )
    logger.info(
        f"Real - expected trial time start (sec) mean, std: {data_summary_dict['Real - expected trial time start (mean sec)']}, {data_summary_dict['Real - expected trial time start (std sec)']}"
    )
    data_summary_dict["4th - 1st stim time (mean sec)"] = np.round(
        np.mean(simplified_df["stim4_time"] - simplified_df["stim1_time"]), decimals=5
    )
    data_summary_dict["4th - 1st stim time (std sec)"] = np.round(
        np.std(simplified_df["stim4_time"] - simplified_df["stim1_time"]), decimals=5
    )
    logger.info(
        f"4th-1st stim time should be 3sec: mean, std {data_summary_dict['4th - 1st stim time (mean sec)']}, {data_summary_dict['4th - 1st stim time (std sec)']}"
    )

    # Adding columns that will be filled in later
    simplified_df["stim1_dur"] = np.nan
    simplified_df["stim2_dur"] = np.nan
    simplified_df["stim3_dur"] = np.nan
    simplified_df["stim4_dur"] = np.nan
    simplified_df["csv-log stim1_time"] = np.nan

    return simplified_df, data_summary_dict


def get_all_trial_timing(sbjnum, run_nums, outputdir=None):
    """
    Get all trial timing info from the csv files and calculate how many
    correct, incorrect, and missed keypresses occurred per run.
    Also logs trigger times so make sure check for inaccuracy or unexpected
    variation in the TR.

    PARAMETERS
    ----------
    sbjnum: str
        A zero-padded two digit string with the subject number identifier (i.e. '01')
    run_nums: list[int]
        A list of integers with the run numbers for the WordNonword task in execution order
        Run numbers are which stimulus sets 1-9 were used, not the order of acquisition
    outputdir: str
        Directory to save the output files

    OUTPUTS
    -------
    sub-{sbjnum}_task-wnw_run-?_events.tsv
        A BIDS-compliant events.tsv file for each run.
        Each row is either a trial or a keypress event that occured outside a trial.
        A separate BIDS-compliant events.json file details the information in each column.
    sub-{sbjnum}_task-wnw_run-summary.tsv
        A summary file containing information about each run.
        These will be combined across subjects to make a group summary file
        with a complementary BIDS json descriptor file.
    sub-{sbjnum}_VisProc_Times.1D
    sub-{sbjnum}_FalVisProc_Times.1D
    sub-{sbjnum}_AudProc_Times.1D
    sub-{sbjnum}_FalAudProc_Times.1D
    sub-{sbjnum}_Keypress_Times.1D
        The above 5 files contain the stimulus onsets in seconds relative to the first fMRI trigger for each condition.
        Each row is a different run in run acquisition order.
        These files are the inputs to AFNI's 3dDeconvolve for the GLM analysis.
    """
    # Any of the following 4 buttons is considered a response
    button_keys = ["Keypress: r", "Keypress: b", "Keypress: g", "Keypress: y"]

    # Remove 1D files to make sure existing files are not appended to
    # Create the file handles for each of the 5 1D files for stimulus onsetes
    # These will each be open & appended to for each run in run acquisition order
    file1Dnames = ["VisProc", "FalVisProc", "AudProc", "FalAudProc", "Keypress"]
    file_handles = [None] * len(file1Dnames)
    for fidx, file1Dname in enumerate(file1Dnames):
        tmp_full_file_path = os.path.join(
            outputdir, f"sub-{sbjnum}_{file1Dname}_Times.1D"
        )
        if os.path.exists(tmp_full_file_path):
            os.remove(tmp_full_file_path)
        file_handles[fidx] = open(tmp_full_file_path, mode="a")

    for runidx in range(len(run_nums)):
        logger.info(f"Processing run {runidx+1}. Run{run_nums[runidx]} stimulus set")
        run_start_time = None
        # timestamps the trigger 't' was inputted by the scanner
        triggertimes = np.full(1000, np.nan)
        # timestamps a button was pressed
        keypresstimes = np.full(1000, np.nan)
        # The button that was pressed.
        key_pressed = np.full(1000, fill_value="", dtype=str)

        run_num = run_nums[runidx]
        # Using the onsent time for visual and auditory stimuli it identify the trial when each button was pressed.
        # & if it was pressed at the right/wrong time or missed.
        # The auditory trials are only in the csv file so that needs
        # to be loaded in addition to the log file where keypresses are logged
        csvfilenames = glob.glob(
            f"{int(sbjnum)}_WordNonword_fastloc_RUN{run_num}_????_???_??_????.csv"
        )
        # For all conditions, the logger does not save the date section of the file names because that
        # could be considered PII. Time during a day is saved since that's not PII and could be useful for
        # confirmation the runs are in the correct order
        if len(csvfilenames) == 0:
            logger.error(
                f"No csv file matches {int(sbjnum)}_WordNonword_fastloc_RUN{run_num}_????_???_??_????.csv"
            )
            raise
        elif len(csvfilenames) > 1:
            tmpcsvfile = []
            for fidx in len(csvfilenames):
                tmpcsvfile.append(
                    csvfilenames[fidx][:-20] + "????_???_??" + csvfilenames[fidx][-9:]
                )
            logger.error(f"More than one file: {tmpcsvfile} with run_number {run_num}")
            raise
        else:
            data_summary_dict = {"Run Acq Order": runidx + 1}
            run_data, data_summary_dict = load_simplify_csv(
                csvfilenames[0], data_summary_dict
            )

            logfilenames = glob.glob(
                f"{int(sbjnum)}_WordNonword_fastloc_RUN{run_num}_????_???_??_????.log"
            )
            logdata = pd.read_csv(logfilenames[0], sep="\t")
            tmpcsvfile = csvfilenames[0][:-20] + "????_???_??" + csvfilenames[0][-9:]
            tmplogfile = logfilenames[0][:-20] + "????_???_??" + logfilenames[0][-9:]
            logger.info(f"Run {runidx+1} matched to {tmpcsvfile} and {tmplogfile}")
            # Rounding minutes to a decimal hour to reduce scan-time specificity for privacy concerns
            data_summary_dict["Acquisition hour"] = np.round(
                int(csvfilenames[0][-8:-6]) + int(csvfilenames[0][-6:-4]) / 60,
                decimals=1,
            )

        trigidx = 0
        keypressidx = 0
        active_vis_row_idx = 0
        in_stim = False

        # Since log file only has timings for visual stimuli, make a list of indices of those rows
        vis_row_idx = run_data.index[run_data["Procedure"] == "Null"].tolist()
        vis_row_idx += run_data.index[run_data["Procedure"] == "VisProc"].tolist()
        vis_row_idx += run_data.index[run_data["Procedure"] == "FalVisProc"].tolist()
        vis_row_idx.sort()

        # Not pressing a button during Null trials should be excluded from the correct trial count
        n_null_trials = len(run_data.index[run_data["Procedure"] == "Null"].tolist())
        if n_null_trials != 2:
            logger.warning(
                f"Run {runidx+1} has {n_null_trials} Null trials. Expected 2 Null trials."
            )

        # Looping through every row of logdata
        for lidx in range(len(logdata)):

            # Log the trigger times when each fMRI volume starts to be acquired
            if "Keypress: t" in logdata.iloc[lidx, 2]:
                triggertimes[trigidx] = logdata.iloc[lidx, 0]
                if trigidx == 0:
                    run_start_time = float(logdata.iloc[lidx, 0])
                    data_summary_dict["global start time log"] = np.round(
                        run_start_time, decimals=5
                    )
                    data_summary_dict["global start time csv-log"] = np.round(
                        data_summary_dict["global time trial 1 csv"]
                        - data_summary_dict["global start time log"],
                        decimals=5,
                    )
                trigidx += 1

            # Log time visual stimulus onset times and compare to the onset times listed in the csv file
            if len(fnmatch.filter([logdata.iloc[lidx, 2]], "stim?: autoDraw = True")):
                vis_stim_onset = float(logdata.iloc[lidx, 0])
                in_stim = True
                if logdata.iloc[lidx, 2][4] == "1":
                    run_data.loc[
                        vis_row_idx[active_vis_row_idx], "csv-log stim1_time"
                    ] = np.round(
                        run_data.loc[vis_row_idx[active_vis_row_idx], "stim1_time"]
                        - vis_stim_onset
                        + run_start_time,
                        decimals=5,
                    )

            # Use the visual stimulus offset time to calculate the duration of each visual stimulus
            # Note that these should be 0.6 seconds each, but the auditory stimuli were as long as 0.9sec
            if in_stim and len(
                fnmatch.filter([logdata.iloc[lidx, 2]], "stim?: autoDraw = False")
            ):
                run_data.loc[
                    vis_row_idx[active_vis_row_idx], f"{logdata.iloc[lidx, 2][0:5]}_dur"
                ] = np.round(float(logdata.iloc[lidx, 0]) - vis_stim_onset, decimals=5)
                in_stim = False
                if logdata.iloc[lidx, 2][4] == "4":
                    active_vis_row_idx += 1

            # # Log the times when any button is pressed by the participant
            if any(x in logdata.iloc[lidx, 2] for x in button_keys):
                key_pressed[keypressidx] = logdata.iloc[lidx, 2][-1]
                keypresstimes[keypressidx] = logdata.iloc[lidx, 0]
                keypressidx += 1

        # looping through rows of the log is finished. Calculate summary statistics
        tmp_vis_stim_dur = (
            run_data["stim1_dur"].to_list()
            + run_data["stim2_dur"].to_list()
            + run_data["stim3_dur"].to_list()
            + run_data["stim4_dur"].to_list()
        )
        data_summary_dict["vis stim duration (mean)"] = np.round(
            np.nanmean(tmp_vis_stim_dur), decimals=5
        )
        data_summary_dict["vis stim duration (std)"] = np.round(
            np.nanstd(tmp_vis_stim_dur), decimals=5
        )
        data_summary_dict["vis trial start time csv-log (mean)"] = np.round(
            np.nanmean(run_data["csv-log stim1_time"]), decimals=5
        )
        data_summary_dict["vis trial start time csv-log (std)"] = np.round(
            np.nanstd(run_data["csv-log stim1_time"]), decimals=5
        )
        if np.abs(data_summary_dict["vis trial start time csv-log (mean)"]) > 0.05:
            logger.warning(
                f"Difference between trial onsets in csv and log file is greater than 50ms"
            )

        triggertimes = triggertimes[0:trigidx] - run_start_time
        data_summary_dict["TR measured (mean)"] = np.round(
            np.mean(triggertimes[1:] - triggertimes[0:-1]), decimals=5
        )
        data_summary_dict["TR measured (std)"] = np.round(
            np.std(triggertimes[1:] - triggertimes[0:-1]), decimals=5
        )

        # Find the smallest difference between a MRI trigger time and each trial start
        # Save just the mean & std difference
        trial_start_times = run_data["stim1_time"].to_numpy()
        diff_between_trigger_times_and_trial_starts = np.full(
            len(trial_start_times), np.nan
        )
        for idx in range(len(trial_start_times)):
            tmp_diff = triggertimes - trial_start_times[idx]
            # Find the absolute minimum, but save the signed value of that minimum
            tmp_diff_idx = np.argmin(np.abs(tmp_diff))
            diff_between_trigger_times_and_trial_starts[idx] = tmp_diff[tmp_diff_idx]
        data_summary_dict["Closest TR - trial start (mean)"] = np.round(
            np.mean(diff_between_trigger_times_and_trial_starts), decimals=5
        )
        data_summary_dict["Closest TR - trial start (std)"] = np.round(
            np.std(diff_between_trigger_times_and_trial_starts), decimals=5
        )

        # Identify which keypresses occurred during a trial and if they were correct or incorrect
        keypresstimes = keypresstimes[0:keypressidx] - run_start_time
        key_pressed = key_pressed[0:keypressidx]
        if any(keypresstimes < 0):
            logger.warning(
                f"Some keypresses occurred before the first trigger. These will be ignored."
            )
            key_pressed = key_pressed[keypresstimes >= 0]
            keypresstimes = keypresstimes[keypresstimes >= 0]
            keypressidx = len(keypresstimes)

        # Assume a response is within a trial if it is from the beginning
        # of a trial until 3 sec after the 4th stimulus onset
        trial_response_length = 6

        for key_idx in range(len(keypresstimes)):
            # Find key press times > trial start times
            trial_idx = np.max(np.where(keypresstimes[key_idx] > trial_start_times))
            trial_start = trial_start_times[trial_idx]

            if keypresstimes[key_idx] < (trial_start + trial_response_length):
                # logging correct or incorrect key presses in trials
                run_data.loc[trial_idx, "Correct Response"] = bool(
                    run_data["Expected_Response"].loc[trial_idx]
                    and (keypresstimes[key_idx] > (trial_start + 3))
                )
                run_data.loc[trial_idx, "keypress time"] = np.round(
                    keypresstimes[key_idx], decimals=5
                )
                run_data.loc[trial_idx, "key pressed"] = key_pressed[key_idx]
            else:
                # logging key presses that occurred outside of trials
                missed_keypress_df = pd.DataFrame(
                    {
                        "Run": run_data["Run"].loc[trial_idx],
                        "keypress time": np.round(keypresstimes[key_idx], decimals=5),
                        "key pressed": key_pressed[key_idx],
                        "TrialN": -1,
                        "ProcedureID": -1,
                        "Procedure": "KeyPressOutsideTrial",
                        "Expected_Response": False,
                        "Correct Response": False,
                    },
                    index=[trial_start + 1],
                )
                # Add a row for the keypress that occurred outside of a trial, but keep the rest of the run_data intact
                run_data = pd.concat(
                    [
                        run_data.iloc[: (trial_idx + 1)],
                        missed_keypress_df,
                        run_data.iloc[(trial_idx + 1) :],
                    ]
                ).reset_index(drop=True)

                # Regenerate trial_start_times with a gap for the added row
                # This is necessary to avoid an index misalignment for the next keypress in the loop
                trial_start_times = run_data["stim1_time"].to_numpy()

        # Calculate summary statistics related to key presses
        data_summary_dict["Correct Keypress (count)"] = np.sum(
            np.logical_and(
                run_data["Expected_Response"].to_numpy(),
                run_data["Correct Response"].to_numpy(),
            )
        )
        data_summary_dict["Correct Keypress (percent)"] = np.round(
            100
            * data_summary_dict["Correct Keypress (count)"]
            / np.sum(run_data["Expected_Response"].to_numpy()),
            decimals=2,
        )
        data_summary_dict["Incorrect Keypress (count)"] = np.sum(
            np.logical_and(
                run_data["Expected_Response"].to_numpy() == False,
                run_data["keypress time"].to_numpy() > 0,
            )
        )

        trial_types = ["VisProc", "FalVisProc", "AudProc", "FalAudProc"]
        n_trials = 0
        for trial_type in trial_types:
            data_summary_dict[f"{trial_type} N Trials"] = np.sum(
                run_data["Procedure"].to_numpy() == trial_type
            )
            n_trials += data_summary_dict[f"{trial_type} N Trials"]
            data_summary_dict[f"{trial_type} N Expected Keypresses"] = np.sum(
                np.logical_and(
                    run_data["Procedure"].to_numpy() == trial_type,
                    run_data["Expected_Response"].to_numpy(),
                )
            )
            data_summary_dict[f"{trial_type} N Correct Keypresses"] = np.sum(
                np.logical_and(
                    run_data["Procedure"].to_numpy() == trial_type,
                    np.logical_and(
                        run_data["Expected_Response"].to_numpy(),
                        run_data["Correct Response"].to_numpy(),
                    ),
                )
            )
            data_summary_dict[f"{trial_type} N Incorrect Keypresses"] = np.sum(
                np.logical_and(
                    run_data["Procedure"].to_numpy() == trial_type,
                    np.logical_and(
                        run_data["Expected_Response"].to_numpy() == False,
                        run_data["keypress time"].to_numpy() > 0,
                    ),
                )
            )

        data_summary_dict["Correct Trials (count)"] = (
            np.sum(run_data["Correct Response"].to_numpy()) - n_null_trials
        )  # Exclude Null trials from the correct trial count
        data_summary_dict["Correct Trials (percent)"] = np.round(
            100 * data_summary_dict["Correct Trials (count)"] / n_trials, decimals=2
        )

        # print(run_data)
        # print(data_summary_dict)

        # Write the run_data to a BIDS-compliant events.tsv file for this run
        run_data.to_csv(
            os.path.join(
                outputdir,
                f"sub-{sbjnum}_task-wnw_run-{data_summary_dict['Run Acq Order']}_events.tsv",
            ),
            index=False,
            sep="\t",
        )

        # If this is the first run, create a new DataFrame to hold the summary data for all runs.
        # This also specifies the order of the columns in the DataFrame.
        # For subsequent runs, add a new row to the existing DataFrame with the summary data for that run.
        if runidx == 0:
            data_summary_df = pd.DataFrame(
                data_summary_dict,
                index=[0],
                columns=[
                    "participant_id",
                    "Run Acq Order",
                    "Acquisition hour",
                    "Run",
                    "Experiment Name",
                    "Correct Trials (count)",
                    "Correct Trials (percent)",
                    "Correct Keypress (count)",
                    "Correct Keypress (percent)",
                    "Incorrect Keypress (count)",
                    "VisProc N Trials",
                    "VisProc N Expected Keypresses",
                    "VisProc N Correct Keypresses",
                    "VisProc N Incorrect Keypresses",
                    "FalVisProc N Trials",
                    "FalVisProc N Expected Keypresses",
                    "FalVisProc N Correct Keypresses",
                    "FalVisProc N Incorrect Keypresses",
                    "AudProc N Trials",
                    "AudProc N Expected Keypresses",
                    "AudProc N Correct Keypresses",
                    "AudProc N Incorrect Keypresses",
                    "FalAudProc N Trials",
                    "FalAudProc N Expected Keypresses",
                    "FalAudProc N Correct Keypresses",
                    "FalAudProc N Incorrect Keypresses",
                    "TR measured (mean)",
                    "TR measured (std)",
                    "Closest TR - trial start (mean)",
                    "Closest TR - trial start (std)",
                    "Real - expected trial time start (mean sec)",
                    "Real - expected trial time start (std sec)",
                    "4th - 1st stim time (mean sec)",
                    "4th - 1st stim time (std sec)",
                    "vis stim duration (mean)",
                    "vis stim duration (std)",
                    "global trigger time csv",
                    "global time trial 1 csv",
                    "global trigger trial 1 diff",
                    "frame rate (mean)",
                    "frame rate (std)",
                    "global start time log",
                    "global start time csv-log",
                    "vis trial start time csv-log (mean)",
                    "vis trial start time csv-log (std)",
                ],
            )
        else:
            data_summary_df.loc[runidx] = data_summary_dict

        # Write the stimulus onset times for each condition to the corresponding 1D file for this run
        for fidx, file1Dname in enumerate(file1Dnames):
            if fidx == 4:
                save_vals = run_data["keypress time"].to_numpy()
                save_vals = save_vals[np.isfinite(save_vals)]
            else:
                save_vals = run_data.loc[
                    run_data["Procedure"] == file1Dname, "stim1_time"
                ]
            np.savetxt(file_handles[fidx], save_vals, fmt="%4.1f", newline=" ")
            np.savetxt(file_handles[fidx], ["\n"], fmt="%s", newline="")

    # After processing all runs, write the summary DataFrame to a BIDS-compliant summary.tsv file
    data_summary_df.to_csv(
        os.path.join(outputdir, f"sub-{sbjnum}_task-wnw_run-summary.tsv"),
        index=False,
        sep="\t",
    )

    # Close the file handles for the 1D files after all runs have been processed
    for fidx, file1Dname in enumerate(file1Dnames):
        np.savetxt(file_handles[fidx], [""], fmt="%s")
        file_handles[fidx].close()


if __name__ == "__main__":
    main()
