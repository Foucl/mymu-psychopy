# -*- coding: utf-8 -*-

# -- ==mymu_imports== --
#%% mymu_imports
import sys
sys.dont_write_bytecode = False

import numpy.random as rnd
import numpy as np
import pandas as pd

import os
import time
import glob
from collections import OrderedDict
import psychopy
import logging as dev_logging
reload(psychopy)
from psychopy import visual, data, core, event, logging
import psychopy_ext
reload(psychopy_ext)
from psychopy_ext import exp
#import logging

import pylsl

import computer
#reload(computer)
reload(exp)

from IPython.core.debugger import Tracer
dev_logging.basicConfig(level=logging.INFO)
logger = dev_logging.getLogger('my_logger')

# for testing - psychopy's moviestim doesn't seem to take care of files already opened
#import win32file
#win32file._setmaxstdio(2048)


#self.logger = logging.getLogger()

# -- ==mymu_imports== --


# -- ==mymu_class== --
#%% mymu-class

PATHS = exp.set_paths('.', computer)

PATHS['img'] = 'resources/img/'
PATHS['stim'] = os.path.join('resources', 'stimuli')
PATHS


class MyMu(exp.Experiment):

    u"""
    Willkommen zu unserem Experiment
    ================================
    
    Druecken Sie die **Leertaste**, um zu starten.
    """
    def __init__(self,
                 name='mymu',
                 version='0.1.0',
                 info=OrderedDict([('subjid', 'mm_'),
                                  ('session', 1),
                                  ]),
                 rp=OrderedDict([  # these control how the experiment is run
                ('no_output', False),  # do you want output? or just playing around?
                ('debug', True),  # not fullscreen presentation etc
                ('autorun', 0),  # if >0, will autorun at the specified speed
                ('happy_triangle_up', True),
                ('block_order', [1,2,3,4]),
                ('n_trl_valid', 21),#60
                ('n_trl_invalid', 7),#20
                ('stream_to_LSL', False),
                ('stream_name', 'mymu_dr_2')
                ]),
                 log_level = logging.WARNING,
                 save_mov = False,
                 marker_labels = None,
                 actions='run',
                 #stream_name='mymu_trigger'
                 ):
        super(MyMu, self).__init__(name=name, info=info,
                rp=rp, actions=actions,
                paths=PATHS, computer=computer, version=version, blockcol='block')
        
        #TODO: add subject ID to stream name!
        #channels = info.desc().append_child('channels')
        #for c in self.marker_labels:
            #channels.append_child("channel") \
                #.append_child_value("label", c) \
                #.append_child_value("type", 'Markers')
        
        self.save_mov = save_mov
        self.stream_name=self.rp['stream_name']
        self.log_level = log_level
        self.logger = logger  
        self.logger.level = log_level
        self.block_order = [x-1 for x in self.rp['block_order']]
        
        if marker_labels:
            self.marker_labels = marker_labels
        else:
            self.marker_labels = ['block', 'validity', 'target_em', 'event', 'trial_no', 'other']
        
        
        # TODO: more options for testing! (only one stimulus, only one condition ...)
        # TODO: add the two other blocks
        # TODO: add instructions
        # TODO: add practice
        # TODO: add state, strategy and other questions
        # TODO: add other input (demographic info etc.)

        # user-defined parameters
        self.n_trl = {'valid': self.rp['n_trl_valid'], 'invalid': self.rp['n_trl_invalid']}
        self.n_trl_pract = {'valid': 6, 'invalid': 2} # just use half of that for the short practice?
        # should scr_fac always get a longer instruction?
        
        # self.prop_valid = .75 # allow choice: ninvalid or prop_invalid
        # self.ninvalid = int((1-self.prop_valid)*self.nvalid)
        
        # the following should not be user defined - move to create_exp_plan? make_trials?
        # I think everythin in __init__() will be exposed to the user by the psychopy_ext.gui?
        # TODO: -> think about what should stay here
        
        #self.n_trials = self.nvalid + self.ninvalid
        
        self.stimsize = (5, 6)  # in deg
        self.isi = 1.2 # make use of that?
        self.iti = 1.5
        
        

        
        factors = OrderedDict({'stim_type': ['em_fac', 'nem_fac_e', 'nem_fac_f', 'scr_fac'], \
                                   'expression': [['ekl', 'fre'], ['neu', 'ekl'], \
                                                  ['neu', 'fre'], ['ekl', 'fre']], \
                                    'validity': ['valid', 'invalid']})
        
        for factor in factors.keys():
            if not factor == 'validity':
                l = factors[factor]
                if factor == 'stim_type':
                    l = [str(n) + '_' + l[i] for n, i in enumerate(self.block_order)]
                factors[factor] = l

        self.factors = factors
        #import pdb; pdb.set_trace()
        
        
        # TODO: decouple expression from file-finding (for scrambled/triangles!)
        # TODO: block order as run-time option
        
        # construct four blocks
        self.my_blocks = [(key, []) for key in self.factors['stim_type']]
        self.my_blocks = OrderedDict(self.my_blocks)
        blocks = self.factors['stim_type']
        
        bl_no = 0
        for block in blocks:
            #import pdb; pdb.set_trace()
            expr = self.factors['expression'][bl_no]
            self.my_blocks[block] = OrderedDict([
                ('expressions', expr),
                ('conditions', [
                        OrderedDict({'texpr':expr[0], 'validity': 'valid', 'pexpr': expr[0], 'weight': self.n_trl['valid']}),
                        OrderedDict({'texpr':expr[0], 'validity': 'invalid', 'pexpr': expr[1], 'weight': self.n_trl['invalid']}),
                        OrderedDict({'texpr':expr[1], 'validity': 'valid', 'pexpr': expr[1], 'weight': self.n_trl['valid']}),
                        OrderedDict({'texpr':expr[1], 'validity': 'invalid', 'pexpr': expr[0], 'weight': self.n_trl['invalid']})
                               ])
                ])
            bl_no += 1
                
        #import pdb; pdb.set_trace()
        
        
        # the following needs to changed so that stimulus type can be parametrized
        test_dir = os.path.join(self.paths['stim'], 'ekl')
        self.all_stims =  [x for x in os.listdir(test_dir)]
        self.test_dir = test_dir
        
        male = [x for x in self.all_stims if x.split('_')[1] == 'm']
        female = [x for x in self.all_stims if x.split('_')[1] == 'w']
        # happy = [x for x in self.all_stims if x[0:3] == 'fre']
        # disgusted = [x for x in self.all_stims if x[0:3] == 'ekl']
        
        
        self.ids = {}
        
        self.ids['male'] = list(set([x[4:8] for x in male]))
        self.ids['female'] = list(set([x[4:8] for x in female]))

        #import pdb; pdb.set_trace()
        self.setup_lsl() 
        
    def __enter__(self):
        return self # for contextmanager 'with thismu as tm:'
								
    def __exit__(self, exception_type, exception_val, trace):
        try:
            self.win.close()
        except:
            pass
        print exception_type, exception_val
	
    def __del__(self):
	   super(MyMu,self).__del__()
	   try:
	       self.win.close()
	   except:
		  pass
		
    def create_stimuli(self):
        """Define your stimuli here, store them in self.s
        """
        
        testmov = os.path.join(self.test_dir, 'ekl_m_03.mp4') # b/c we can't initialize a MovieStim without a file
        self.testmov = testmov
        #self.set_logging(level=self.log_level
        self.all_movie_frames = []
        
        # --- Stimuli
        self.create_fixation(size=.3)
        self.s = {}
        self.s['fix']= self.fixation
        self.s['mov'] = visual.MovieStim3(self.win, filename=testmov, name='PrimeVid', noAudio=True, autoLog=True, size=(612,920)) #(511, 768) )
        self.s['blank'] = visual.ImageStim(self.win, size=(0,0), autoLog=True)
        self.s['target'] = visual.ImageStim(self.win, size=self.stimsize, name='TargetPic', autoLog=True)

        
        self.win.setRecordFrameIntervals(False)
        #self.win.waitBlanking = False
    
    def create_win(self, *args, **kwargs):
        super(MyMu, self).create_win(units='deg', colorSpace = 'rgb255', color=[100]*3,
                                      *args, **kwargs)
        
    def before_exp(self, *args, **kwargs):
        #self.setup_lsl()
        super(MyMu, self).before_exp(*args, **kwargs)
    
    def set_logging(self, *args, **kwargs):
        super(MyMu, self).set_logging(level=self.log_level, *args, **kwargs)
        
        
    def before_block(self, *args, **kwargs):
        super(MyMu, self).before_block(text=None, auto=0, wait=0.5, wait_stim=None)
        self.gen_and_push_marker('block_start')
        #self.fixation.draw(self.win)
        #event.waitKeys()
        
        
    def make_trials(self, block):
        # self.n_trl = {'valid': 60, 'invalid': 20}
        
        this_block = self.my_blocks[block]        
        this_trl_list = []
        ids = self.ids
        trial_ids = {'valid': [], 'invalid': []}
        
        if self.rp['happy_triangle_up']:
            self.triangle_mapping = {'fre': 'fre_scr_up', 'ekl': 'ekl_scr_down'}
        else:
            self.triangle_mapping = {'fre': 'fre_scr_down', 'ekl': 'ekl_scr_up'}
        
        
                           
        # 1. Fill up ids for valid and invalid conditions:
        for con in self.n_trl:
            for sex in ids:
                n_avail = len(ids[sex])
                n_target = self.n_trl[con] / 2
                if n_target <= n_avail:
                    trial_ids[con].extend(list(rnd.choice(ids[sex], n_target, False)))
                else:
                    diff = n_target - n_avail
                    trial_ids[con].extend(ids[sex] + list(rnd.choice(ids[sex], diff, True)))
         
        #for expr in this_block['expressions']:
            
    
        for c in this_block['conditions']:
            trgl = None
            if 'scr_fac' in block:
                basedir = self.triangle_mapping[c['pexpr']]
                trgl = basedir.split('_')[-1]
                #import pdb; pdb.set_trace()
            else:
                basedir = c['pexpr']
            idtmp = trial_ids[c['validity']]
            stimftmp = [basedir + '/' + c['pexpr'][0:3] + '_' + x + '.mp4' for x in idtmp]
            i = 0
            for stim in stimftmp:
                this_trl_list.extend([OrderedDict({'block': block, 'texpr': c['texpr'][0:3], 'validity': c['validity'], \
                'pexpr': c['pexpr'][0:3],'stimf': stim, 'sex': idtmp[i].split('_')[0], 'id': idtmp[i], 'trgl': trgl})])
                i += 1
        
        return this_trl_list
        
    def save_frame(self, n_rep=None, buffer='front', name=None):
        if not name:
            name = self.this_event.name
        if not n_rep:
            n_rep = int(self.this_event.dur * 30)
        if n_rep < 1:
            n_rep = 1
        im = self.win._getFrame(buffer)
        self.all_movie_frames.append((n_rep, im, name))
    
    # overwrite at least idle_event for movie-creation
    def before_event(self, *args, **kwargs):
        if self.event_no == 0:
            sys.stdout.write('\rtrial %s\r\n' % (self.thisTrialN+1))
            #sys.stdout.write('\r\n')
            sys.stdout.flush()
            pass
        if not self.this_event.name == 'prime':
            super(MyMu, self).before_event(*args, **kwargs)
        if self.this_event.name in ['prime', 'target']:
            self.gen_and_push_marker()
        if self.save_mov:
            #self.win.getMovieFrame(buffer='front')
            self.save_frame()
    
            
    def post_trial(self, *args, **kwargs):
        self.this_trial['real_dur'] = self.trial_clock.getTime()
        super(MyMu, self).post_trial(*args, **kwargs)
        
        if self.save_mov and self.thisTrialN == 2:
            self.save_movie_frames()
            self.quit(message='movie of first three trials saved, nothing to do anymore')
   
    def save_movie_frames(self, filen='./exp_t1-7.mp4'):
        frames = self.all_movie_frames
        # seems super easy, copied from psychopy.visual.Window.saveMovieFrames
        from moviepy.editor import ImageSequenceClip
        numpyFrames = []

        # TODO: drop the whole n_rep stuff - maybe even use native psychopy save function?
        # TODO: then: keep number of saved trials to a minimum (maybe three: 2 val, 1 inval)
        # TODO: give more control of trial_list, for this, for testing and for instruction/practice!!
        for n_rep, frame, name in frames: # BUT: now I have to bite the dust and create many frames? can this be done more efficiently?
            print "saving", name, n_rep, "times"
            for _ in xrange(n_rep):
                numpyFrames.append(np.array(frame))
        clip = ImageSequenceClip(numpyFrames, fps=30)
        clip.write_videofile(filen, codec='libx264')
        self.all_movie_frames = []

    def setup_lsl(self):
        if not self.rp['stream_to_LSL']:
            return
        marker_len = len(self.marker_labels)
        info = pylsl.StreamInfo(self.stream_name, 'Markers', marker_len, 0, 'string', self.info['subjid'])
        #info = pylsl.StreamInfo(self.stream_name, 'Markers', 6, 0, 'string', 'myuidw43536')
        #TODO: add subject ID to stream name!
        channels = info.desc().append_child('channels')
        for c in self.marker_labels:
            channels.append_child("channel") \
                .append_child_value("label", c) \
                .append_child_value("type", 'Markers')
                
        self.outlet = pylsl.StreamOutlet(info)
        self.logger.info('created outlet %s with name %s', self.outlet, self.stream_name)
       
    def gen_and_push_marker(self, text=None):
        if not self.rp['stream_to_LSL']:
            return
        target_len = len(self.marker_labels)
        try:
            tt = self.this_trial
            tn = self.thisTrialN
            if not text:
                text = self.this_event.name
                # TODO: read self
            marker_l = [tt['block'], tt['texpr'], tt['validity'], text, tn]
        except AttributeError:
            tbn = self.this_blockn
            tb = self.blocks[tbn][0][0][self.blockcol]
            marker_l = [tb, '', '', text, '', '']

        if len(marker_l) < target_len:
            marker_l.extend([''] * (target_len - len(marker_l)))
        elif len(marker_l) > target_len:
            raise Exception('to many elements in the marker list!')
            
        self.this_marker_l = [str(x) for x in marker_l]
        #self.logger.level = 10
        self.logger.debug('sent marker %s', self.this_marker_l)
        self.outlet.push_sample(self.this_marker_l)


    def play_mov(self, *args, **kwargs):
        self.before_event()
        ut = self.rp['unittest'] or self.rp['autorun']
        #ap = self.rp['autorun']
        save = self.save_mov

        mov = self.s['mov']
        i = 1
        while(mov.status != visual.FINISHED):
            if mov.getCurrentFrameTime() >= 0.9:
                mov.stop()
                break
            mov.draw()
            self.win.flip()
            self.last_keypress()
        return
        
        
        
        while(mov.status != visual.FINISHED and mov.status!= visual.STOPPED):
            ft = mov.getCurrentFrameTime()
            if i == 3: # we are somewhere during the neutral part of the video
                if ut:
                    mov.seek(13/30.)
                    mov._videoClock.reset(mov._videoClock.getTime())
                if save:
                    self.save_frame(n_rep=12, buffer='front', name='prime_neutral')
            elif (ft > 12/30. and ft < 18/30.) and save and i%2 == 0:
                self.save_frame(n_rep=1, buffer='front', name='prime_movement')
            elif ft > 19/30.:
                if ut:
                    mov.stop()
                    break
            mov.draw()
            self.win.flip()
            self.last_keypress()
            i += 1
        if save:
            self.save_frame(n_rep=12, buffer='front', name='prime_apex')
        self.logger.debug("mov flipped %s times", i)
        return None
            

    def create_trial(self):
        """Define trial composition
        """
        self.trial = [exp.Event(self,
                                name='fix',
                                dur=.400,  # in seconds
                                display=self.s['fix'],
                                func=self.idle_event),
                      exp.Event(self,
                                dur=1, # 1s - controlled by video length
                                name='prime',
                                display=self.s['mov'], # just get the 'stimf' from the trialhandler/exp_plan/conditions?
                                func=self.play_mov),
                               
                     exp.Event(self,
                                name='isi',
                                dur=self.isi,
                                display=self.s['blank'],
                                func=self.idle_event),
                     exp.Event(self,
                                name='target',
                                dur=1.300,
                                display=self.s['target'],
                                #draw_stim=False,
                                func=self.target_event), # override idle_event for trigger sending (and data receiving??)
                      exp.Event(self,
                                name='iti',
                                dur=self.iti,
                                display=self.s['blank'],
                                func=self.idle_event)] 
                                
    def target_event(self, *args, **kwargs):
        self.before_event() # draws the target stimulus
        # start the listener and extract time and amplitude of maxima
        # listener should be similar to self.wait() and return those two properties
        
        
        #print marker_str
        #super(MyMu, self).idle_event(*args, **kwargs) # maybe completely drop the parent method?
        # call 
        event_keys = self.wait()
        return event_keys
                  
    def create_exp_plan(self):
        """Put together trials
        DURATION??
        check image files here; randomize here
        """
        exp_plan = []
        

        for block in self.my_blocks:
            
            trials = self.make_trials(block)      
            
            i = 1
            for trl in trials:
                exp_plan.append(OrderedDict([
                            ('block', block),
                            ('trialno', i),
                            ('texpr', trl['texpr']), # is this how that should be done? (trl could be generated by make_trials above)
                            ('validity', trl['validity']),
                            ('pexpr', trl['pexpr']),
                            ('stimf', trl['stimf']),
                            ('sex', trl['sex']),
                            ('id', trl['id']),
                            ('trgl', trl['trgl']),
                            ('onset', ''),  # empty ones will be filled up
                            ('dur', ''),    # during runtime
                            ('real_dur', ''),
                            ('corr_resp', ''),
                            ('subj_resp', ''),
                            ('accuracy', ''),
                            ('rt', ''),
                            ]))
                i += 1
         
       
        self.exp_plan = exp_plan
        #import pdb; pdb.set_trace()
        
        
    def before_trial(self):
        """Set up stimuli prior to a trial
        """
        tt = self.this_trial
        #print abc
        
        #par_dir = os.path.join(self.paths['stim'], self)
        vid_fname = os.path.join(self.paths["stim"], tt['stimf'])
        self.s['mov'].setMovie(vid_fname)
        self.s['target'].setImage(os.path.join(self.paths['img'], tt['validity'] + '_ArialBlack_740.png'))
    
        self.gen_and_push_marker('trl_beg')
        #image='./img/invalid_ArialBlack_740.png',
        # with textstim: self.s['target'].text = self.this_trial['validity']
        # or if-else
        # but check for pyglet memory leak, imagestim might still be better!
        
        
class _exp(exp.Task):
    # should take the block as argument?
    pass
        
class _pract(_exp):
    # inherit from _exp, just with different settings?
    # -> how to keep track of trials here?
    # make option: long vs short practice (first vs other blocks)
    # also handle instruction presentation here
    pass

    

#thismu = MyMu(rp={'no_output': False, 'unittest': True, 'debug': True, 'autorun': 0, 'happy_triangle_up': True, 
 #                'block_order': [4,3,2,1], 'stream_to_LSL': True,'stream_name': 'trigger'}, log_level=logging.DEBUG,
  #                  save_mov=False, marker_labels = None)    							        
# -- ==mymu_class== --


# -- ==mymu_run_thismu== --
# %%
#with thismu as tm:
 #   tm.run()

# -- ==mymu_run_thismu== --


# %% ui test