# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 00:51:28 2016

@author: DDmitarbeiter
"""

import scripts.mymu
reload(scripts.mymu)

from scripts.mymu import MyMu

tm = MyMu()
tm.run()