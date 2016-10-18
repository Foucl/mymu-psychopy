# -*- coding: utf-8 -*-


# -- ==ThreadingSkeleton== --

import threading
import Queue
import logging.config
#import yaml

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

# -- ==ThreadingSkeleton== --