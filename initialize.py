#initialize.py

"""
Initiates an fMRI data collection day.
Provides 1-time creation of subject ID, session #, and stimulus # vars
"""

import sys
import pickle
import time
from psychopy import gui
import os

today = time.strftime('%y-%m-%d')

scan_id = '%s.?_3T3' % today

info = {'Subject': 666, 'scan_id':scan_id, 'stimulus_id':1}
order = info.keys()

GUI = gui.Dlg(title='Initialize Longitudinal Followup')
GUI.SetSize([1000, 1000])

for key in info.keys():
    GUI.addField(key,info[key])

GUI.show()

if GUI.OK:
    info = {}
    for key, value in zip(order, GUI.data):
        info[key] = value
else:
    abort = gui.Dlg(title = 'Quitting...')
    abort.addText('Initialization Aborted by User')
    abort.show()
    raise Exception("Initialization Aborted by User")

f = open("config.pck", 'w')
pickle.dump(info, f)
f.close()

#create subject dir in behavioral data directory
data_dir = os.path.join('data', info['scan_id'])

if not os.path.exists(data_dir):
    os.mkdir(data_dir)

print "INITIALIZED SESSION WITH FOLLOWING PARAMETERS"
print info