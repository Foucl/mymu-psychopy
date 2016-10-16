#!/usr/bin/env python

"""
Computer configuration file
===========================

Specify default settings for all computers where you run your experiment such
as a monitor size or root path to storing data. This is intended as a more
portable and extended version of PsychoPy's MonitorCenter.

A computer is recognized by its mac address which is dependent on its
hardware and by its name. In the future versions of psychopy_ext,
if anything in the hardware changes, you'll see a warning.

# TODO: split computer configuration and defaults possibly by moving to a
config file

"""

import uuid, platform

recognized = True
# computer defaults
root = '.'  # means store output files here
stereo = False  # not like in Psychopy; this merely creates two Windows
default_keys = {'exit': ('lshift', 'escape'),  # key combination to exit
                'trigger': 'space'}  # hit to start the experiment

valid_responses = {'f': 0, 'j': 1, 'e': 99}  # organized as input value: output value, 'e' is used in KeyError-Workaround

# monitor defaults
distance = 51
width = 52
# window defaults
screen = 0  # default screen is 0
view_scale = (1, 1)

# Get computer properties
# Computer is recognized by its mac address
mac = uuid.getnode()
system = platform.uname()[0]
name = platform.uname()[1]

if mac == "3417EBCB518F" and system == 'Windows':  # Dev computer, Windows booted
    distance = 51
    width = 52 # Dell U2412M, 24inch diag, 16:10 (1920x1200)
    root = '../data/'

elif mac == 145320949993177:  # Lab computer
    distance = 127
    width = 60
    view_scale = [1,-1]  # top-bottom inverted
    default_keys['trigger'] = 5
    valid_responses = {'9': 0, '8': 1, '7': 2, '6': 3}

else:
    recognized = False
