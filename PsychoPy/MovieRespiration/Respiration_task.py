# Respiration task - ONLY --> 2 runs

# 540s = TOTAL EXP TIME
#GENERATE WITH:
# ffmpeg -sameq -ss [start_seconds] -t [duration_seconds] -i [input_file] [outputfile]
from psychopy import visual,event,core,gui,logging
import random
import os,time
import numpy as np
# CHOOSE YOUR monitor
# =======================
fullScreen=False # set to true during experiments

# CREATE SCREEN
# ================
#win=visual.Window([800,600],fullscr=fullScreen,allowGUI=False,monitor='testMonitor',screen=screen_to_show,units='pix');
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

# TASK DURATIONS                                                                        TOTAL TIME = (21*5)+(39*5)+18+10.5=328.5s / 1.5 = 219 TRs (+ 4 extra)  ===> 5:34.5 min
# ===================
numBlocks=9                                              #Number of trials of resp blocks --> 9
startBufferDur=18                                        #Duration of additional fixation period immediately after scan starts
endBufferDur=10.5                                        #Duration of additional fixation period immediately following last rest block
exp_Duration=511.5;                                      # 9 * 60 = 540s - (18+10.5) = 511.5
# 540s = TOTAL EXP TIME

# SET LOG FILE NAME
# ====================
_thisDir = os.path.dirname(os.path.abspath(__file__))
fileDlg = gui.Dlg(title="Run Information");
fileDlg.addField('File Prefix: ');

fileDlg.show();
if gui.OK:      # if GUI works --> make log file & record data in it
    Dlg_Responses=fileDlg.data;
    LogFilePrefix=Dlg_Responses[0];
    LogFileName = f"{_thisDir}{os.sep}RunLogs{os.sep}{LogFilePrefix}_RespTask_%s_log.txt"
else:           # if not... --> test log
    print('User Cancelled')
    LogFileName = f"{_thisDir}{os.sep}RunLogs{os.sep}_RespTask_%s_log.txt"

# writing 34 [empty] lines in logfile
Logger=logging.LogFile(LogFileName,34,'w');

# ==============================================================================================================================
# ======================                           OBJECTS                            ===============================================================
# ==============================================================================================================================
# Rest Buffers
# rest window
#Instr_Rest_Window=visual.Rect(win,width=300,height=200,pos=(0,0),lineColor='black',lineWidth=3);
# fixation cross
xhr=visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-30,0),(30,0),(0,0),(0,30),(0,-30)),units='pix',closeShape=False,name='rest');

# Bubble OBJ
bubble_practice = visual.ShapeStim(
win=win, name='bubble_practice',
size=(0.1, 0.1), vertices='circle',
ori=0.0, pos=(0, 0),
lineWidth=1.0,     colorSpace='rgb',  lineColor=[0.8824, 0.9451, 1.0000], fillColor=None,
opacity=0.3, depth=2.0, interpolate=True)

# Resp conditions: Ampl (depth) & Freq (speed)
amplitude = [0.01,0.02,0.03];
frequency = [(1.5*np.pi*0.2),(2*np.pi*0.2),(2.5*np.pi*0.2)]; 

# ==============================================================
# ===========                INSTRUCTIONS                    ==============
# ==============================================================
Instr_Video_T='TASK NAME: RESPIRATION ONLY\n\n Relax & breathe with the bubble cue.\n';
Instr_Video_S=visual.TextStim(win,text=Instr_Video_T,height=25,units='pix',name='intro',color='black',wrapWidth=800,pos=(0,0));

# =========================================
# SETTING GENERAL CLOCK AND LOGGING
# =========================================
clock=core.Clock();                                                         # use the core clock
logging.setDefaultClock(clock)                                                               #set logging according to core clock
logging.console.setLevel(logging.DATA)                                            #set the console to receive nearly all messages
Logger=logging.LogFile(LogFileName,logging.DATA,'w');               # prepare above logfile to write data
win.setRecordFrameIntervals(True);                                                  #capture frame intervals
win.saveFrameIntervals(fileName=LogFileName, clear=False);          #write frame intervals to LogFileName

# ==================================================================
# PRINT FIRST SET OF INSTRUCTIONS AND WAIT FOR TRIGGER
# ==================================================================
Instr_Video_S.draw();win.flip();
win.logOnFlip('Instructions FRAME TIME = %s' %(win.lastFrameT),logging.DATA);
event.waitKeys(keyList=['t']);        # MUST PRESS "T" to trigger rest period!!!                                                                                                                   # Wait for Scanner Trigger.

clock.reset();
Exp_Start_Time=clock.getTime();                                                                                                                    # Record Scanning Start Time

# STARTING REST BUFFER
# =========================
xhr.draw();win.flip();
win.logOnFlip('[Starting Buffer] starts FRAME TIME = %s' %(win.lastFrameT),logging.DATA);
t=0;
Elapsed_Time=startBufferDur;
while t<Elapsed_Time:
    t=clock.getTime();
    for quit in event.getKeys(keyList=['escape','q'], timeStamped=False):
        if quit in ['escape','q']:
            win.close();
            core.quit();
win.flip();

# BUBBLE BLOCKS
# ===============
t=0;    # exp clock reset --> t gets the current [total] time of experiment so needs reset***
# Timers: stimtimer (bubble) & movie duration
stimtimer = core.Clock()        # add another (separate) timer
Elapsed_Time=Elapsed_Time+exp_Duration;      # add on movie_duration to elapsed time variable (empty)

while t<Elapsed_Time:       # while t is less than exp_Duration
    # get the current time from global clock
    t=clock.getTime();
    # show the bubble blocks
    for i in range(numBlocks):      # 7 [60s] blocks
        # monotonic clock --> for tracking time (during each block)
        newtimer = core.MonotonicClock()
        # timing stimulus drawing --> add 60s to the clock (for each 'block')
        stimtimer.add(60.0)
        # random parameters --> randomized amplitude/frequency "blocks"
        ampl = random.choice(amplitude);
        freq = random.choice(frequency);
        # sine wave function --> 300 floats, 3000 timepoints across time, scaled to 0.11
        resp_pattern = np.sin(freq*np.linspace(0,300,num=3000))*ampl+0.11
        # flip window for [new] display & log (NO LOGGING IN WHILE LOOP!)
        win.flip();win.logOnFlip('Resp {0}: FrameTime Onset = {1}, Ampl = {2}, Freq = {3}'.format(i,(win.lastFrameT),ampl,freq),logging.DATA);
        while stimtimer.getTime()<0:    # ????: countdown from 60s
            # allow "q" keys to quit
            for key in event.getKeys(keyList=['escape','q'], timeStamped=False):
                if key in ['escape','q']:                                                                       #could also be if key != [] or something to that effect
                    win.close();
                    core.quit();
            # get time from monotonic clock --> time for sine wave to traverse timepoints
            t = newtimer.getTime()
            # change the bubble size parameters --> rounding t (* 10 = ms) & displaying sine wave function (resp_pattern) across time
            bubble_practice.setSize(resp_pattern[round(t*10)], log=None)
            bubble_practice.draw()
            # update the window by frame --> to show sine wave function mvmnt
            #bubble_practice.setAutoDraw(False, log=None)
            win.update()
        # flip at [end] of while loop
        win.flip();win.logOnFlip('Resp {0}: FrameTime Ends = {1}'.format(i,(win.lastFrameT)),logging.DATA);
win.flip()      # flip window again to log end of movie
win.logOnFlip('Task: FrameTime Ends = {0}'.format(win.lastFrameT),logging.DATA);

# ENDING REST BUFFER
#=======================
Elapsed_Time=Elapsed_Time+endBufferDur                                   #Add final buffer time of rest
xhr.draw();win.flip();
win.logOnFlip('[Ending Buffer] starts FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA);
t=0;
while t<Elapsed_Time:
    t=clock.getTime();
    for quit in event.getKeys(keyList=['escape','q'], timeStamped=False):
        if quit in ['escape','q']:
            win.close();
            core.quit();

win.flip();
win.close();
core.quit();
