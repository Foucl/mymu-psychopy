"""
Response Priming Experiment with Emotional Facial Expressions as Stimuli and Response.

This demo is part of psychopy_ext library.
"""

try:
    import pandas
except:
    pass

from psychopy import visual
from psychopy_ext import exp

# some modules are only available in Python 2.6
try:
    from collections import OrderedDict
except:
    from exp import OrderedDict


import computer
PATHS = exp.set_paths('mymu', computer)

class MyMu(exp.Experiment):
    """
    Willkommen zu unserem Experiment
    ================================

    Druecken Sie eine **beliebige Taste**, um zu starten.
    """
    def __init__(self,
                 name='mymu',
                 info=OrderedDict([('subjid', 'mm_'),
                                  ('session', 1),
                                  ]),
                 rp=None,
                 actions='run'
                 ):
        super(MyMu, self).__init__(name=name, info=info,
                rp=rp, actions=actions,
                paths=PATHS, computer=computer)

        # user-defined parameters
        self.ntrials = 8
        self.stimsize = 2  # in deg

    def create_stimuli(self):
        """Define your stimuli here, store them in self.s
        """
        self.create_fixation()
        self.s = {}
        self.s['fix']= self.fixation
        self.s['stim'] = visual.GratingStim(self.win, mask='gauss',
                                            size=self.stimsize)

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
		
if __name__ == "__main__":
    MyMu(rp={'no_output':True, 'debug':True}).run()