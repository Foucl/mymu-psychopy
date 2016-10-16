# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 16:11:30 2016

@author: DDmitarbeiter
"""

# pandas does not come by default with PsychoPy but that should not prevent
# people from running the experiment
# %%


#from pylsl import StreamInfo, StreamOutlet
import time
import random
import pylsl

# some modules are only available in Python 2.6



class LslTest(object):
    
    def __init__(self, stream_name='triggers'):
        self.stream_name = stream_name  
        print("created outlet with stream_name", self.stream_name)
        self.info = pylsl.StreamInfo(self.stream_name, 'Markers', 1, 0, 'float32', 'myuidw43536')
        self.outlet = pylsl.StreamOutlet(self.info)
        
    def send_triggers(self):
        markernames = [3]
        begin = time.clock()
        #time.sleep(60)
        while True:
            self.outlet.push_sample([random.choice(markernames)])
            time.sleep(random.random()*3)
            if time.clock() - begin >= 20:
                return


o = LslTest('triggers17')
#%%

from collections import OrderedDict
from psychopy import visual, event
from psychopy_ext import exp

import scripts.computer as computer
PATHS = exp.set_paths('trivial', computer)

class Exp1(exp.Experiment):
    """
    Instructions (in reST format)
    =============================

    **Hit 'j'** to advance to the next trial, *Left-Shift + Esc* to exit.
    """
    def __init__(self,
                 name='exp',
                 info=OrderedDict([('subjid', 'quick_'),
                                  ('session', 1),
                                  ]),
                 rp=OrderedDict([  # these control how the experiment is run
                ('no_output', True),  # do you want output? or just playing around?
                ('debug', True),  # not fullscreen presentation etc
                ('autorun', 0),  # if >0, will autorun at the specified speed
                ]),
                 actions='run', stream_name='triggers3'
                 ):
        super(Exp1, self).__init__(name=name, info=info,
                rp=rp, actions=actions,
                paths=PATHS, computer=computer)
        self.stream_name = stream_name

        # user-defined parameters
        self.ntrials = 8
        self.stimsize = 2  # in deg
        self.info = StreamInfo(stream_name, 'Markers', 1, 0, 'string', 'myuidw43536')
        self.outlet = StreamOutlet(self.info)
        print("created outlet with stream_name", self.stream_name)
        
            

    def create_stimuli(self):
        """Define your stimuli here, store them in self.s
        """
        self.create_fixation()
        self.s = {}
        self.s['fix']= self.fixation
        self.s['stim'] = visual.GratingStim(self.win, mask='gauss',
                                            size=self.stimsize)
        markernames = ['Test', 'Blah', 'Marker', 'XXX', 'Testtest', 'Test-1-2-3']
        while True:
            self.outlet.push_sample([random.choice(markernames)])
            key = event.waitKeys(maxWait=random.random()*3)
            if key:
                break

    def create_trial(self):
        """Define trial composition
        """
        self.trial = [exp.Event(self,
                                dur=.200,  # in seconds
                                display=[self.s['stim'], self.s['fix']],
                                func=self.idle_event),
                      exp.Event(self,
                                dur=0,
                                display=self.s['fix'],
                                func=self.wait_until_response)
                     ]

    def create_exp_plan(self):
        """Put together trials
        """
        exp_plan = []
        for trialno in range(self.ntrials):
            exp_plan.append(OrderedDict([
                        ('trialno', trialno),
                        ('onset', ''),  # empty ones will be filled up
                        ('dur', ''),    # during runtime
                        ('corr_resp', 1),
                        ('subj_resp', ''),
                        ('accuracy', ''),
                        ('rt', ''),
                        ]))
        self.exp_plan = exp_plan




#%%
import random

from psychopy import visual, event  # import some libraries from PsychoPy
from pylsl import StreamInfo, StreamOutlet

#create a window
mywin = visual.Window([800,600], monitor="testMonitor", units="deg")

#create some stimuli
grating = visual.GratingStim(win=mywin, mask="circle", size=3, pos=[-4,0], sf=3)
fixation = visual.GratingStim(win=mywin, size=0.5, pos=[0,0], sf=0, rgb=-1)

#draw the stimuli and update the window
grating.draw()
fixation.draw()
mywin.update()

stream_name = 'triggers'
info = StreamInfo(stream_name, 'Markers', 1, 0, 'string', 'myuidw43536')
outlet = StreamOutlet(info)
print("now sending markers...")
markernames = ['Test', 'Blah', 'Marker', 'XXX', 'Testtest', 'Test-1-2-3']
while True:
    outlet.push_sample([random.choice(markernames)])
    key = event.waitKeys(maxWait=random.random()*3)
    if key:
        break
    
mywin.close()

#%%

import random
import time

from pylsl import StreamInfo, StreamOutlet

# first create a new stream info (here we set the name to MyMarkerStream,
# the content-type to Markers, 1 channel, irregular sampling rate,
# and string-valued data) The last value would be the locally unique
# identifier for the stream as far as available, e.g.
# program-scriptname-subjectnumber (you could also omit it but interrupted
# connections wouldn't auto-recover). The important part is that the
# content-type is set to 'Markers', because then other programs will know how
#  to interpret the content
info = StreamInfo('trigger999', 'Markers', 1, 0, 'string', 'myuidw43536')

# next make an outlet
outlet = StreamOutlet(info)

print("now sending markers...")
markernames = ['Test', 'Blah', 'Marker', 'XXX', 'Testtest', 'Test-1-2-3']
while True:
    # pick a sample to send an wait for a bit
    outlet.push_sample([random.choice(markernames)])
    time.sleep(random.random()*3)