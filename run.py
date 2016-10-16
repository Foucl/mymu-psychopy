# -*- coding: utf-8 -*-

from psychopy_ext import ui

__author__ = "Christopher Dannheim"
__version__ = "0.1"
__name__ = 'test'
exp_choices = [
    ui.Choices('scripts.mymu', name='Mymu', alias='mymu'),
    ]

# bring up the graphic user interface or interpret command line inputs
# usually you can skip the size parameter
ui.Control(exp_choices, title='Demo Project', size=(560,550))

