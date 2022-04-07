# Movie w/ Respiration task (2-3 runs)

#GENERATE WITH:
# ffmpeg -sameq -ss [start_seconds] -t [duration_seconds] -i [input_file] [outputfile]
from psychopy import visual,event,core,gui,logging,data,prefs
import random
import os,time
import numpy as np

# See: https://psychopy.org/api/preferences.html for why this line needs to be before importing sound
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound
# --------- Set Up Environment --------------------------------------------------

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expInfo = {'sync': u't', 'end_break': 'space', 
            'abort': 'escape','Choose': 'RUN 0 for Sound Test; RUN 1-3 for task',
            'RUN': ['A','B', 'C'], 'ShowMovie': ['yes', 'no'], 'ID': u''}



expInfo['date'] = data.getDateStr() 
ID = expInfo['ID']

dlg = gui.DlgFromDict(dictionary=expInfo, title="Enter Run Info",
        fixed=['sync','end_break','abort','Choose'])
if dlg.OK:  print(expInfo)
else:       print('User Cancelled'); core.quit() 

if expInfo['ShowMovie'] == 'yes':
    expName = 'MovieResp'
    ShowMovie = True
else:
    expName = 'Resp'
    ShowMovie = False

expInfo['expName'] = expName

# Data file name stem = absolute path + name + ID number + date
filename = f"{_thisDir}{os.sep}RunLogs{os.sep}{expInfo['ID']}_{expName}_RUN{expInfo['RUN']}_{expInfo['date']}"

# An ExperimentHandler for data saving
thisExp = data.ExperimentHandler(name=expName,
        extraInfo=expInfo, runtimeInfo=None, originPath=None,
        savePickle=True, saveWideText=True, dataFileName=filename)

# save a log file for detailed verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# logging.log(level=logging.EXP,msg="some message here") --> log message timestamped by time of logging
# win.logOnFlip(level=logging.EXP,msg="some message here") --> log message timestamped by frame flip (time when stim appears)

# CHOOSE YOUR monitor
# =======================
fullScreen=True # set to true during experiments

# CREATE SCREEN
# ================
# MAIN WINDOW
win = visual.Window(
    size=[1920, 1080], fullscr=fullScreen, screen=0, 
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height', depthBits=24)

# ==================================================================
# Allow Escape or "q" key   --> during "while" loop, while stim is AutoDrawing
# ==================================================================
def escape():
    for key in event.getKeys(keyList=['escape','q'], timeStamped=False):
        if key in ['escape','q']:                                                                       #could also be if key != [] or something to that effect
            win.close();
            core.quit();

escape()

# ==============================================================
#       BUBBLE STIM PARAMETERS (BY RUN)
#   All three runs have the same breathing patterns that starts
#   at a different point
# ==============================================================

if expInfo['RUN'] == 'A':
    BreathingPhase = 0
elif expInfo['RUN'] == 'B':
    BreathingPhase = np.pi
elif expInfo['RUN'] == 'C':
    BreathingPhase = np.pi/2


# TASK DURATIONS & TIMING                                                                        TOTAL TIME = (21*5)+(39*5)+18+10.5=328.5s / 1.5 = 219 TRs (+ 4 extra)  ===> 5:34.5 min
# ===================

bubbletime_loginterval = 0.5; # Log circle size every 0.5 sec

premovietime = 21
movietime = 420
postmovietime = 15
totaltime = premovietime + movietime + postmovietime


# CREATE BREATHING PATTERNS
# =============================
amp = 0.1 # amplitude of the carrier frequency
AMamp = 0.05 # Amplitude of the AM (depth) modulation
meanshift = 0.11 # The mean circle diameter should always be positive
# Due to frame rate differences and rounding, the final time point might be a few frames past the end of BreathingPattern
#   add an extra second to make sure the script never gets past the last value
TimingFudge = 1 
FC = 1/5 # Averaging 5s breathing cycles
FM = 1/60 # Breathing frequency modulates over 60s cycles
FCscale = (2*FC*np.pi)
FMscale = (2*FM*np.pi)
FreqDev = FC-1/6 # Frequency deviation between 2s and 3s breathing cycles
ModFreq = FreqDev/FM
# Time in seconds spaced in 0.1 second intervals
TimeInSec = np.round(np.linspace(0,totaltime+TimingFudge,num=(totaltime+TimingFudge)*10+1), decimals=5)
AMmod = -AMamp*np.cos(2*np.pi*TimeInSec*FM+BreathingPhase)+0.2
BreathingPattern = AMmod*np.sin(2*np.pi*FC*TimeInSec + ModFreq*np.sin(2*np.pi*FM*TimeInSec+BreathingPhase)+BreathingPhase)*amp+meanshift


logging.log(level=logging.EXP,msg=f"Breathing Run {expInfo['RUN']} with Phase={BreathingPhase}, amp={amp}, AMamp={AMamp}, meanshift={meanshift}, FC={FC}, FM={FM}, FreqDev={FreqDev}")
logging.log(level=logging.EXP, msg=f"BreathingPattern {BreathingPattern}")

# =========================================
# SETTING GLOBAL CLOCK
# =========================================                                                       # use the core clock
globalClock = core.Clock()

# ==============================================================================================================================
# ======================                           OBJECTS                            ===============================================================
# ==============================================================================================================================

if ShowMovie:
    #      VIDEO PATH --> from relative path (same dir as script)                                    
    movie_Filename = _thisDir + os.sep + 'spring-blender-open-movie.mp4';
    if not os.path.exists(movie_Filename):
        raise RuntimeError("Video File could not be found:" + os.path.split(movie_Filename)[1])

    # VIDEO OBJ
    movie=visual.MovieStim3(win,movie_Filename,size=(1280,536),pos=(0,0),loop=False,autoLog=False);   # autostart = starts the video automatically when first drawn

# Bubble OBJ
# Note: Changed to line thickness of 3 and opacity of 0.75 for a volunteer who couldn't wear corrective lenses
bubble = visual.ShapeStim(
    win=win,name='bubble stimulus',
    size=(0.1, 0.1),vertices='circle',
    ori=0.0,pos=(0, 0),lineWidth=2.0, #3.0,
    colorSpace='rgb',lineColor=[1, 1, 1],
    fillColor=None,opacity=0.5, #rbg0.75,
    interpolate=True, autoLog=False)

# ==============================================================
# ===========                INSTRUCTIONS                    ==============
# ==============================================================
if ShowMovie:
    Instr_Video_T='Watch the movie while breathing in and out with the circle.';
else:
    Instr_Video_T='Breathe in and out with the circle.';
Instr_Video_S=visual.TextStim(win,text=Instr_Video_T,height=25,units='pix',name='intro',color='black',wrapWidth=800,pos=(0,0));

# ==================================================================
# PRINT FIRST SET OF INSTRUCTIONS AND WAIT FOR TRIGGER
# ==================================================================
Instr_Video_S.draw();win.flip();
win.logOnFlip('Instructions FRAME TIME = %s' %(win.lastFrameT),logging.DATA);
event.waitKeys(keyList=['t']);        # MUST PRESS "T" to trigger rest period!!!                                                                                                                   # Wait for Scanner Trigger.                                                                                                               # Record Scanning Start Time

win.mouseVisible = False
# ==================================================================
# RESET GLOBAL CLOCK & LOG EXP START TIME
# ==================================================================
globalClock.reset()
win.flip(); win.logOnFlip('Experiment START = %s' %(globalClock.getTime()),logging.DATA);

# STARTING REST BUBBLE --> 15s
# =========================
logging.log(level=logging.EXP, msg=f"Respiration START: {globalClock.getTime()}")

exp_timer = core.MonotonicClock()
BubbleLogTime = exp_timer.getTime()
while exp_timer.getTime()<premovietime:
    t = exp_timer.getTime()
    bubble.size = BreathingPattern[round(t*10)]
    bubble.setAutoDraw(True)
    win.update()
    escape()
    if t>(BubbleLogTime+bubbletime_loginterval):
        logging.log(level=logging.EXP, msg=f"Breath circle width pre movie: {bubble.size}")
        BubbleLogTime += bubbletime_loginterval
bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Premovie respiration END: {globalClock.getTime()}")   
 
# MOVIE AND BUBBLE --> 420s
# =========================
movietimer = core.MonotonicClock()
logging.log(level=logging.EXP, msg=f"Movie START: {globalClock.getTime()}")
while movietimer.getTime() < movietime:
    if ShowMovie:
        movie.setAutoDraw(True)
    escape()
    t = exp_timer.getTime()
    bubble.size = BreathingPattern[round(t*10)]
    bubble.setAutoDraw(True)
    win.update()
    escape()
    if t>(BubbleLogTime+bubbletime_loginterval):
        logging.log(level=logging.EXP, msg=f"Breath circle width in movie: {bubble.size}")
        BubbleLogTime += bubbletime_loginterval
if ShowMovie:
    movie.setAutoDraw(False)
bubble.setAutoDraw(False)
        
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Movie END: {globalClock.getTime()}")
escape()

# POST MOVIE BUBBLE --> 15s
# =========================
while exp_timer.getTime()<totaltime:
    t = exp_timer.getTime()
    bubble.size = BreathingPattern[round(t*10)]
    bubble.setAutoDraw(True)
    win.update()
    escape()
    if t>(BubbleLogTime+bubbletime_loginterval):
        logging.log(level=logging.EXP, msg=f"Breath circle width post movie: {bubble.size}")
        BubbleLogTime += bubbletime_loginterval
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Postmovie respiration END: {globalClock.getTime()}")  
        
bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Respiration END: {globalClock.getTime()}")

# get the end global clock time
win.flip(); win.logOnFlip('Experiment END = %s' %(globalClock.getTime()),logging.DATA);

win.close()
core.quit()
