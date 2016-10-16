# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 20:18:12 2016

@author: DDmitarbeiter
"""
# %%

# imports
import sys
import os
import time
import pylsl
import threading
import Queue
import logging

import numpy.random as rnd
import numpy as np
import pandas as pd

from IPython.core.debugger import Tracer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#from FACET_LSL import *

class ThreadingSkeleton(object):
    """
    Simple Skeleton for creating a Threading class that does not inherit from threading.Threat,
    so the threads created here can be restarted.
    Implements a Command Queue (cmd_q) - if a reply_q is needed, it will have to be overwritten
    Has some features like an alive event flag
    Implemented Methods: start(), join(), restart()
    Methods needed to be implemented by the Child: run()
    also stores the success of messages in self.last_cmd and exceptions in self.last_exc
    """
    
    def __init__(self, cmd_q=Queue.Queue(), name = 'ThreadingSkeleton', thread = threading.Thread()): # <- can be overwritten by using super(ChildClassName, self).__init__(name='XY')
        self.thread = thread
        self.thread.target = self.run
        self.thread.name = name
        self.cmd_q = cmd_q
        self.alive = threading.Event()
        self.alive.set()
        self.name = name
        self.last_cmd = None
        self.last_exc = None
        
    def run(self):
        pass
    
    def start(self, restart=False):
        if not self.thread.isAlive():
            #self.join()
            self.thread = threading.Thread(target=self.run, name = self.name)
            self.alive.set()
            self.thread.start()
        else:
            if restart:
                self.restart()
            else:
                logger.info('Thread is running, doing nothing')
    
    def join(self, timeout=None):
        try:
            self.alive.clear()
            threading.Thread.join(self.thread, timeout)
            logger.info('Successfully stopped Thread %s', self.thread.name)
            self.last_cmd = True
            #self._handle_CLOSE()
        except Exception as e:
            logger.warning('Error while trying to join: %s', e)
            self.last_cmd = False
            self.last_exc = e
        self.alive.clear()
        
    def restart(self):
        if self.thread.is_alive():
            self.join()
            while self.thread.isAlive():
                pass
            self.start()
        else:
            self.start()
            
    def toggle(self):
        if self.thread.isAlive():
            self.join()
        else:
            self.start()
            
# %% 


class MarkerGenerator(ThreadingSkeleton):
    """ Threading Class that sends a marker every x seconds into LSL
    """
    def __init__(self, send_event = threading.Event(), stop_event=threading.Event(), name='marker-gen-class', stream_name = 'halledi',
                 marker_labels = None, interval=4, marker_list = None):
        super(MarkerGenerator, self).__init__(name=name)
        self.stop_event = stop_event
        self.marker_labels = marker_labels or ['block', 'validity', 'target_em', 'event', 'trial_no', 'other']
        self.marker_list = marker_list or ['em_fac', 'valid', 'disgusted', 'trial_start', '23', 'dg_up']
        self.marker_list_b = ['em_scrambled_', 'valid', 'disgusted', 'prime', '23', 'dg_up']
        self.send_event = send_event
        self.interval = interval
        self.stream_name = stream_name
    
    def setup_lsl(self, marker_labels):
        marker_len = len(marker_labels)
        self.info = pylsl.StreamInfo(self.stream_name, 'Markers', marker_len, 0, 'string', 'myid')
        channels = self.info.desc().append_child('channels')
        for c in self.marker_labels:
            channels.append_child("channel") \
                .append_child_value("label", c) \
                .append_child_value("type", "Markers")
        self.outlet = pylsl.StreamOutlet(self.info)
        logger.info('created outlet %s', self.outlet)
        
    def run(self):
        self.counter = 0
        logger.info('MarkerGenerator Thread')
        self.setup_lsl(self.marker_labels)
        while self.alive.is_set():
            if not self.stop_event.wait(self.interval):
                self.send()
            else:
                self.alive.clear()
        
    def send(self):
        logger.debug('sending trigger now')
        self.counter += 1
        if self.counter % 3 == 0:
            mlist = self.marker_list
        else:
            mlist = self.marker_list_b
        self.send_event.set()
        self.outlet.push_sample(mlist)
        self.send_event.clear()        
    
    def cancel(self):
        self.stop_event.set()
        
#self.outlet.push_sample(marker_str)

# %%
        

logger.setLevel(logging.INFO)
t = MarkerGenerator(stream_name = 'la')
t.start()

#%%
stream_l = pylsl.resolve_byprop("name",'ladidudelda', timeout=8)
