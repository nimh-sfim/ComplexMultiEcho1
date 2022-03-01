# Movie w/ Respiration task (2-3 runs)

#GENERATE WITH:
# ffmpeg -sameq -ss [start_seconds] -t [duration_seconds] -i [input_file] [outputfile]
from psychopy import visual,event,core,gui,logging,data
import random
import os,time
import numpy as np

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
#       Ampl = depth, Freq = speed
# ==============================================================

amplitude = [0.01,0.02,0.03];
frequency = [(1.5*np.pi*0.2),(2*np.pi*0.2),(2.5*np.pi*0.2)];

# 1st matrix
mat1_0,mat1_1,mat1_2 = [(amplitude[0], i) for i in frequency],[(amplitude[1], i) for i in frequency],[(amplitude[2], i) for i in frequency]
mat1 = mat1_0+mat1_1+mat1_2
# 2nd matrix = reverse of 1st matrix
mat2 = mat1[len(mat1)-1::-1]
# 3rd matrix = odd frequencies 1st, even frequencies 2nd
odd = [i for i in mat2 if round(i[1]) % 2 != 0]    # run 3 = odd freq then even freq runs (from mat2 order)
even = [i for i in mat2 if round(i[1]) % 2 == 0]
mat3 = odd+even

# ==============================================================
#       Counterbalancing Subject-Matrix Order
# ==============================================================

if expInfo['RUN'] == 'A':
    matrix_run = mat1
elif expInfo['RUN'] == 'B':
    matrix_run = mat2
elif expInfo['RUN'] == 'C':
    matrix_run = mat3

# log matrix with tuple (ampl[0], freq[1])
logging.log(level=logging.EXP,msg=f"Current (ampl,freq) matrix for run {expInfo['RUN']}: {matrix_run}")

resp_pattern = [np.sin(i[1]*np.linspace(0,300,num=3000))*i[0]+0.11 for i in matrix_run]
logging.log(level=logging.EXP,msg=f"Current sine function (f(x)) matrix for run {expInfo['RUN']}: {resp_pattern}")

# TASK DURATIONS & TIMING                                                                        TOTAL TIME = (21*5)+(39*5)+18+10.5=328.5s / 1.5 = 219 TRs (+ 4 extra)  ===> 5:34.5 min
# ===================
prebubbletime = 12;
bubbletime = 60;
bubbletime_loginterval = 1; # Log circle size every 1 sec
movietime = 420;

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
bubble = visual.ShapeStim(
    win=win,name='bubble stimulus',
    size=(0.1, 0.1),vertices='circle',
    ori=0.0,pos=(0, 0),lineWidth=1.0,
    colorSpace='rgb',lineColor=[1, 1, 1],
    fillColor=None,opacity=1.0,interpolate=True, autoLog=False)

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

# ==================================================================
# RESET GLOBAL CLOCK & LOG EXP START TIME
# ==================================================================
globalClock.reset()
win.flip(); win.logOnFlip('Experiment START = %s' %(globalClock.getTime()),logging.DATA);

# STARTING REST BUBBLE --> 12s
# =========================
bubbletimer = core.Clock()
bubbletimer.add(prebubbletime)      # 12s intervals
logging.log(level=logging.EXP, msg=f"Respiration START: {globalClock.getTime()}")
for i in range(0,1):    # i = resp_pattern[0]
    tmp_timer = core.MonotonicClock()
    tmp_array = resp_pattern[i]
    logging.log(level=logging.EXP, msg=f"Sine Array {i}: {tmp_array}")
    BubbleLogTime = bubbletimer.getTime()
    while bubbletimer.getTime() < 0:  # duration of 60s
        # get the time from the monotonic clock
        t = tmp_timer.getTime();
        bubble.size = tmp_array[round(t*10)]
        bubble.setAutoDraw(True)
        escape()
        # update the window after every draw
        win.update()
        if bubbletimer.getTime()>(BubbleLogTime+bubbletime_loginterval):
            logging.log(level=logging.EXP, msg=f"Breath circle width: {bubble.size}")
            BubbleLogTime += bubbletime_loginterval

    bubbletimer.add(prebubbletime)     # re-add time to clock (at end of while loop)
bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Respiration END: {globalClock.getTime()}")

# MOVIE BUBBLE --> 420s
# =========================
movietimer = core.Clock()
movietimer.add(movietime)
bubbletimer.reset()
bubbletimer.add(bubbletime)     # 60s intervals
BubbleLogTime = bubbletimer.getTime()
logging.log(level=logging.EXP, msg=f"Movie START: {globalClock.getTime()}")
while movietimer.getTime() < 0:
    if ShowMovie:
        movie.setAutoDraw(True)
    escape()
    for i in range(1,8):    # i = resp_pattern[1:8] (1-7)
        tmp_timer = core.MonotonicClock()
        tmp_array = resp_pattern[i]
        logging.log(level=logging.EXP, msg=f"Sine Array {i}: {tmp_array}")
        while bubbletimer.getTime() < 0:  # duration of 60s
            # get the time from the monotonic clock
            t = tmp_timer.getTime();
            bubble.size = tmp_array[round(t*10)]
            bubble.setAutoDraw(True)
            escape()
            # update the window after every draw
            win.update()
            if bubbletimer.getTime()>(BubbleLogTime+bubbletime_loginterval):
                logging.log(level=logging.EXP, msg=f"Breath circle width: {bubble.size}")
                BubbleLogTime += bubbletime_loginterval
            
        bubbletimer.add(bubbletime)     # re-add time to clock (at end of while loop)
    movie.setAutoDraw(False)
    bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Movie END: {globalClock.getTime()}")
    
# REST BUBBLE --> 12s
# =========================
bubbletimer.reset()
bubbletimer.add(prebubbletime)     # 12s intervals
logging.log(level=logging.EXP, msg=f"Respiration START: {globalClock.getTime()}")
for i in range(8,9):    # i = resp_pattern[8]
    tmp_timer = core.MonotonicClock()
    tmp_array = resp_pattern[i]
    BubbleLogTime = bubbletimer.getTime()
    while bubbletimer.getTime() < 0:  # duration of 12s
        # get the time from the monotonic clock
        t = tmp_timer.getTime();
        bubble.size = tmp_array[round(t*10)]
        bubble.setAutoDraw(True)
        escape()
        # update the window after every draw
        win.update()
        if bubbletimer.getTime()>(BubbleLogTime+bubbletime_loginterval):
                logging.log(level=logging.EXP, msg=f"Breath circle width: {bubble.size}")
                BubbleLogTime += bubbletime_loginterval
    logging.log(level=logging.EXP, msg=f"Sine Array {i}: {tmp_array}")
    bubbletimer.add(prebubbletime)     # re-add time to clock (at end of while loop)
bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Respiration END: {globalClock.getTime()}")

# get the end global clock time
win.flip(); win.logOnFlip('Experiment END = %s' %(globalClock.getTime()),logging.DATA);

win.close()
core.quit()
