import random
import psychopy
import serial
import numpy
import os
from psychopy.iohub import launchHubServer
import subject
from common import *


def main():
    #if you want to trigger scanner
    info = create_user_prompt()
    
    #getting booleans for 
    trigger = info['Trigger fMRI']
    if trigger in ['yes', 'y']:
        trigger=True
    else:
        trigger=False
        
    practice = False
    if info['Practice'] == 'yes':
        practice = True
        
    
    
    #number of trials would have to be divisible by 4
    trials = 9
    stimuli=create_stimuli(trials)
    

    
def create_user_prompt():
    config_data = get_config()

    #creates user prompt
    info = {'Subject':666, 'scan_id':'?', 'Session':1, 'Trigger fMRI': 'yes','Experiment':'symbols'}

    if config_data:
        for key in config_data.keys():
            info[key] = config_data[key]

    info = infoGUI(info)
    return info

#TODO: create list of stimuli
def create_stimuli(trials):
    stimuli = []
    equals_list = generate_equal(trials)
    greater_list = generate_greater(trials)
    less_list = generate_less(trials)
    return stimuli

#generate equal
def generate_equal(trials):
    #counter
    i = 0;
    
    equals=[]
    keeping_track=[]
    
    #reflecting 50%
    while i<trials/2:
        
        #random numbers between 0-9
        temp = random.randrange(0,10)
        if len(keeping_track)<10 and temp not in keeping_track:
            keeping_track.append(temp)
            equals.append((temp,temp))
            i+=1
        if len(keeping_track)==10:
            keeping_track=[]
        
    return equals 
   

def generate_greater(trials):
    #counter 
    i=0
    
    greater = []
    keeping_track=[]
    
    #reflecting 25%
    while i<trials/4:
        #random numbers between 0-8 because nothing greater than 9
        temp = random.randrange(0,9)
        if len(keeping_track)<9 and temp not in keeping_track:
            keeping_track.append(temp)
            temp_greater = random.randrange(1,10)
            #do we want to make sure this second one isn't repeated either
            #check logic I guess
            while temp_greater<= temp:
                temp_greater = random.randrange(1,10)
            greater.append((temp,temp_greater))
            i+=1
        if len(keeping_track)==9:
            keeping_track=[]
    
    return greater
    

def generate_less(trials):
    #counter 
    i=0
    
    less = []
    keeping_track=[]
    
    #reflecting 25%
    while i<trials/4:
        #random numbers between 1-9 because nothing less than 0
        temp = random.randrange(1,10)
        if len(keeping_track)<9 and temp not in keeping_track:
            keeping_track.append(temp)
            temp_less = random.randrange(0,10)
            #do we want to make sure this second one isn't repeated either
            #check logic I guess
            while temp_less>=temp:
                temp_less = random.randrange(0,10)
            less.append((temp,temp_less))
            i+=1
        if len(keeping_track)==9:
            keeping_track=[]
    
    return less
    


main()