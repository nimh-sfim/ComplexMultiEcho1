
# Program to get the timing data from the Psychopy scripts into AFNI-friendly format


import pandas as pd
import numpy as np
import os
import glob
import logging
from argparse import ArgumentParser

logger = logging.getLogger("GENERAL")

def main():
    # Argument Parsing
    parser = ArgumentParser(
        description=("Gets the timing data from the Psychopy csv and log files "
                     "for the WordNonword task and outputs AFNI-friendly "
                     "stimulus timing files")
    )
    parser.add_argument("--sbjnum", type=int, help="The subject number (i.e. 1)")
    parser.add_argument(
        "--runnums", type=int, nargs="+", required=True, default=[],
        help="3 Run numbers for Word Nonword task in execution order"
    )
    parser.add_argument("--rootdir", help="Directory path until the subjectID",
                        required=False,
                        default="/data/NIMH_SFIM/handwerkerd/ComplexMultiEcho1/Data/")
    
    parser.add_argument(
        "--", action="store_true", dest="placeholder",
        help= (
            "Placeholder to allow you to indicate that the series of "
            "integers for --ignore has terminated. Does nothing else."
        )
    )
    args = parser.parse_args()

    sbjnum = f"{args.sbjnum:0>2}"
    sbjid = f"sub-{sbjnum}"
    FullRootDir = os.path.join(args.rootdir, sbjid, "DataOffScanner/psychopy/")

    try:
        os.chdir(FullRootDir)
    except OSError:
        print(f"{FullRootDir} does not exist or is not accessible")
        raise

    # setting up the logger
    log_handler = logging.FileHandler(f"{sbjid}_CreateEventTimesForGLM.log", mode='w')
    log_formatter = logging.Formatter("%(levelname)-8s\t%(message)s")
    log_handler.setFormatter(log_formatter)
    logger.root.addHandler(log_handler)
    logger.root.setLevel(logging.INFO)
 
    logger.info(f"Running CreateEventTimesForGLM on {sbjid}")
    logger.info(f"psychopy logs in {FullRootDir}")

    RunNums = args.runnums
    logger.info(f"Processing {len(RunNums)} runs in order: {RunNums}")

    # Save the trial timing files
    get_trial_timing(sbjnum, RunNums)
    
    # Save the keypress timing file
    get_keypress_timing(sbjnum, RunNums)


def get_trial_timing(sbjnum, RunNums, NumTrials=12):
    """
    Get the trial timing info from the csv files and do some checks to confirm
    they look reasonable

    PARAMETERS
    ----------
    sbjnum: str
        A zero-padded two digit string with the subject number identifier (i.e. '01')
    RunNums: list[int]
        A list of the nonword runs IDs in order of execution
    NumTrials: int
        The number of trials per condition in each run. (default=12)

    RETURNS
    -------
    A file name is saved for each trial time containing the trial times
    to use with AFNI. 
    sub-{sbjnum}_['VisProc', 'FalVisProc', 'AudProc', 'FalAudProc']_Times.1D"
    """

    logger.info("Getting Trial Times")
    # There are for diffferent trial types (called ProcTypes in the logs)
    ProcTypes = np.array(['VisProc', 'FalVisProc', 'AudProc', 'FalAudProc'])

    allrundata = list()
    for runidx in range(len(RunNums)):
        RunNum = RunNums[runidx]
        logger.info(f"Loading Word Nonword Run {RunNum} which is acquired run #{runidx+1}")
        csvfilenames = glob.glob(f"{int(sbjnum)}_WordNonword_fastloc_RUN{RunNum}_????_???_??_????.csv")
        # For all conditions, the logger does not save the date section of the file names because that
        # could be considered PII. Time during a day is saved since that's not PII and could be useful for
        # confirmation the runs are in the correct order
        if len(csvfilenames)==0:
            logger.error(f"No csv file matches {int(sbjnum)}_WordNonword_fastloc_RUN{RunNum}_????_???_??_????.csv")
            raise
        elif len(csvfilenames)>1:
            tmpcsvfile = []
            for fidx in len(csvfilenames):
                tmpcsvfile.append(csvfilenames[fidx][:-20] + '????_???_??' + csvfilenames[fidx][-9:])
            logger.error(f"More than one file: {tmpcsvfile} with RunNumber {RunNum}")
            raise
        else:
            tmpcsvfile = csvfilenames[0][:-20] + '????_???_??' + csvfilenames[0][-9:]
            logger.info(f"Run {runidx+1} matched to {tmpcsvfile}")
            allrundata.append(pd.read_csv(csvfilenames[0]))

    for ProcType in ProcTypes: # Diff saved file for each trial type
        TrialTimes = np.empty((NumTrials, len(RunNums)))
        for runidx in range(len(RunNums)):
            RunNum = RunNums[runidx]
            logger.info(f"Processing Run {RunNum} for {ProcType}")

            # For each trial type load the measured time the first stimulus appeared in a trial (stim1_time)
            #   and when that stimulus was supposed to appear (StartSec)
            rundata = allrundata[runidx]
            TrialTimes[:,runidx] = np.around(rundata.loc[rundata['Procedure']==ProcType,'stim1_time'].values,decimals=1)
            ExpectedStart = np.around(rundata.loc[rundata['Procedure']==ProcType,'StartSec'].values,decimals=1)

            logger.info(f"Actual Times:   {TrialTimes[:,runidx]}")
            logger.info(f"Expected Times: {ExpectedStart}")

            # Log similaries/differences between expected and actual trial times
            tmp_absdiff = np.abs(TrialTimes[:,runidx]-ExpectedStart)
            if "all_abs_timing_diff" not in locals():
                all_abs_timing_diff = tmp_absdiff
            else:
                all_abs_timing_diff = np.concatenate((all_abs_timing_diff, tmp_absdiff), axis=0)
            logger.info("Absolute difference between actual & expected trial times: Mean: "
                        f"{np.mean(tmp_absdiff)}, Max: {np.max(tmp_absdiff)}")

        # Save a separate .1D file for each trial type
        np.savetxt(f"sub-{sbjnum}_{ProcType}_Times.1D", TrialTimes.T, fmt='%4.1f')
    
    print(f"Total number of trials {len(all_abs_timing_diff)}")
    total_trial_accuracy = ("Absolute difference between actual & expected trial times: Mean: "
                            f"{np.mean(tmp_absdiff)}, Max: {np.max(tmp_absdiff)}")
    print(total_trial_accuracy)
    logger.info(total_trial_accuracy)


def get_keypress_timing(sbjnum, RunNums, ShowExpected=True):
    """
    Get the keypress timing info from the csv files and calculate how many
    correct, incorrect, and missed keypresses occurred per run.
    Also logs trigger times to make sure check for inaccuracy or unexpected
    variation in the TR.

    PARAMETERS
    ----------
    sbjnum: str
        A zero-padded two digit string with the subject number identifier (i.e. '01')
    RunNums: list[int]
    ShowExpected: bool
        Adds extra logging to compare measured to expected values

    RETURNS
    -------
    sub-{sbjnum}_Keypress_Times.1D and contains the keypress timings to use with AFNI
    Note: For this file, all keypresses are included because it is modeling motor
    movement. It does not distinguish correct, incorrect, and missed pressed.
    """

    logger.info("Getting Keypress Times")
    # Any of the following 4 buttons is considered a response
    ButtonKeys = ['Keypress: r', 'Keypress: b', 'Keypress: g', 'Keypress: y']
    KeypressTimesAllRuns = []
    AllCorrectCount = 0
    AllMissedCount = 0
    AllIncorrectCount = 0
    AllExpectedCount = 0
    for runidx in range(len(RunNums)):
        triggertimes = np.empty(1000) # timestamps the trigger 't' was pressed
        keypresstimes = np.empty(1000) # timestamps a button was pressed
        ExpectedResponseTimes = np.empty(1000) # When the 4th stimulus appeared in a trial (after which a response might be expected)
        RunNum = RunNums[runidx]
        # Using the appearance time for the 4th stimulus in each trial to see if a button was pressed
        # at the right/wrong time or missed. This information is only in the csv file so that needs
        # to be loaded in addition to the log file where keypresses are logged
        csvfilenames = glob.glob(f"{int(sbjnum)}_WordNonword_fastloc_RUN{RunNum}_????_???_??_????.csv")
        # For all conditions, the logger does not save the date section of the file names because that
        # could be considered PII. Time during a day is saved since that's not PII and could be useful for
        # confirmation the runs are in the correct order
        if len(csvfilenames)==0:
            logger.error(f"No csv file matches {int(sbjnum)}_WordNonword_fastloc_RUN{RunNum}_????_???_??_????.csv")
            raise
        elif len(csvfilenames)>1:
            tmpcsvfile = []
            for fidx in len(csvfilenames):
                tmpcsvfile.append(csvfilenames[fidx][:-20] + '????_???_??' + csvfilenames[fidx][-9:])
            logger.error(f"More than one file: {tmpcsvfile} with RunNumber {RunNum}")            
            raise
        else:
            rundata = pd.read_csv(csvfilenames[0])
            logfilenames = glob.glob(f"{int(sbjnum)}_WordNonword_fastloc_RUN{RunNum}_????_???_??_????.log")
            logdata = pd.read_csv(logfilenames[0], sep='\t')
            tmpcsvfile = csvfilenames[0][:-20] + '????_???_??' + csvfilenames[0][-9:]
            tmplogfile = logfilenames[0][:-20] + '????_???_??' + logfilenames[0][-9:]
            logger.info(f"Run {runidx+1} matched to {tmpcsvfile} and {tmplogfile}")

        # Find the times when the 4th stimulus appeared for each trial
        Stim4Times = rundata.loc[rundata['Procedure'] != 'Null','stim4_time'].values
        Stim4Times = Stim4Times[~np.isnan(Stim4Times)]

        logvals = logdata.iloc[:,2].values
        trigidx = 0
        keypressidx = 0
        ntidx = 0
        for lidx in range(len(logvals)):
            # For the log lines that initialize each trial, if there's
            # "('Expected_Response', 1)" then a button press is expected
            # Identify those trials and log their trial number "TrialN"
            if 'New trial (' in logvals[lidx]:
                tmp = logdata.iloc[lidx,2]
                tmpidx = np.char.find(tmp, 'Expected_Response')
                tmpbool = tmp[tmpidx+20]
                if tmpbool == '1':
                    Rtrialstartidx = np.char.find(tmp,'TrialN')
                    Rtrialendidx = np.char.find(tmp, "), ('ProcedureID'")
                    tmpTrialNumber = float(tmp[(Rtrialstartidx+9):Rtrialendidx])
                    ExpectedResponseTimes[ntidx] = Stim4Times[int(tmpTrialNumber-1)]
                    ntidx+=1

            # Log the trigger times when each fMRI volume starts to be acquired
            if 'Keypress: t' in logvals[lidx]:
                triggertimes[trigidx] = logdata.iloc[lidx,0]
                trigidx+=1

            # Log the times when any button is pressed by the participant
            if any(x in logvals[lidx] for x in ButtonKeys):
                keypresstimes[keypressidx] = logdata.iloc[lidx,0]
                keypressidx+=1

        # Truncate the hacky extra long arrays I stated with
        ExpectedResponseTimes = ExpectedResponseTimes[:ntidx]
        triggertimes = triggertimes[:trigidx]
        # The difference between every 2 trigger pulses should be the TR (with error form keyboard sampling variation)
        VolSpacing = triggertimes[1:]-triggertimes[:-1]

        # keypresstimes are a global clock while the Stim4Times are initialized
        # by the first TR. Subtract the first trigger time so they are on the same clock
        keypresstimes = keypresstimes[:keypressidx]-triggertimes[0]

        tmp_negkeypress = keypresstimes < 0
        if tmp_negkeypress.any():
            logger.info(f"NOTE: Removing keypress(es) {keypresstimes[tmp_negkeypress]}sec before the start of the scan")
            keypresstimes = keypresstimes[not tmp_negkeypress]
        tmp_scanlength = triggertimes[-1]-triggertimes[0]
        tmp_postscankeypress = keypresstimes > tmp_scanlength
        if tmp_postscankeypress.any():
            logger.info(f"NOTE: Removing keypress(es) {keypresstimes[tmp_postscankeypress]}sec after the end of the scan")
            keypresstimes = keypresstimes[not tmp_postscankeypress]


        # Go through all trials where a response is expected and count trials with or without a response thats
        # 0.1 sec before the expected response to 3 sec after (starting before in case there are any frame/timer refresh issues)
        MissedResponseCount = 0
        CorrectResponseCount = 0
        for eidx in range(len(ExpectedResponseTimes)):
            tmp = np.any((keypresstimes >= (ExpectedResponseTimes[eidx]-0.1)) & (keypresstimes <= (3+ExpectedResponseTimes[eidx])))
            if tmp:
                CorrectResponseCount += 1
            else:
                MissedResponseCount += 1

        # Go through all keypresses and log the key presses that are correct or incorrect
        # Note: For now, ALL key presses are given to the GLM in one regressor, but
        #   tracking correct and incorrect responses is useful to gauge attention level
        CorrectKeypressTimes = np.empty(len(keypresstimes))
        IncorrectKeypressTimes = np.empty(len(keypresstimes))
        cidx=0
        iidx=0
        for kidx in range(len(keypresstimes)):
            tmp = np.any(((ExpectedResponseTimes-0.1)<=keypresstimes[kidx]) & (ExpectedResponseTimes>=(keypresstimes[kidx]-3)))
            if tmp:
                CorrectKeypressTimes[cidx] = keypresstimes[kidx]
                cidx += 1
            else:
                IncorrectKeypressTimes[iidx] = keypresstimes[kidx]
                iidx += 1
        CorrectKeypressTimes = CorrectKeypressTimes[:cidx]
        IncorrectKeypressTimes = IncorrectKeypressTimes[:iidx]
        if runidx == 0:
            AllVolSpacing = VolSpacing
        else:
            AllVolSpacing = np.concatenate((AllVolSpacing, VolSpacing), axis=0)
        logger.info(f"VolumeSpacing (TR): mean {np.mean(VolSpacing)} std {np.std(VolSpacing)} absmax {np.max(np.abs(VolSpacing-1.5))}")
        logger.info(f"Correct Keypress Times: {CorrectKeypressTimes}")
        logger.info(f"Incorrect Keypress Times: {IncorrectKeypressTimes}")
        logger.info(f"Correct, Missed, Incorrect Keypress Count: {CorrectResponseCount} {MissedResponseCount} {len(IncorrectKeypressTimes)}")
        KeypressTimesAllRuns.append(keypresstimes)
        
        AllCorrectCount += CorrectResponseCount
        AllMissedCount += MissedResponseCount
        AllIncorrectCount += len(IncorrectKeypressTimes)
        AllExpectedCount += len(ExpectedResponseTimes)

    AllResponseTotals = (f"Total Correct {AllCorrectCount}, Missed "
                         f"{AllMissedCount}, Incorrect {AllIncorrectCount}, "
                         f"Expected {AllExpectedCount}")
    print(AllResponseTotals)
    logger.info(AllResponseTotals)

    AllTRTotals = (f"VolumeSpacing (TR): mean {np.mean(AllVolSpacing)} "
                   f"std {np.std(AllVolSpacing)} absmax "
                   f"{np.max(np.abs(AllVolSpacing-1.5))} "
                   f"Total Volumes {len(AllVolSpacing)}")
    print(AllTRTotals)
    logger.info(AllTRTotals)

    # Save all the keypress times
    if os.path.exists(f"sub-{sbjnum}_Keypress_Times.1D"):
        os.remove(f"sub-{sbjnum}_Keypress_Times.1D")
    with open(f"sub-{sbjnum}_Keypress_Times.1D", mode='a') as keyfile:
        for runidx in range(len(RunNums)):
            np.savetxt(keyfile, KeypressTimesAllRuns[runidx], fmt='%4.1f', newline="\t")
            np.savetxt(keyfile, [''], fmt='%s')




if __name__ == '__main__':
    main()