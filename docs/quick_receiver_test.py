# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 16:58:39 2016

@author: DDmitarbeiter
"""

"""Example program to demonstrate how to read string-valued markers from LSL."""

import pylsl
reload(pylsl)
import time

# first resolve a marker stream on the lab network
name = 'trigger999'
print("looking for a stream named %s" % name)
#import pdb; pdb.set_trace()
streams = pylsl.resolve_byprop("name",name, timeout=8)
#streams = pylsl.resolve_stream('name', name, timeout=8)


# create a new inlet to read from the stream
now = time.clock()
if streams:
	inlet = pylsl.StreamInlet(streams[0])
	print "created inlet, receiving triggers"
	while True:
		sample,timestamp = inlet.pull_sample(timeout=1)
		if sample:
			print("got %s at time %s" % (sample[0], timestamp))
		if time.clock() - now > 60:
			break