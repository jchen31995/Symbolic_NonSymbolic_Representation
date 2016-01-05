import os
import random # for stimuli generating
import psychopy
from psychopy import core, visual, event, gui, parallel
import subject # for user prompt
import shuffler # for shuffling stimuli list
from common import * #for window size and all that good stuff

from psychopy.iohub import launchHubServer
import serial


#LEFT TO DO: Appending [1st_Stim, Jitter, 2nd_Stim, RT, Fixation_Jitter] to Excel and exporting data to Excel
#            Setting up SR Box
#            Generating Dot Stimulus png's
#            Adjusting Stimulus Size

def main():
    
    #if you want to trigger scanner
    info = create_user_prompt()
    
    
    #getting conditions
    trigger = info['Trigger fMRI']
    if trigger in ['yes', 'y']:
        trigger=True
    else:
        trigger=False
        
    practice = False
    if info['Practice'] == 'yes':
        practice = True
    """
    # start the iohub server and get the keyboard and PST box devices
    io = launchHubServer(**iohub_config)
    kb = io.devices.keyboard
    srbox = io.devices.serial

    # initializes data collection for PST box and keyboard
    kb.enableEventReporting(True)
    srbox.enableEventReporting(True)

    # Source: https://psychtoolbox-3.googlecode.com/svn/beta/Psychtoolbox/PsychHardware/CMUBox.m
    print('Switching response box to streaming mode and switching on lamp #3...')
    srbox.write(chr(numpy.uint8(128+32+64+4)))
    core.wait(0.25)
    print('...done.')
    
    #serial adapter
    if trigger:
        ser = serial.Serial(port=7)
        ser.write(chr(numpy.uint8(128+32+64+1))) 
    """
    
    #TODO: work out some of the finer details of figuring the numbers out, but I think have most of it
    #number of trials has to be divisible by 80
    num_trials = 12
    if not num_trials%4==0:
        print "Number of trials has to be divisible by 4 to ensure 50%-25%-25% ratio is preserved"
        exit()
    
    trials = 80
    #if for some reason you want more than 80 trials (not recommended -- takes much longer to run, also need to ease up on repeats)
    if num_trials>trials:
        temp = num_trials/80
        trials = trials + 80*(num_trials/80)
    repeats = 3
    
    keeping_track=[]
    #create stimuli, jitters
    stimuli=create_stimuli(num_trials,trials,repeats)
    first_jitter = generate_jitter(1.5,5.5,num_trials, repeats)
    fixation_jitter = generate_jitter(1.9,8.4,num_trials,repeats)
    for i in range(0,num_trials):
        keeping_track.append(i)
    
    
    
    
    
    
    
    ###CREATE WINDOW
    #win = visual.Window(size=screen_size, units='pix', fullscr=True, rgb = background_color)
    win = visual.Window(size=screen_size, units='pix', rgb = background_color)
    win.setRecordFrameIntervals(True)
    win.setMouseVisible(False)
    mouse = event.Mouse(visible=False, newPos=None, win=win)
    
    ###CREATE STIMULI
    onscr_stim = visual.TextStim(win, "", height =text_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    fixation_cross = visual.TextStim(win, "+", height = text_height, pos=[0,0], color=text_color, font='Courier New', bold=True)

    #instructions the patient will see
    msg = Message(win, color=text_color, height=text_height)
    msg.send("You are about to see two stimuli.\n\nThe second stimuli will either be greater than, less than, or equal to the first one.\n\nIf the stimuli are equal, press the button with your pointer finger.  If the stimuli are not, press the button with your middle finger.", wait=True)
    msg.send("Get Ready...", wait=False)
    quit = event.waitKeys(keyList = ['q','escape','space'])
    if quit[0] == 'escape' or quit[0]=='q':
        exit()
        
    ###CREATE SUBJECT
    datadir = ""
    sub = subject.Subject(info['Subject'], info['Session'], experiment="symbolic", dataDir=datadir)
    sub.addStatic('scan_id', info['scan_id'])
    
    #initializing clocks and variables
    clock = core.Clock()
    clock.reset()
    trial_clock = core.Clock()
    trial_clock.reset()
    
    #iterating through every stimuli
    for trial_no in keeping_track:
        #io.clearEvents('serial')
        #event.clearEvents()
        
        #First Stimulus
        #sub.inputData(trial_no, 'First Stimulus', stimuli[trial_no][1])
        onscr_stim.setText(stimuli[trial_no][0])
        while trial_clock.getTime()<.5:
            onscr_stim.draw()
            win.flip()
        trial_clock.reset()
        
        #Blank or fixation cross during jitter?
        onscr_stim.setText("")
        while trial_clock.getTime()<first_jitter[trial_no]:
            onscr_stim.draw()
            win.flip()
        trial_clock.reset()
        
        #Second Stimulus
        onscr_stim.setText(stimuli[trial_no][1])
        while trial_clock.getTime()<.5:
            onscr_stim.draw()
            win.flip()
        trial_clock.reset()
        
        #TODO: blank screen for 2500 msec ==2.5 sec or until subject responds
        #Yeah, this is the SRbox code for it
        """
        while trial_clock.getTime()<2.5:
                #while loop keeps going until we get input
            key = srbox.getEvents()
            quit = kb.getEvents()
            press_time = clock.getTime()
            if key:
                press_time = clock.getTime()
                RT = press_time - start_time
                key = key[0].current_byte
                break
            if quit:
                if quit[0].key=='q' or quit[0].key=='escape':
                    exit()
                
            
            while trial_clock.getTime()<fixation_jitter[trial_no]:
                fixation_cross.draw()
                win.flip()
        """
        
def create_user_prompt():
    config_data = get_config()

    #creates user prompt
    info = {'Subject':666, 'scan_id':'?', 'Session':1, 'Trigger fMRI': 'yes','Experiment':'symbols'}

    if config_data:
        for key in config_data.keys():
            info[key] = config_data[key]

    info = infoGUI(info)
    return info

#Right now we get 80 stimuli minimum, but what if we wanted fewer/more? How do we preserve the 50%-25%-25% and 50-50 symbols/nonsymbols ratios?
#Only requirement really should be that it's divisible by 4, not 80
#I think my logic makes sense... maybe someone can check?
#TODO: create list of stimuli
def create_stimuli(num_trials,trials,repeats):
    list1=['same','same','greater','less']
    list2=[0,1,2,3,4,5,6,7,8,9]
    list3=['symbolic','nonsymbolic']


    same_or_diff = shuffler.Condition(list1, "samediff", repeats)
    integer = shuffler.Condition(list2, "integer", repeats)
    format = shuffler.Condition(list3, "format", repeats)
    stimList = shuffler.MultiShuffler([same_or_diff,integer,format], trials).shuffle()
    
    
    
    samedifflist=[]
    numlist=[]
    formatlist=[]
    same = 0
    greaterthan = 0
    lessthan = 0
    for stim in stimList:
        same_diff = getattr(stim, "samediff")
        num = getattr(stim, "integer")
        format = getattr(stim, "format")
        if same_diff=='same':
            same+=1
            if not same>num_trials/2:
                samedifflist.append(same_diff)
                numlist.append(num)
                formatlist.append(format)
        
        if same_diff=='greater':
            greaterthan+=1
            if not greaterthan>num_trials/4:
                samedifflist.append(same_diff)
                numlist.append(num)
                formatlist.append(format)
                
        
        if same_diff=='less':
            lessthan+=1
            if not lessthan>num_trials/4:
                samedifflist.append(same_diff)
                numlist.append(num)
                formatlist.append(format)
        

    #stimuli is a list of tuples where (first stimulus, second stimulus)
    stimuli=[]
    #png placeholders == png file paths
    for condition, stim, type in zip(samedifflist,numlist,formatlist):
        #equal number of dots
        if condition=='same' and type =='symbolic':
            #generate dots where both equal
            stimuli.append(("png","png"))
        #equal numbers
        if condition=='same' and type =='nonsymbolic':
            stimuli.append(["%s" % stim,"%s"% stim])


        #greater
        if condition=='greater' and type =='symbolic':
            #generate dots where 2nd stimulus greater
            stimuli.append(("png","greaterthan_png"))
        #2nd stimulus greater than 1st
        if condition=='greater' and type =='nonsymbolic':
            if stim ==9:
                stim = random.randrange(0,9)
                
            temp = random.randrange(stim+1,10)

            #if for some reason if it doesnt work
            if not temp>stim:
                print ("Second stimulus was not greater than first stimulus")
                exit()
            stimuli.append(("%s" % stim, "%s" % temp))


        #less
        if condition=='less' and type=='symbolic':
            stimuli.append(("png","lessthan_png"))
        #2nd stimulus less than 1st
        if condition=='less' and type =='nonsymbolic':
            if stim==0:
                stim = random.randrange(1,10)
                
            temp = random.randrange (0,stim)
            
            
            #if for some reason if it doesnt work
            if not temp<stim:
                print ("Second stimulus was not less than first stimulus")
                exit()


            stimuli.append(("%s" % stim, "%s" % temp))
    return stimuli
    
def generate_jitter(min_duration,max_duration,num_trials, repeats):
    list1=[.0,.1,.2,.3,.4,.5,.6,.7,.8,.9]
    list2=[1,2,3,4,5,6,7,8]

    msec = shuffler.Condition(list1, "msec", repeats)
    sec = shuffler.Condition(list2, "sec", repeats)

    secList = shuffler.MultiShuffler([msec, sec], 80).shuffle()

    jitter = []
    counter = 0
    for time in secList:
        seconds = getattr(time, "sec")
        millisecond = getattr(time, "msec")
        time = seconds + millisecond
        if time>=min_duration and time<=max_duration:
            counter+=1
            jitter.append(time)
        if counter==num_trials:
            break
    return jitter

main()