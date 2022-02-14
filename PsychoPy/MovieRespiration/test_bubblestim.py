# Matched breathing pattern? --> exact same?
# Rest --> bubble stimulus (9 min)

# gradually varying respiration cues --> get respiration values from ECG.1D file (Neurokit2) & vary peaks

import psychopy
from psychopy import visual, core, event
import random
import numpy as np
import os
# add pygame as external module to PsychoPy (download copy of package for Python2.7, unzip package in a folder, add that folder to the Psychopy path
# psychoPy preferences/general --> modify preference for paths to a list of strings (['/path1','/path2'])
# these will get added to the Python path (when you import PsychoPy in your script) --> no need to 'import pygame'
# import pygame

# create a window (same as experiment window) --> ideally transparent window (opacity=0)
win = visual.Window(
    size=[800,600], fullscr=False, screen=0, 
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height', depthBits=24)

### STIMULI ###

# movie
movie_Filename='/Users/holnessmn/Desktop/Tasks_OHBM2022/FishBoy_Movie/spring-blender-open-movie.mp4';
movie=visual.MovieStim3(win,movie_Filename,size=(700,500),pos=(0,0),loop=False);   # autostart = starts the video automatically when first drawn
movie_Duration=420;     # 7 min
Rest=60;                # 1 min

# bubble
bubble = visual.ShapeStim(
    win=win,name='bubble stimulus',
    size=(0.1, 0.1),vertices='circle',
    ori=0.0,pos=(0, 0),lineWidth=1.0,
    colorSpace='rgb',lineColor=[0.8824, 0.9451, 1.0000],
    fillColor=None,opacity=0.3,interpolate=True)

# rest block
xhr=visual.ShapeStim(win,lineColor='#000000',lineWidth=3.0,vertices=((-30,0),(30,0),(0,0),(0,30),(0,-30)),units='pix',closeShape=False,name='rest');

# global clock
timer = core.Clock()

# 0.5 sec breath
# 1.0 sec breath
# 1.5 sec breath
# 2.0 sec breath

# matrix_change = time --> at this time, change the size
# matrix_vals =  .1D values (peaks) --> make simple Neurokit resp file (30s long) (locally) & modify peaks to your liking 
    # copy file values to make the simulation more "natural"
    # for i in resp file....do this --> (obj_size = i)

# draw() specific command --> psychopy

# inhale    # 0.0001(size_increase) * num_frames = 0.3 (max_size)
# nice slow increase rate (by frame)
# slow breath

# numpy array of sine floats (like .1D file)
# +4 = high enough so NO NEGATIVE NUMBERS (visShapeStim.size = no negs)    
#shape = (ampl * np.sin(freq*t) + 4) * 0.025        # 0.1 / 4 = 0.025 (scaling factor)

#for i in range(numBlocks):

# choose random parameters (speed = freq / depth = ampl)
amplitude = [0.01,0.02,0.03];
frequency = [(1.5*np.pi*0.2),(2*np.pi*0.2),(2.5*np.pi*0.2)];    
# 5 min (300s) timecourse: sine wave of 3000 vals long, round(t/100) --> tenth --> idx

# for each block condition
ampl = random.choice(amplitude);
freq = random.choice(frequency);

# sine wave pattern
# 2*np.pi*0.2 = freq * np.linspace(0,300,num=3000) = time, ampl = 0.05
# resp pattern of 3000 timepoints
resp_pattern = np.sin(freq*np.linspace(0,300,num=3000))*ampl+0.11

while timer.getTime()<movie_Duration:
    movie.setAutoDraw(True)
    for key in event.getKeys(keyList=['escape','q'], timeStamped=False):
        if key in ['escape','q']:                                                                       #could also be if key != [] or something to that effect
            win.close();
            core.quit();
    for i in range(1,8):
        newtimer = core.MonotonicClock()
        timer.add(60.0)
        tmp_array = resp_pattern
        while timer.getTime() < 0:  # duration of 60s
            # get the time from the monotonic clock
            t = newtimer.getTime();
            bubble.size = tmp_array[round(t*10)]
            bubble.setAutoDraw(True)
            # update the window after every draw
            win.update()
    win.flip()
timer.reset()
    

