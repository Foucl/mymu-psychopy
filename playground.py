# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import scripts.mymu
reload(scripts.mymu)
from scripts.mymu import MyMu

tm = MyMu(save_mov=True)
tm.rp['block_order'] = [3,2,1,4]

with tm as t:
    t.run()



for factor in factors.keys():
            if not factor == 'validity':
                l = factors[factor]
                if factor == 'stim_type':
                    l = [str(n) + '_' + l[i] for n, i in enumerate(block_order)]
                else:
                    l = [l[i] for i in block_order]
                factors[factor] = l