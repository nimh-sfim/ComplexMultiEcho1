#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    Original Experiment Name:        fastloc_malins, v4.0, 13-09-2017
    Original Script Author:          Sibylla Leon Guerrero
    Updating Authors:       Ramya Varadarajan & Dan Handwerker
    Updating Note:          Now works in PsychoPy v2021.2.3
                            Visual stimuli are spaced by 1 sec, just like audio stimuli
    Design  Author:==
    Malins, J. G., Gumkowski, N., Buis, B., Molfese, P., Rueckl, J. G., Frost, S. J.,  rbrrgrr
        Mencl, W. E. (2016). Dough, tough, cough, rough: A "fast" fMRI localizer of 
        component processes in reading. Neuropsychologia, 91, 394406.t
    Software Author:
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
    """

# --------- Import Components --------------------------------------------------
# 
from __future__ import absolute_import, division
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle
import os           # system and path functions
import sys          # to get file system encoding


# --------- Set Up Environment --------------------------------------------------
# Start the global clock right away
globalClock = core.MonotonicClock() 

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'fastloc_malins_v4' 
expInfo = {'sync': u't', 'end_break': 'space', 
            'abort': 'escape','Choose': 'RUN 0 for Sound Test; RUN 1-8 for task',
            'RUN':['0','1', '2', '3', '4', '5', '6', '7', '8', '99'], 'TR':['2000', '650'], 'ID': u''}

expInfo['date'] = data.getDateStr() 
expInfo['expName'] = expName
ID = expInfo['ID']

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName,
        fixed=['sync','end_break','abort','expName', 'Choose'])
if dlg.OK:  print(expInfo)
else:       print('User Cancelled'); core.quit() 

# Data file name stem = absolute path + name + ID number + date
filename = _thisDir + os.sep + 'data/%s_%s_RUN%s_%s' %(expInfo['ID'], expName, 
                expInfo['RUN'], expInfo['date'])

# An ExperimentHandler for data saving
thisExp = data.ExperimentHandler(name=expName, version='4',
        extraInfo=expInfo, runtimeInfo=None, originPath=None,
        savePickle=True, saveWideText=True, dataFileName=filename)


# ------------------------------------------------------------
#       Edit experiment parameters
# ------------------------------------------------------------
# Set experiment parameters: run onset, ends and test stimuli
stimuli = '%s%s%s' %('fastloc_newrun',expInfo['RUN'],'.xlsx')
stimDuration = 0.600
soundDuration = 0.900
# Each stimulus is set to appear 1s after the previous stimulus as defined later in the code
# isiDuration = 0.200

# ------------------------------------------------------------


# save a log file for detailed verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  

endExpNow = False  # flag for 'escape' or other condition => quit the exp


# Setup the Window
win = visual.Window(
    size=(1920, 1080), fullscr=True, screen=0,
    allowGUI=False, allowStencil=False, monitor='testMonitor', 
    color=[0.004,0.004,0.004], colorSpace='rgb', useFBO=True)


# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:    frameDur = 1.0 / round(expInfo['frameRate'])
else:                               frameDur = 1.0 / 60.0  # if measuring doesn't work, then guess

#   Calculate the number of frames for the trial stimuli & ISIs
stimFrames = round(stimDuration * expInfo['frameRate'])
soundFrames = round(soundDuration * expInfo['frameRate'])
# isiFrames = round(isiDuration * expInfo['frameRate'])

# Create some handy timers
waitClock = core.Clock()                # to track the wait time
trialClock = core.Clock()               # to track relative time for each trial
endClock = core.Clock()                 # to track relative end time

# Initialize text & fill components
rect0 = visual.Rect(        #RV: rect0 is the rectangle in the middle of the screen before the starting key
    win=win, name='rect0',
    width=(0.5), height=(0.45),
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[-1.000,-1.000,-1.000], lineColorSpace='rgb',
    fillColor=[-1.000,-1.000,-1.000], fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)

rect1 = visual.Rect(    #RV: rect1 is the rectangle in the middle of the screen after the starting key (a, e, u, l, =, etc)
    win=win, name='rect0',
    width=(0.5), height=(0.45),
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[-1.000,-1.000,-1.000], lineColorSpace='rgb',
    fillColor=[-1.000,-1.000,-1.000], fillColorSpace='rgb',
    opacity=1, depth=-1.0, interpolate=True)
    

stim1 = visual.TextStim(win=win, name='stim1',   # the starting keys
    text='',
    font=u'Arial', units = 'cm',
    pos=[0, 0], height=1.41, wrapWidth=None, ori=0,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-2.0);
stim2 = visual.TextStim(win=win, name='stim2',
    text='',
    font=u'Arial', units = 'cm',
    pos=(0, 0), height=1.41, wrapWidth=None, ori=0,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-3.0);
stim3 = visual.TextStim(win=win, name='stim3',
    text='',
    font=u'Arial', units = 'cm',
    pos=(0, 0), height=1.41, wrapWidth=None, ori=0,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-4.0);
stim4 = visual.TextStim(win=win, name='stim4',
    text='',
    font=u'Arial', units = 'cm',
    pos=(0, 0), height=1.41, wrapWidth=None, ori=0,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=-5.0);

setupText = visual.TextStim(win=win, name='setupText',
    text='waiting for ready...\n\n<spacebar>', 
    font='Arial', units = 'cm', ori = 0,
    pos=[0, 0], height=0.8, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    alignText='center', anchorHoriz='center', depth=-1.0);

goodjob = visual.TextStim(win=win, name='goodjob',
    text=u'Great job!\n\nYou are all done with this set.', 
    font=u'Arial', units = 'cm', alignText='center', anchorHoriz='center',
    pos=(0, 0), height=1, wrapWidth=None, ori=0, 
    color=u'black', colorSpace='rgb', opacity=1,
    depth=-1.0);
    
#   Initialize sounds
sound1 = sound.Sound('A', secs=-0.8)
sound1.setVolume(0.5)
sound2 = sound.Sound('A', secs=-0.8)
sound2.setVolume(0.5)
sound3 = sound.Sound('A', secs=-0.8)
sound3.setVolume(0.5)
sound4 = sound.Sound('A', secs=-0.8)
sound4.setVolume(0.5)



# ---------- Define Visual Trials -------------------------------------------

def VisualTrial():
    # ------Initialize Routine "trial"-----------------------------------
    t = 0.0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    
    # update component parameters for each repeat
    if Font == "Arial": Height = 1.8
    elif Font == "Wingdings": Height = 1.5
    
    stim1.setText(target1); stim1.setFont(Font); stim1.setHeight(Height); #RV: this is what makes the stimulus show up on the screen in word trials 
    stim2.setText(target2); stim2.setFont(Font); stim2.setHeight(Height);
    stim3.setText(target3); stim3.setFont(Font); stim3.setHeight(Height);
    stim4.setText(target4); stim4.setFont(Font); stim4.setHeight(Height);
    
    if expInfo['TR'] == '650':   
        StartTR = StartTR650
        thisITI = ITI650
    elif expInfo['TR'] == '2000':
        thisITI = ITI2000
        StartTR = StartTR2000
    
    # keep track of which components have finished
    trialComponents = [rect1, stim1, stim2, stim3, stim4]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine:
        # get current time
        gt = globalClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
    
        # *rect1* updates
        if gt >= 0 and rect1.status == NOT_STARTED:
            # keep track of start time/frame for later
            rect1.frameNStart = frameN  # exact frame index
            rect1.setAutoDraw(True)
        rect1_frameRemains = StartTR + thisITI - 0.05 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if rect1.status == STARTED and stim4.status == STOPPED:
            rect1.setAutoDraw(False)
        
        # *stim1* updates
        if gt >= StartTR + trigger_time -0.017 - win.monitorFramePeriod * 0.75 and stim1.status == NOT_STARTED:
            # keep track of start time/frame for later
            stim1.frameNStart = frameN  # exact frame index
            stim1.setAutoDraw(True)
            win.flip()
            stim1.tStart = globalClock.getTime()
        if stim1.status == STARTED and frameN >= (stim1.frameNStart + stimFrames-1):
            stim1.setAutoDraw(False)
        
        # *stim2* updates
        if gt >= StartTR+1+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and stim2.status == NOT_STARTED:
            # keep track of start time/frame for later
            stim2.frameNStart = frameN  # exact frame index
            stim2.setAutoDraw(True)
            win.flip()
            stim2.tStart = globalClock.getTime()
        if stim2.status == STARTED and frameN >= (stim2.frameNStart + stimFrames-1):
            stim2.setAutoDraw(False)
        
        # *stim3* updates
        if gt >= StartTR+2+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and stim3.status == NOT_STARTED:
            # keep track of start time/frame for later
            stim3.frameNStart = frameN  # exact frame index
            stim3.setAutoDraw(True)
            win.flip()
            stim3.tStart = globalClock.getTime()
        if stim3.status == STARTED and frameN >= (stim3.frameNStart + stimFrames-1):
            stim3.setAutoDraw(False)
        
        # *stim4* updates
        if gt >= StartTR+3+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and stim4.status == NOT_STARTED:
            # keep track of start time/frame for later
            stim4.frameNStart = frameN  # exact frame index
            stim4.setAutoDraw(True)
            win.flip()
            stim4.tStart = globalClock.getTime()
        if stim4.status == STARTED and frameN >= (stim4.frameNStart + stimFrames-1):
            stim4.setAutoDraw(False)
        
    
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine: 
            win.flip()

    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"): thisComponent.setAutoDraw(False)
    
    # Save trial times
    currentLoop.addData('testMonitor', trialClock.getTime())
    currentLoop.addData('global time', globalClock.getTime())
    currentLoop.addData('stim1_time', stim1.tStart - trigger_time)
    currentLoop.addData('stim2_time', stim2.tStart - trigger_time)
    currentLoop.addData('stim3_time', stim3.tStart - trigger_time)
    currentLoop.addData('stim4_time', stim4.tStart - trigger_time)

# ----------------------------------------------------------------------------------------------

# ---------- Define Audio Trials -------------------------------------------

def AudioTrial():
    # ------Initialize Routine "trial"-----------------------------------
    t = 0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    
    # update component parameters for each repeat
    sound1.setSound('sound_files/' + target1 + '.wav', secs=0.8)
    sound2.setSound('sound_files/' + target2 + '.wav', secs=0.8)
    sound3.setSound('sound_files/' + target3 + '.wav', secs=0.8)
    sound4.setSound('sound_files/' + target4 + '.wav', secs=0.8)
    if expInfo['TR'] == '650':   
        StartTR = StartTR650
        thisITI = ITI650
    elif expInfo['TR'] == '2000':
        thisITI = ITI2000
        StartTR = StartTR2000
    
    # keep track of which components have finished
    trialComponents = [rect1, sound1, sound2, sound3, sound4]
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    # -------Start Routine "trial"-------
    while continueRoutine:
        # get current time
        gt = globalClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
    
        # *rect1* updates
        if gt >= 0 and rect1.status == NOT_STARTED:
            # keep track of start time/frame for later
            rect1.frameNStart = frameN  # exact frame index
            rect1.setAutoDraw(True)
        rect1_frameRemains = StartTR + thisITI - 0.05 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if rect1.status == STARTED and sound4.status == STOPPED:
            rect1.setAutoDraw(False)
        
        # *sound1* updates
        if gt >= StartTR + trigger_time -0.017 - win.monitorFramePeriod * 0.75 and sound1.status == NOT_STARTED:
            # keep track of start time/frame for later
            sound1.frameNStart = frameN  # exact frame index
            sound1.play()
            win.flip()
            sound1.tStart = globalClock.getTime()
        if sound1.status == STARTED and frameN >= (sound1.frameNStart + soundFrames-1):
            sound1.stop()
        
        # *sound2* updates
        if gt >= StartTR+1.0+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and sound2.status == NOT_STARTED:
            # keep track of start time/frame for later
            sound2.frameNStart = frameN  # exact frame index
            sound2.play()
            win.flip()
            sound2.tStart = globalClock.getTime()
        if sound2.status == STARTED and frameN >= (sound2.frameNStart + soundFrames-1):
            sound2.stop()
        
        # *sound3* updates
        if gt >= StartTR+2.0+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and sound3.status == NOT_STARTED:
            # keep track of start time/frame for later
            sound3.frameNStart = frameN  # exact frame index
            sound3.play()
            win.flip()
            sound3.tStart = globalClock.getTime()
        if sound3.status == STARTED and frameN >= (sound3.frameNStart + soundFrames-1):
            sound3.stop()
        
        # *sound4* updates
        if gt >= StartTR+3.0+trigger_time -0.017 - win.monitorFramePeriod * 0.75 and sound4.status == NOT_STARTED:
            # keep track of start time/frame for later
            sound4.frameNStart = frameN  # exact frame index
            sound4.play()
            win.flip()
            sound4.tStart = globalClock.getTime()
        if sound4.status == STARTED and frameN >= (sound4.frameNStart + soundFrames-1):
            sound4.stop()
        
    
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine: 
            win.flip()

    # -------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"): thisComponent.setAutoDraw(False)
    
    # Save trial times
    currentLoop.addData('trial_duration', trialClock.getTime())
    currentLoop.addData('global time', globalClock.getTime())
    currentLoop.addData('stim1_time', sound1.tStart - trigger_time)
    currentLoop.addData('stim2_time', sound2.tStart - trigger_time)
    currentLoop.addData('stim3_time', sound3.tStart - trigger_time)
    currentLoop.addData('stim4_time', sound4.tStart - trigger_time)

# ----------------------------------------------------------------------------------------------




# --------- Run Experiment --------------------------------------------------



# ------Initialize Routine "Setup"-------
t = 0
waitClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
key_resp_1 = event.BuilderKeyResponse()  #RV: this controls the first spacebar keypress

# keep track of which components have finished
setupComponents = [setupText, key_resp_1]
for thisComponent in setupComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED


# -------Start Routine "Setup"-------

while continueRoutine:
    t = waitClock.getTime()

# update/draw components on each frame
    # *key_resp_1* updates
    if t >= 0.0 and key_resp_1.status == NOT_STARTED: #RV: controls when subject can do the spacebar to start trial (at time 0)
        key_resp_1.tStart = t  
        key_resp_1.status = STARTED
        key_resp_1.clock.reset()  # now t=0
        event.clearEvents()
    if key_resp_1.status == STARTED:
        theseKeys1 = event.getKeys(keyList=expInfo['end_break'])
        # check for quit:
        if "escape" in theseKeys1:  endExpNow = True
        if len(theseKeys1) > 0:     continueRoutine = False
            
    # *setupText* updates
    if t >= 0.0 and setupText.status == NOT_STARTED:
        setupText.tStart = t  
        setupText.setAutoDraw(True)
            
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in setupComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Setup"-------
for thisComponent in setupComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
        
thisExp.nextEntry()



# ------Initialize Routine "Wait"-------
waitClock.reset()  # clock
frameN = -1
continueRoutine = True
# update component parameters for each repeat
key_resp_2 = event.BuilderKeyResponse() #RV: this controls the second keypress

# keep track of which components have finished
waitComponents = [rect0, key_resp_2]
for thisComponent in waitComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

# -------Start Routine "Wait"-------

while continueRoutine:
    t = waitClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)

    # update/draw components on each frame

    # rect0 updates
    if t >= 0 and rect0.status == NOT_STARTED:
        # keep track of start time/frame for later
        rect0.tStart = t
        rect0.frameNStart = frameN  # exact frame index
        rect0.setAutoDraw(True)  
    
    # *key_resp_2* updates
    if t >= 0.0 and key_resp_2.status == NOT_STARTED: #RV: controls the time between spacebar and starting trial by pressing t
        key_resp_2.tStart = t 
        key_resp_2.frameNStart = frameN  # exact frame index
        key_resp_2.status = STARTED
        # keyboard checking is just starting
        win.callOnFlip(key_resp_1.clock.reset)  # t=0 on next screen flip
        event.clearEvents(eventType='keyboard')
    if key_resp_2.status == STARTED:
        theseKeys2 = event.getKeys(keyList=expInfo['sync']) #RV: returns a list of keys that were pressed
        
        # check for quit:
        if "escape" in theseKeys2:
            endExpNow = True
        if len(theseKeys2) > 0:  # at least one key was pressed
            key_resp_2.keys = theseKeys2[-1]  # just the last key pressed
            trigger_time = globalClock.getTime() # RV: this controls the delay between pressing "t" and starting the trial
            # a response ends the routine
            continueRoutine = False
            
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in waitComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

# -------Ending Routine "Wait"-------
for thisComponent in waitComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
        
# check responses
if key_resp_2.keys in ['', [], None]:  # No response was made
    key_resp_2.keys=None
thisExp.addData('key_resp_2.keys',key_resp_2.keys)
if key_resp_2.keys != None:  # we had a response
    thisExp.addData('global trigger time', trigger_time)
    
thisExp.nextEntry()


# -------Set up trial loop "trials"-------

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1, method='sequential',
                           extraInfo=expInfo, originPath=-1,
                           trialList=data.importConditions(stimuli),
                           seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
print("thisTrial initial")

# abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial.keys():
        print(thisTrial)
        print("paramName " + paramName)
        exec(paramName + '= thisTrial[\'' + paramName + '\']')

for thisTrial in trials:
    currentLoop = trials
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial.keys():
            exec(paramName + '= thisTrial[\'' + paramName + '\']')



    # ------Initialize Routine "trial"-----------------------------------
    t = 0.0
    trialClock.reset()  # clock
    frameN = -1
    continueRoutine = True
    
    # update component parameters for each repeat
    trialType = Procedure
    
    if trialType != "AudProc":  VisualTrial() 
    else:  AudioTrial()
     
    # One loop completed, go to next
    thisExp.nextEntry()
    
# completed 1 repeats of 'trials'
   

        
# ------Initialize Routine "end"-------
t = 0
endClock.reset()  # clock
frameN = -1
continueRoutine = True

# keep track of which components have finished
endComponents = [goodjob]
for thisComponent in endComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED


# -------Start Routine "end"-------
while continueRoutine:
    # get current time
    t = endClock.getTime()
    
    # *goodjob* updates
    if t >= 0.0 and goodjob.status == NOT_STARTED:
        # keep track of start time/frame for later
        goodjob.tStart = t
        goodjob.setAutoDraw(True)  
    if goodjob.status == STARTED and t >= 5.0:
        goodjob.setAutoDraw(False)
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in endComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  
        win.flip()


# -------Ending Routine "end"-------
for thisComponent in endComponents:
    if hasattr(thisComponent, "setAutoDraw"):  
        thisComponent.setAutoDraw(False)
        sound1.stop()
        sound2.stop()
        sound3.stop()
        sound4.stop()

# Save csv file (autosave feature isn't working for wide text in PsychoPy 1.85.3)
thisExp.saveAsWideText(filename+'.csv')

# log and data file will auto-save on quit
win.close()
core.quit()

