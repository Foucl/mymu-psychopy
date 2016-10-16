# -*- coding: utf-8 -*-

# -- ==mymu_imports== --
#%% mymu-imports
import sys
sys.dont_write_bytecode = False

import numpy.random as rnd
import numpy as np
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets

import os
import glob
from collections import OrderedDict
import psychopy
reload(psychopy)
from psychopy import visual, data, core, event, logging
import psychopy_ext
reload(psychopy_ext)
from psychopy_ext import exp
from pyglet import app



import scripts.computer as computer
#reload(computer)
reload(exp)

from IPython.core.debugger import Tracer
# for testing - psychopy's moviestim doesn't seem to take care of files already opened
#import win32file
#win32file._setmaxstdio(2048)

# -- ==mymu_imports== --




# -- ==mymu_class== --
#%%

PATHS = exp.set_paths('mymu', computer)
PATHS['vid'] = './vid/'
PATHS['img'] = './img/'

try:
    del(thismu)
    del(MyMu)
except:
    pass

class MyMu(exp.Experiment):

    """
    Willkommen zu unserem Experiment
    ================================

    Drücken Sie eine **beliebige Taste**, um zu starten.
    """
    def __init__(self,
                 name='mymu',
                 version='0.9',
                 info=OrderedDict([('subjid', 'mm_'),
                                  ('session', 1),
                                  ]),
                 rp=OrderedDict([  # these control how the experiment is run
                ('no_output', False),  # do you want output? or just playing around?
                ('debug', False),  # not fullscreen presentation etc
                ('autorun', 0),  # if >0, will autorun at the specified speed
                ('log_level', 40)
                ]),
                 actions='run'
                 ):
        super(MyMu, self).__init__(name=name, info=info,
                rp=rp, actions=actions,
                paths=PATHS, computer=computer, version=version)#, blockcol='block')

        # user-defined parameters
        self.nvalid = 60
        self.ninvalid = 20
        self.stimsize = (9, 6)  # in deg
        self.isi = 1.2
        ids = {} 
        
        self.out_movie_frames = []
        
        self.all_stims =  [x for x in os.listdir(self.paths["vid"])]
        
        male = [x for x in self.all_stims if x[5] == 'm']
        female = [x for x in self.all_stims if x[5] == 'w']
        happy = [x for x in self.all_stims if x[0:3] == 'fre']
        disgusted = [x for x in self.all_stims if x[0:3] == 'ekl']
        
        
        self.ids = {}
        
        self.ids['male'] = list(set([x[5:8] for x in male]))
        self.ids['female'] = list(set([x[5:8] for x in female]))

        self.factors = {'expression': ['disgusted', 'happy'], 'validity': ['valid', 'invalid']}
        self.conditions=[
            OrderedDict({'texpr':'ekl', 'validity': 'valid', 'pexpr': 'ekl', 'weight': self.nvalid}),
            OrderedDict({'texpr':'ekl', 'validity': 'invalid', 'pexpr': 'fre', 'weight': self.ninvalid}),
            OrderedDict({'texpr':'fre', 'validity': 'valid', 'pexpr': 'fre', 'weight': self.nvalid}),
            OrderedDict({'texpr':'fre', 'validity': 'invalid', 'pexpr': 'ekl', 'weight': self.ninvalid})
            ]
                

    def create_stimuli(self):
        """Define your stimuli here, store them in self.s
        """
        testmov = os.path.join(self.paths["vid"], 'ekl99m03.avi')
        self.set_logging(level=self.rp['log_level'])
        self.all_movie_frames = []
        
        
        self.all_mov = {}
        
        for stim in self.all_stims:
            if self.rp['dict']:
                mov = visual.MovieStim3(self.win, filename=os.path.join(self.paths["vid"], stim), size=(511, 768), name='PrimeVid', noAudio=True, autoLog=True)
            else:
                mov = ''
            self.all_mov[stim] = mov
        
        self.create_fixation()
        self.s = {}
        self.s['fix']= self.fixation
        self.s['mov'] = visual.MovieStim3(self.win, filename=testmov, size=(511, 768), name='PrimeVid', noAudio=True, autoLog=True)
        self.s['blank'] = visual.ImageStim(self.win, size=(0,0), autoLog=True)
        self.s['target'] = visual.ImageStim(self.win, size=self.stimsize, name='TargetPic', autoLog=True)
        
        self.win.setRecordFrameIntervals(False)
        #self.win.waitBlanking = False
    
    def create_win(self, *args, **kwargs):
        super(MyMu, self).create_win(units='deg', color=(100,100,100),
                                      *args, **kwargs)
        #app.run()
        
        
    def make_trials(self):
        self.trial_list = []
        ids = self.ids
    
        for c in self.conditions:
            # TODO: make it possible to just set nTrials and propValid!! TDD!
            idtmp = []
            stimftmp = []
            if c['validity'] == 'valid':
                idtmp = ids['male'][:] + list(rnd.choice(ids['male'], 10)) +                         idtmp + ids['female'][:] + list(rnd.choice(ids['female'], 11))
                stimftmp = [c['pexpr'] + '99' + x + '.avi' for x in idtmp]
            elif c['validity'] == 'invalid':
                idtmp = list(rnd.choice(ids['male'], 10)) + list(rnd.choice(ids['male'], 10))
                stimftmp = [c['pexpr'] + '99' + x + '.avi' for x in idtmp]

            for stim in stimftmp:
                self.trial_list.extend([OrderedDict({'texpr': c['texpr'], 'validity': c['validity'], 'pexpr': c['pexpr'],                                    'stimf': stim, 'mov':self.all_mov[stim], 'sex': stim[3], 'id': stim[4:6]})])
            #rnd.shuffle(self.trial_list) not necessary, psychopy_ext takes care of shuffling!
        #return trial_list
        
    def save_frame(self, n_rep=None, buffer='front', name=None):
        # TODO: only check for save_movie here
        if not name:
            name = self.this_event.name
        if not n_rep:
            n_rep = int(self.this_event.dur * 30)
        if n_rep < 1:
            nrep = 1
        im = self.win._getFrame(buffer)
        self.all_movie_frames.append((n_rep, im, name))
    
    # overwrite at leaste idle_event for movie-creation
    def before_event(self, *args, **kwargs):
        super(MyMu, self).before_event(*args, **kwargs)
        if self.rp['save_mov'] :
            #self.win.getMovieFrame(buffer='front')
            self.save_frame()
    
            
    def post_trial(self, *args, **kwargs):
        super(MyMu, self).post_trial(*args, **kwargs)
        if self.rp['save_mov'] and self.thisTrialN == 2:
            #self.win.saveMovieFrames('./exp_run_t1-7.mp4') # TODO: create custom function
            self.save_movie_frames()
            #for frame in self.all_movie_frames:
               # print frame[0], frame[1], frame[2]
            self.quit(message='movie of first three trials saved, nothing to do anymore')
   
    def save_movie_frames(self, filen='./exp_t1-7.mp4'):
        frames = self.all_movie_frames
        # seems super easy, copied from psychopy.visual.Window.saveMovieFrames
        from moviepy.editor import ImageSequenceClip
        numpyFrames = []
        n = 0
        i = 0
        for n_rep, frame, name in frames: # BUT: now I have to bite the dust and create many frames? can this be done more efficiently?
            if name == 'prime_rest':
                n += 1
            elif name == 'isi':
                print "saving prime_rest", n, "times"
                n = 0
                print "saving isi", n_rep, "times"
            else:
                print "saving", name, n_rep, "times"
            for _ in xrange(n_rep):
                numpyFrames.append(np.array(frame))
        clip = ImageSequenceClip(numpyFrames, fps=30)
        clip.write_videofile(filen, codec='libx264')
        self.all_movie_frames = []
       
    def play_simple(self, *args, **kwargs):
        
        n_rep_first = 22
        ut = self.rp['unittest']
        if ut:
            n_rep_first = 2
        show_ft = False
               
        self.s['mov'].draw()
        # save a lot of memory by just saving the backbuffer with n_rep = n_rep_first/2!
        self.save_frame(n_rep=(n_rep_first+2)/2,buffer='back', name='prime_neutral')
        self.s['mov'].seek(0.0)
        self.s['mov'].pause()
        
        save = self.rp['save_mov']
        # TODO: add way to quit using exitkey
        i = 0
        print "\n"
        while (self.s['mov'].status != visual.FINISHED):
            if i == n_rep_first:
                self.s['mov'].play()
                self.s['mov'].seek((1/30.))
                self.s['mov']._videoClock.reset(self.s['mov']._videoClock.getTime())
            self.s['mov'].draw()
            t = self.s['mov'].getCurrentFrameTime()
            self.win.flip()
            if save and i > n_rep_first and i%2 == 0:
                self.save_frame(n_rep=1, buffer='front', name='prime_rest')
                self.s['mov'].seek(t + (1/30.))
                self.s['mov']._videoClock.reset(self.s['mov']._videoClock.getTime())
                print "the frametime at flip", i, "was", t
                #print "======="
            i += 1
            key = self.last_keypress()
        print "new supersimple loop flipped", i, "times"
        return
            
        
        n_neut = 1
        for i in xrange(n_rep_first):  
            self.s['mov'].draw()
            if i == 0:
                beg = self.trial_clock.getTime()
            if (i+3)%2==0 and show_ft:
                ft = self.s['mov'].getCurrentFrameTime() + (1/30.)
                ft_ms = ft * 1000
                frame_no = round(ft * 30)
                text = "frametime: %6.2fms \nframe: %d\niteration/flip/frame refresh: %d\ntotal iteration: %d\n_nextFrameT=%6.2f, _videoClock=%6.2f" %                     (ft_ms, frame_no,i+1, n_neut, self.s['mov']._nextFrameT, self.s['mov']._videoClock.getTime())
                #ts = visual.TextStim(self.win, text=text, pos=(0,-5.5))
                #ts.draw()
            self.win.flip()
            if (i+3)%2==0 and show_ft and False:
                if 'escape' in event.waitKeys():
                    self.quit()
            n_neut += 1
            
        self.s['mov'].play()
        
        self.s['mov']._videoClock.reset()
        for i in xrange(2):
            self.s['mov'].draw()
            ft = self.s['mov'].getCurrentFrameTime() + (1/30.)
            ft_ms = ft * 1000
            frame_no = round(ft * 30)
            text = "frametime: %6.2fms \nframe: %d\niteration/flip/frame refresh: %d\ntotal iteration: %d\n_nextFrameT=%6.2f, _videoClock=%6.2f" %                     (ft_ms, frame_no,i+1, n_neut, self.s['mov']._nextFrameT, self.s['mov']._videoClock.getTime())
            #ts = visual.TextStim(self.win, text=text, pos=(0,-5.5))
            #ts.draw()
            self.win.flip()
            if show_ft and False:
                if 'escape' in event.waitKeys():
                    self.quit()
            n_neut += 1
            
            
        end_neut = self.trial_clock.getTime()
        print "neutral phase (21 refreshes, 10 frames) took", end_neut-beg, "s"
        a = self.s['mov'].getCurrentFrameTime()
        print "frametime before entering movement-loop is", a
        self.s['mov'].seek(0.0)
        
        
        i = 0
        j = 0
        
        #Tracer()()
        #self.s['mov']._videoClock.reset()
        while (self.s['mov'].status != visual.FINISHED):
            self.s['mov'].draw()
            if (i+3)%1==0 and show_ft:
                ft = self.s['mov'].getCurrentFrameTime() + (1/30.)
                ft_ms = ft * 1000
                frame_no = round(ft * 30)
                text = "frametime: %6.2fms \nframe: %d\niteration/flip/frame refresh: %d\ntotal iteration: %d\n_nextFrameT=%6.2f, _videoClock=%6.2f" %                     (ft_ms, frame_no,i+1, n_neut, self.s['mov']._nextFrameT, self.s['mov']._videoClock.getTime())
                #ts = visual.TextStim(self.win, text=text, pos=(0,-5.5))
                #ts.draw()
            self.win.flip()
            if (i+3)%1==0 and show_ft:
                if 'escape' in event.waitKeys():
                    self.quit()
            #self.win.flip()
            if save and (i+2)%2==0:
                t_pre = self.s['mov']._videoClock.getTime()
                self.save_frame(n_rep=1, buffer='front', name='prime_rest')
                self.s['mov'].seek((1/30. * (i/2) + (1/30.)))
                self.s['mov']._videoClock.reset(self.s['mov']._videoClock.getTime())
                t_post = self.s['mov']._videoClock.getTime()
                print "in iteration", i
                print "video Clock after seek:", t_post
                print "frametime after seek", self.s['mov'].getCurrentFrameTime()
                print "netframet after seek", self.s['mov']._nextFrameT
                print "============="
                # print round((t_post - t_pre)*1000, 3)
                #print "nextFrameT for i=", i, "should be", round(self.s['mov']._nextFrameT * 1000, 3)
                #print "time after reset:", self.s['mov']._videoClock.getTime()
                #Tracer()()
            if ut and i > 4:
                self.s['mov'].stop()
                return
            i += 1
            n_neut += 1
        print " last run of loop went for", i, "iterations (was: 20, should be: 40!)"
        print " total flips: ", n_neut
        # finished, should I replay the final frame a couple of times to get to 1s?
        end = self.trial_clock.getTime()
        print ", duration of movie", end-beg
        self.s['mov'].stop()
        #

    def create_trial(self):
        """Define trial composition
        """
        self.trial = [exp.Event(self,
                                name='fix',
                                dur=3,  # in seconds
                                display=self.s['fix'],
                                func=self.idle_event),
                      #exp.Event(self,
                                #dur=1,
                                #name='prime',
                                #display=self.s['mov'], # just get the 'stimf' from the trialhandler/exp_plan/conditions?
                                #func=self.play_simple),
                               
                     exp.Event(self,
                                name='isi',
                                dur=3,
                                display=self.s['blank'],
                                func=self.idle_event),
                     exp.Event(self,
                                name='target',
                                dur=1.300,
                                display=self.s['target'],
                                #draw_stim=False,
                                func=self.idle_event),
                      exp.Event(self,
                                name='iti',
                                dur=1.5,
                                display=self.s['blank'],
                                func=self.idle_event)]
                  
    def create_exp_plan(self):
        """Put together trials
        DURATION??
        check image files here; randomize here
        """
        
        self.make_trials()
        
        trials = self.trial_list
                
        exp_plan = []
        i = 1
        for trl in trials:
            exp_plan.append(OrderedDict([
                        ('block', 'emo_fac'),
                        ('trialno', i),
                        ('texpr', trl['texpr']), # is this how that should be done? (trl could be generated by make_trials above)
                        ('validity', trl['validity']),
                        ('pexpr', trl['pexpr']),
                        ('stimf', trl['stimf']),
                        ('mov', trl['mov']),
                        ('sex', trl['sex']),
                        ('id', trl['id']),
                        ('onset', ''),  # empty ones will be filled up
                        ('dur', ''),    # during runtime
                        ('corr_resp', ''),
                        ('subj_resp', ''),
                        ('accuracy', ''),
                        ('rt', ''),
                        ]))
            i += 1
        self.exp_plan = exp_plan
        
        
    def before_trial(self):
        """Set up stimuli prior to a trial
        """
        
        if self.rp['dict']:
            self.s['mov'] = self.this_trial['mov']
        else:
            vid_fname = os.path.join(self.paths["vid"], self.this_trial['stimf'])
            self.s['mov'].setMovie(vid_fname)
        self.s['target'].setImage(os.path.join(self.paths['img'], self.this_trial['validity'] + '_grey.png'))
        
        

thismu = MyMu(rp={'no_output':True, 'debug':True, 'dict': False, 'autorun': 0,                   'log_level': logging.WARNING, 'unittest': False, 'save_mov':False})


#del MyMu # should take care of opened files?

# -- ==mymu_class== --


# -- ==mymu_run_thismu== --
# %%
thismu.run()

# -- ==mymu_run_thismu== --