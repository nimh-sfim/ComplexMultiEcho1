# Movie w/ Respiration task (2-3 runs)

#GENERATE WITH:
# ffmpeg -sameq -ss [start_seconds] -t [duration_seconds] -i [input_file] [outputfile]
from psychopy import visual,event,core,gui,logging,data
import random
import os,time
import numpy as np

# CHOOSE YOUR monitor
# =======================
fullScreen=False # set to true during experiments

# CREATE SCREEN
# ================
# MAIN WINDOW
win=visual.Window([800,600],fullscr=fullScreen,screen=0, 
    winType='pyglet', allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=False, units='height');

# allow window to close with keypress 'q'
for quit in event.getKeys(keyList=['escape','q'], timeStamped=False):
    if quit in ['escape','q']:
        win.close();
        core.quit();

# --------- Set Up Environment --------------------------------------------------
# Start the global clock right away
globalClock = core.MonotonicClock() 
win.flip(); win.logOnFlip('ExpStartTime (global clock) = %s' %(globalClock.getTime()),logging.DATA);

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'Movie_Resp' 
expInfo = {'sync': u't', 'end_break': 'space', 
            'abort': 'escape','Choose': 'RUN 0 for Sound Test; RUN 1-3 for task',
            'RUN':['0','1', '2', '3'], 'TR':['2000','650','1500'], 'ID': u''}

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

# ==============================================================
#       BUBBLE STIM PARAMETERS (BY RUN)
#       Ampl = depth, Freq = speed
# ==============================================================

amplitude = [0.01,0.02,0.03];
frequency = [(1.5*np.pi*0.2),(2*np.pi*0.2),(2.5*np.pi*0.2)];

mat1_0,mat1_1,mat1_2 = [(amplitude[0], i) for i in frequency],[(amplitude[1], i) for i in frequency],[(amplitude[2], i) for i in frequency]
mat1 = mat1_0+mat1_1+mat1_2     # run 1
mat2 = mat1[len(mat1)-1::-1]    # run 2 = reverse of run 1
odd = [i for i in mat2 if round(i[1]) % 2 != 0]    # run 3 = odd freq then even freq runs (from mat2 order)
even = [i for i in mat2 if round(i[1]) % 2 == 0]
mat3 = odd+even

if expInfo['RUN'] == 1:
    matrix_run = mat1
elif expInfo['RUN'] == 2:
    matrix_run = mat2
elif expInfo['RUN'] == 3:
    matrix_run = mat3
else:
    matrix_run = mat1       # run matrix 1 on test runs

resp_pattern = [np.sin(i[1]*np.linspace(0,300,num=3000))*i[0]+0.11 for i in matrix_run]
print("Matrix of array blocks (9) for the run: ", resp_pattern)

# TASK DURATIONS                                                                        TOTAL TIME = (21*5)+(39*5)+18+10.5=328.5s / 1.5 = 219 TRs (+ 4 extra)  ===> 5:34.5 min
# ===================
Rest=60                                        #Duration of additional fixation period immediately after scan starts
movie_Duration=420;                                      # 7 * 60 = 420s
exp_Duration = Rest+movie_Duration+Rest;
numBlocks=9;

# SET LOG FILE NAME
# ====================
#fileDlg = gui.Dlg(title="Run Information");
#fileDlg.addField('File Prefix: ');
#
#fileDlg.show();
#if gui.OK:      # if GUI works --> make log file & record data in it
#    Dlg_Responses=fileDlg.data;
#    LogFilePrefix=Dlg_Responses[0];
#    LogFileName='/Users/holnessmn/Desktop/Tasks_OHBM2022/FishBoy_Movie/Logs/'+LogFilePrefix+'_Log.txt';
#else:           # if not... --> test log
#    print('User Cancelled')
#    LogFileName='/Users/holnessmn/Desktop/Tasks_OHBM2022/FishBoy_Movie/Logs/testLog.txt';

# writing 34 [empty] lines in logfile
#Logger=logging.LogFile(LogFileName,34,'w');
Logger=logging.LogFile(filename,34,'w');


# ==============================================================================================================================
# ======================                           OBJECTS                            ===============================================================
# ==============================================================================================================================

#      VIDEO PATH                                       
movie_Filename='/Users/holnessmn/Desktop/Tasks_OHBM2022/FishBoy_Movie/spring-blender-open-movie.mp4';
if not os.path.exists(movie_Filename):
    raise RuntimeError("Video File could not be found:" + os.path.split(movie_Filename)[1])

# VIDEO OBJ
movie=visual.MovieStim3(win,movie_Filename,size=(700,500),pos=(0,0),loop=False);   # autostart = starts the video automatically when first drawn

# Bubble OBJ
bubble = visual.ShapeStim(
win=win, name='bubble',
size=(0.1, 0.1), vertices='circle',
ori=0.0, pos=(0, 0),
lineWidth=1.0,     colorSpace='rgb',  lineColor=[0.8824, 0.9451, 1.0000], fillColor=None,
opacity=0.3, depth=2.0, interpolate=True)

# ==============================================================
# ===========                INSTRUCTIONS                    ==============
# ==============================================================
Instr_Video_T='TASK NAME: VIDEO\n\n Watch the next video attentively.\n Relax & breathe with the bubble cue.';
Instr_Video_S=visual.TextStim(win,text=Instr_Video_T,height=25,units='pix',name='intro',color='black',wrapWidth=800,pos=(0,0));

# =========================================
# SETTING GENERAL CLOCK AND LOGGING
# =========================================
clock=core.Clock();                                                         # use the core clock
logging.setDefaultClock(clock)                                                               #set logging according to core clock
logging.console.setLevel(logging.DATA)                                            #set the console to receive nearly all messages
Logger=logging.LogFile(filename,logging.DATA,'w');               # prepare above logfile to write data
#Logger=logging.LogFile(LogFileName,logging.DATA,'w');               # prepare above logfile to write data
win.setRecordFrameIntervals(True);                                                  #capture frame intervals
win.saveFrameIntervals(fileName=filename, clear=False);          #write frame intervals to LogFileName
# win.saveFrameIntervals(fileName=LogFileName, clear=False);          #write frame intervals to LogFileName

# ==================================================================
# PRINT FIRST SET OF INSTRUCTIONS AND WAIT FOR TRIGGER
# ==================================================================
Instr_Video_S.draw();win.flip();
win.logOnFlip('Instructions FRAME TIME = %s' %(win.lastFrameT),logging.DATA);
event.waitKeys(keyList=['t']);        # MUST PRESS "T" to trigger rest period!!!                                                                                                                   # Wait for Scanner Trigger.                                                                                                               # Record Scanning Start Time

clock.reset();
Exp_Start_Time=clock.getTime();

# STARTING REST BUBBLE
# =========================
t=0;
stimtimer = core.Clock();
Elapsed_Time=exp_Duration;     # time entire experiment duration

def bubble_loop():
    while stimtimer.getTime()<0:    # ????: countdown from 60s
        # allow "q" keys to quit
        for key in event.getKeys(keyList=['escape','q'], timeStamped=False):
            if key in ['escape','q']:                                                                       #could also be if key != [] or something to that effect
                win.close();
                core.quit();
        # get time from monotonic clock --> time for sine wave to traverse timepoints
        time = newtimer.getTime()
        # change the bubble size parameters --> rounding t (* 10 = ms) & displaying sine wave function (resp_pattern) across time
        bubble.size = tmp_array[round(time*10)]
        print(bubble.size)
        bubble.setAutoDraw(True)
        # update the window by frame --> to show sine wave function mvmnt
        #bubble_practice.setAutoDraw(False, log=None)
        win.update()

while t<Elapsed_Time:
    t=clock.getTime();
    for i in range(numBlocks):  # numBlocks = 9
        newtimer = core.MonotonicClock()
        stimtimer.add(60)
        tmp_array = resp_pattern[i]
        try:
            if len(tmp_array) == len(resp_pattern[i]):
                print("Matrix array currently running: ", tmp_array)
        except IndexError as idxerr:
            raise idxerr("Matrix is nonexistent or not long enough for indexing.")
            break
        if i in range(1,8):
            while t<ElapsedTime-120:
                t=clock.getTime();
                movie.setAutoDraw(True)
                bubble_loop()
        else:
            movie.setAutoDraw(False)
        bubble_loop()
    win.flip()

# get the end global clock time
win.flip(); win.logOnFlip('ExpEndTime (global clock) = %s' %(globalClock.getTime()),logging.DATA);

win.close();
core.quit();

