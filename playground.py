# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import scripts.mymu
reload(scripts.mymu)
from scripts.mymu import MyMu
import logging
from collections import OrderedDict

tm = MyMu(save_mov=False, log_level=logging.INFO, info=OrderedDict([('subjid', 'mm_'), ('session', 1), ]))
tm.rp['block_order'] = [3,2,1,4]
tm.rp['no_output'] = False
#tm.run()
with tm as t:
    t.run()

import pdb; pdb.set_trace()


clock_b.reset()
clock_b.getTime()
clock_a.getTime()



print b.getTime()
print clock_a.getTime()


import pylsl

info = pylsl.StreamInfo('my_stream43', 'Markers', 1, 0, 'string', 'my_id')

outlet = pylsl.StreamOutlet(info)