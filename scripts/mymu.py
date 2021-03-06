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
import threading
import Queue
import copy
#import logging

import pylsl

from ThreadingSkeleton import ThreadingSkeleton

import computer
#reload(computer)
reload(exp)

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
    
    Drücken Sie die **Leertaste**, um zu starten.
    """
    def __init__(self,
                 name='mymu',
                 version='0.1.0',
                 info=OrderedDict([('subjid', 'mm_'),
                                  ('session', 1),
                                  ]),
                 rp=OrderedDict([  # these control how the experiment is run
                ('no_output', False),  # do you want output? or just playing around?
                ('unittest', False),
                ('debug', True),  # not fullscreen presentation etc
                ('autorun', 0),  # if >0, will autorun at the specified speed
                ('happy_triangle_up', True),
                ('block_order', [1,2,3,4]),
                ('n_trl_block', 12),
                ('prop_valid', 0.75),
                ('stream_to_LSL', True),
                ('stream_name', 'mymu_dr_9991')
                ]),
                 log_level = logging.DEBUG,
                 save_mov = False,
                 marker_labels = None,
                 actions='run',
                 unittest = False, # I want to be able to set some stuff withoug passing the whole dict
                 #stream_name='mymu_trigger'
                 ):
        #print "MyMu.__init__() called"
        #import pdb; pdb.set_trace()
                  
        if unittest:
            rp['unittest'] = True
                     
        super(MyMu, self).__init__(name=name, info=info, rp=rp, actions=actions,
                paths=PATHS, computer=computer, version=version, blockcol='block')
        
        #print "exp.Exp.__init__() called)"
        
        
        # strip unicodes from docstring if doing a unittest:
        
        if self.rp['unittest']:
            docstring = self.__doc__
            docstring =  ''.join([i if ord(i) < 128 else ' ' for i in docstring])
            setattr(self, '__doc__', docstring)
        
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
        
        # should scr_fac always get a longer instruction?
        
        
        
        # the following should not be user defined - move to create_exp_plan? make_trials?
        # I think everythin in __init__() will be exposed to the user by the psychopy_ext.gui?
        # TODO: -> think about what should stay here
        
        #self.n_trials = self.nvalid + self.ninvalid
        
        self.target_size = (5, 6)  # in deg
        self.mov_size =  (508, 768) #(612,920)
        self.isi = 1.2 # make use of that?
        self.iti = 1.5
        self.setup_lsl()
        self.to_keep = dir(self)
        self.to_keep.append('to_keep')
        
                        
    def delete_everything(self, keep):
        for var in dir(self):
            if not (var.startswith('_') or var in keep):
                delattr(self, var)
        
         
        
    def __enter__(self):
        return self # for contextmanager 'with thismu as tm:'
								
    def __exit__(self, exception_type, exception_val, trace):
        try:
            self.win.close()
        except:
            pass
        try:
            self.outlet.__del__()
        except:
            pass
        print exception_type, exception_val

    def order_blocks(self):
        block_map = {'stim_type': ['em_fac', 'nem_fac_e', 'nem_fac_f', 'scr_fac'], \
                                   'expression': [['ekl', 'fre'], ['neu', 'ekl'], \
                                                  ['neu', 'fre'], ['ekl', 'fre']]}

        for factor in block_map.keys():
            l = block_map[factor]
            l = [l[i-1] for i in self.rp['block_order']]
            if factor == 'stim_type':
                l = [str(i) + '_' + l[i] for i in range(len(l))]
            block_map[factor] = l

        self.my_blocks = [(key, []) for key in block_map['stim_type']]
        self.my_blocks = OrderedDict(self.my_blocks)
        blocks = block_map['stim_type']
        self.calculate_trial_number()
  
        for bl_no, block in enumerate(blocks):
            #import pdb; pdb.set_trace()
            expr = block_map['expression'][bl_no]
            self.my_blocks[block] = OrderedDict([
                ('expressions', expr),
                ('conditions', [
                        OrderedDict({'texpr':expr[0], 'validity': 'valid', 'pexpr': expr[0], 'weight': self.n_trl['valid']}),
                        OrderedDict({'texpr':expr[0], 'validity': 'invalid', 'pexpr': expr[1], 'weight': self.n_trl['invalid']}),
                        OrderedDict({'texpr':expr[1], 'validity': 'valid', 'pexpr': expr[1], 'weight': self.n_trl['valid']}),
                        OrderedDict({'texpr':expr[1], 'validity': 'invalid', 'pexpr': expr[0], 'weight': self.n_trl['invalid']})
                               ])
                ])
           
        
    def calculate_trial_number(self):
        #('n_trl_block', 80),
        #('prop_valid', 0.75),
        
        prop_valid = self.rp['prop_valid'] # .75 # allow choice: ninvalid or prop_invalid
        n_total = self.rp['n_trl_block']
        n_valid = int(prop_valid*n_total)
        n_invalid = n_total - n_valid
        # self.ninvalid = int((1-self.prop_valid)*self.nvalid)
        self.n_trl = {'valid': n_valid, 'invalid': n_invalid}
		
    def create_stimuli(self):
        """Define your stimuli here, store them in self.s
        """
        
        test_dir = os.path.join(self.paths['stim'], 'ekl')
        all_stims =  [x for x in os.listdir(test_dir)]

        male = [x for x in all_stims if x.split('_')[1] == 'm']
        female = [x for x in all_stims if x.split('_')[1] == 'w']
        self.ids = {}
        
        self.ids['male'] = list(set([x[4:8] for x in male]))
        self.ids['female'] = list(set([x[4:8] for x in female]))
        
        testmov = os.path.join(test_dir, 'ekl_m_03.mp4') # b/c we can't initialize a MovieStim without a file
        self.testmov = testmov
        #self.set_logging(level=self.log_level)
        self.all_movie_frames = []
        
        # --- Stimuli
        self.create_fixation(size=.3)
        self.s = {}
        self.s['fix']= self.fixation
        self.s['mov'] = visual.MovieStim3(self.win, filename=testmov, name='PrimeVid',
                            noAudio=True, autoLog=True, size=self.mov_size)#(612,920)) #(511, 768) )
        self.s['blank'] = visual.ImageStim(self.win, size=(0,0), autoLog=True)
        self.s['target'] = visual.ImageStim(self.win, size=self.target_size, name='TargetPic', autoLog=True)

        
        self.win.setRecordFrameIntervals(False)
        #self.win.waitBlanking = False
    
    def create_win(self, *args, **kwargs):
        super(MyMu, self).create_win(units='deg', colorSpace = 'rgb255', color=[100]*3,
                                      *args, **kwargs)
               
    def run(self):
        self.delete_everything(self.to_keep)
        
        #self
        try:
            self.outlet.__del__()
        except:
            pass
        super(MyMu, self).run()
        
    def before_exp(self, *args, **kwargs):
        #self.setup_blocks()
        
        super(MyMu, self).before_exp(*args, **kwargs)
        
        
    def setup(self):
        self.order_blocks()
        super(MyMu, self).setup()
        #import pdb; pdb.set_trace()
        
        
    def setup_task(self):
        #import pdb; pdb.set_trace()
        super(MyMu, self).setup_task()
        
        
    
    def set_logging(self, *args, **kwargs):
        super(MyMu, self).set_logging(level=self.log_level, *args, **kwargs)
    
        
    def last_keypress(self, *args, **kwargs):
        keys = super(MyMu, self).last_keypress(*args, **kwargs)
        if 'p' in keys:
            try:
                tg, tt, te = self.play_or_pause('pause')
            except Exception as e:
                logger.info('exception raised when trying to pause clock', e)
            event.waitKeys()
            try:
                self.play_or_pause('play', (tg, tt, te))
            except Exception as e:
                logger.info('exception raised when trying to continue clock', e)
        #self.all_keys = []
        for key in keys:
            if not self._check_if_in_keylist(key, self.keylist_flat):
                key.remove(key)
        return keys
        
    
    def play_or_pause(self, action, stime=(0,0)):
        if action=='pause':
            logging.info('paused during trial')
            tg = self.glob_clock.getTime()
            tt = self.trial_clock.getTime()
            te = self.event_clock.getTime()
            return tg, tt, te
        else:
            logging.info('continued after pause')
            self.glob_clock.reset(-stime[0])
            self.trial_clock.reset(-stime[1])
            self.event_clock.reset(-stime[2])
        
        
        
        
    def before_block(self, *args, **kwargs):
        self.real_clock = core.Clock()
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
                    
        # 2. generate a trial_list with filenames
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
        tt = self.this_trial
        tn = self.thisTrialN
        te = self.this_event
        if self.event_no == 0:
            txt = '\rtrial %s: %s (%s)\r\n' % (tn+1, tt['pexpr'], tt['validity'])
            sys.stdout.write(txt)
            sys.stdout.flush()
        if not te.name == 'prime':
            super(MyMu, self).before_event(*args, **kwargs)
        if te.name in ['prime', 'target']:
            self.gen_and_push_marker()
        if self.save_mov:
            #self.win.getMovieFrame(buffer='front')
            self.save_frame()
    
            
    def post_trial(self, *args, **kwargs):
        self.this_trial['real_dur'] = self.real_clock.getTime()  
        self.this_trial['subj_resp'] = ''
        self.this_trial['rt'] = ''
        
        if self.save_mov and self.thisTrialN == 6:
            self.save_movie_frames()
            #self.quit(message='movie of first three trials saved, nothing to do anymore')
            self.win.close()
   
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
        #import pdb; pdb.set_trace()
        marker_len = len(self.marker_labels)
        self.sender = MarkerSender(self.stream_name, self.info['subjid'], self.marker_labels)
        self.sender.start()
        return
        info = pylsl.StreamInfo(self.stream_name, 'Markers', marker_len, 0, 'string', self.info['subjid'])
        #info = pylsl.StreamInfo(self.stream_name, 'Markers', 6, 0, 'string', 'myuidw43536')
        #TODO: add subject ID to stream name!
        #channels = info.desc().append_child('channels')
        #for c in self.marker_labels:
            #channels.append_child("channel") \
                #.append_child_value("label", c) \
                #.append_child_value("type", 'Markers')
        info = pylsl.StreamInfo('my_stream33', 'Markers', 6, 0, 'string', 'my_id')

        self.outlet = pylsl.StreamOutlet(info)       
        #self.outlet = pylsl.StreamOutlet(info)
        #self.logger.info('created outlet %s with name %s', self.outlet, self.stream_name)
       
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
        self.sender.cmd_q.put(self.this_marker_l)
        #self.outlet.push_sample(self.this_marker_l)


    def play_mov(self, *args, **kwargs):
        self.before_event()
        ut = self.rp['unittest'] or self.rp['autorun']
        #ap = self.rp['autorun']
        save = self.save_mov

        mov = self.s['mov']
        i = 1
        #while(mov.status != visual.FINISHED):
            #if mov.getCurrentFrameTime() >= 0.9:
             #   mov.stop()
              #  break
            #mov.draw()
            #self.win.flip()
            #self.last_keypress()
        #return

        while(mov.status != visual.FINISHED and mov.status!= visual.STOPPED):
            if mov.getCurrentFrameTime() >= 0.96:
                mov.stop()
                break
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
                                func=self.idle_event), # override idle_event for trigger sending (and data receiving??)
                      exp.Event(self,
                                name='iti',
                                dur=self.iti,
                                display=self.s['blank'],
                                func=self.idle_event)] 
                                
    def target_event(self, *args, **kwargs):
        return super(MyMu, self).idle_event(*args, **kwargs) # maybe completely drop the parent method?
        #self.before_event() # draws the target stimulus
        # start the listener and extract time and amplitude of maxima
        # listener should be similar to self.wait() and return those two properties
        #print marker_str
        # call 
        #event_keys = self.wait()
        #return event_keys
                  
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
        self.real_clock.reset()
        #image='./img/invalid_ArialBlack_740.png',
        # with textstim: self.s['target'].text = self.this_trial['validity']
        # or if-else
        # but check for pyglet memory leak, imagestim might still be better!
        

class MarkerSender(ThreadingSkeleton):
    
    def __init__(self, stream_name='sn', stream_id='sid', marker_labels=['one']):
        super(MarkerSender, self).__init__(name='marker-sender-class')
        self.stream_name = stream_name
        self.stream_id = stream_id
        self.marker_labels = marker_labels
        self.outlet = None
        
    def setup_lsl(self):
        #import pdb; pdb.set_trace()
        marker_len = len(self.marker_labels)
        info = pylsl.StreamInfo(self.stream_name, 'Markers', marker_len, 0, 'string', self.stream_id)#self.info['subjid'])
        #info = pylsl.StreamInfo(self.stream_name, 'Markers', 6, 0, 'string', 'myuidw43536')
        #TODO: add subject ID to stream name!
        channels = info.desc().append_child('channels')
        for c in self.marker_labels:
            channels.append_child("channel") \
                .append_child_value("label", c) \
                .append_child_value("type", 'Markers')
        #info = pylsl.StreamInfo('my_stream33', 'Markers', 6, 0, 'string', 'my_id')

        self.outlet = pylsl.StreamOutlet(info)       
        logger.info('created outlet %s with name %s', self.outlet, self.stream_name)
        
    def run(self):
        logger.setLevel(logging.INFO)
        logger.info('Starting MarkerSender Thread')
        if not self.outlet:
            self.setup_lsl()
        marker = ['']
        while self.alive.is_set():
            try:
                marker = self.cmd_q.get(True, 0.1)
                self.outlet.push_sample(marker)
            except Queue.Empty as e:
                continue
            except Exception as e:
                logger.warning("Couldn't push the marker %s, Error: %s", marker, e)
            
        


        
class _Exp(exp.Task):
    # should take the block as argument?
    
    pass
        
class _Pract(_Exp): 
    
    def __init__(self, parent,
                 name='MyMu_Practice',
                 version='0.01',
                 method='sequential',
                 data_fname=None,
                 blockcol='block'):
        #datafile = copy.copy(parent.datafile)
        #datafile.writeable = False
    
        super(_Pract, self).__init__(parent, name, version, method, data_fname, blockcol)
        self.datafile = copy.copy(parent.datafile)
        self.datafile.writeable=False
# no, just roll your own run_exp/run_block methods!
    # inherit from _exp, just with different settings?
    # -> how to keep track of trials here?
    # make option: long vs short practice (first vs other blocks)
    # also handle instruction presentation here

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