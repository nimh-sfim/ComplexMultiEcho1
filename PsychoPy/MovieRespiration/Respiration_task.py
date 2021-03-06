# Respiration task (2 runs)

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
expName = 'Resp_Task' 
expInfo = {'sync': u't', 'end_break': 'space', 
            'abort': 'escape','Choose': 'RUN 0 for Sound Test; RUN 1-3 for task',
            'RUN':['0','1', '2','3'], 'TR':['2000','650','1500'], 'ID': u''}

expInfo['date'] = data.getDateStr() 
expInfo['expName'] = expName
ID = expInfo['ID']

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName,
        fixed=['sync','end_break','abort','expName', 'Choose'])
if dlg.OK:  print(expInfo)
else:       print('User Cancelled'); core.quit() 

# Data file name stem = absolute path + name + ID number + date
filename = _thisDir + os.sep + 'RunLogs/%s_%s_RUN%s_%s' %(expInfo['ID'], expName, 
                expInfo['RUN'], expInfo['date'])

# An ExperimentHandler for data saving
thisExp = data.ExperimentHandler(name=expName,
        extraInfo=expInfo, runtimeInfo=None, originPath=None,
        savePickle=True, saveWideText=True, dataFileName=filename)

# save a log file for detailed verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# CHOOSE YOUR monitor
# =======================
fullScreen=True # set to true during experiments

# CREATE SCREEN
# ================
# MAIN WINDOW
win = visual.Window(
    size=[800,600], fullscr=fullScreen, screen=0, 
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

mat1_0,mat1_1,mat1_2 = [(amplitude[0], i) for i in frequency],[(amplitude[1], i) for i in frequency],[(amplitude[2], i) for i in frequency]
mat1 = mat1_0+mat1_1+mat1_2     # run 1

if expInfo['RUN'] == 1:
    matrix_run = mat1
else:
    matrix_run = mat1       # run matrix 1 on all practice & real runs

# log matrix with tuple (ampl[0], freq[1])
logging.log(level=logging.EXP,msg=f"Current (ampl,freq) matrix for run {expInfo['RUN']}: {matrix_run}")

resp_pattern = [np.sin(i[1]*np.linspace(0,300,num=3000))*i[0]+0.11 for i in matrix_run]
logging.log(level=logging.EXP,msg=f"Current sine function (f(x)) matrix for run {expInfo['RUN']}: {resp_pattern}")


# TASK DURATIONS & TIMING                                                                        TOTAL TIME = (21*5)+(39*5)+18+10.5=328.5s / 1.5 = 219 TRs (+ 4 extra)  ===> 5:34.5 min
# ===================
bubbletime = 60;
blocks = 9;

# =========================================
# SETTING GLOBAL CLOCK
# =========================================                                                       # use the core clock
globalClock = core.Clock()

# ==============================================================================================================================
# ======================                           OBJECTS                            ===============================================================
# ==============================================================================================================================

# Bubble OBJ
bubble = visual.ShapeStim(
    win=win,name='bubble stimulus',
    size=(0.1, 0.1),vertices='circle',
    ori=0.0,pos=(0, 0),lineWidth=1.0,
    colorSpace='rgb',lineColor=[0.8824, 0.9451, 1.0000],
    fillColor=None,opacity=0.3,interpolate=True,autoLog=False)

# ==============================================================
# ===========                INSTRUCTIONS                    ==============
# ==============================================================
Instr_Video_T='TASK NAME: RESPIRATION ONLY\n\n Relax & breathe with the bubble cue.';
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

# REST BUBBLE --> 60s intervals
# =========================
bubbletimer = core.Clock()
bubbletimer.add(bubbletime)
logging.log(level=logging.EXP, msg=f"Respiration START: {globalClock.getTime()}")
for i in range(0,9):    # i = resp_pattern[0] 
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
    bubbletimer.add(bubbletime)     # re-add the time once it runs out (at end of while loop)
bubble.setAutoDraw(False)
win.flip(); win.logOnFlip(level=logging.EXP, msg=f"Respiration END: {globalClock.getTime()}")

# get the end global clock time
win.flip(); win.logOnFlip('Experiment END = %s' %(globalClock.getTime()),logging.DATA);

win.close()
core.quit()
