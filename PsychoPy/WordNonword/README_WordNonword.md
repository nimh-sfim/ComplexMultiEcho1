# Word vs Nonword & Visual vs Audio task

Script location:
- The psychopy script to run is [WordNonword_fastloc.py](WordNonword_fastloc.py)
- The task is based on [Malins, et al (2016). "Dough, tough, cough, rough: A "fast" fMRI localizer of component processes in reading." Neuropsychologia](https://doi.org/10.1016/j.neuropsychologia.2016.08.027).

Stimulus conditions:
- We are using 4 stimulus conditions from that paper:
    1. Visual unrelated words
    2. Audio unrelated words
    3. Visual false font non-words (wingdings)
    4. Audio words coded to non-words

Basic instructions:
- Each run includes 12 trials for each condition and the intent is to collect 3 runs per volunteer.
The stimuli are presented in groups of 4 of the same condition, each 1 sec apart (4 sec of stimulation/trial)
- Participants are instructed to press a button if the same stimulus appears twice in a group of 4.
- All groups of 4 stimuli/trial are listed in [AllStimuli.csv](AllStimuli.csv) and the sound files for each word are the [sound_files](./sound_files/) subdirectory

Stimulus order:
- There are 9 hard-coded stimulus orders. These were generated using [CreatingStimuliOrders.ipynb](CreatingStimuliOrders.ipynb). These orders are in files like [WordNonword_Run1.csv](WordNonword_Run1.csv.

TR & inter-trial-interval (ITI) considerations:
Here are a few key things to keep in mind regarding how these files interact with the Psychopy script:
  - It is recommended that the First and last trial "Procedure" column is "Null" to create time before the first and after the last trial. The font still needs to be "Arial" or else the script is unhappy (easier to set the font than add another conditional to the script)
  - Note that the initial ITI might be longer than typical (16 sec). This is to give the noise cancelling headphones more time to learn the scanner noise before the first trial begins
  - The initial column uses the numbers in [AllStimuli.csv](AllStimuli.csv) in case anyone wants to more easily connect the two back.
  - The "ITISec" column is the gap between the **starts** of trials so an 8sec ITI with a 4 sec trial means there's only 4 sec of no stimulation between trials
  - The script automatically changes the ITIs so that each trial begins at the start of a TR, and the shortest permissible ITI is 8 sec. With a 1.5 sec TR, if ITISec=8, then the actual ITI is 9.
  - A few TR options are hard-coded into the launching window in Psychopy, if you add another TR to that window, it should be able to use it without any additional changes. When you run the script, the log will include a line that lists the expected length of the scan

Running the script:
- When running the script, you can enter a subject ID, and select one of the 9 runs. There are two additional runs:
  -[WordNonword_shorttest.csv](WordNonword_shorttest.csv) includes one trial of each type and is useful for introducting participants to the task.
  -[WordNonword_audtest.csv](WordNonword_audtest.csv) is only audio trials and is useful for making sure the participant can hear the stimuli in the scanner
- Once the script is run [CreateEventTimesForGLM.py](CreateEventTimesForGLM.py) can be used to generate timing files for AFNI and it also includes checks to make sure the script ran as expected, summarizes task accuracy, and shows the average TR as recorded by the TTL pulses in Psychopy.
