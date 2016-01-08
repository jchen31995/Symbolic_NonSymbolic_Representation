import glob
import os
import random # for stimuli generating
import psychopy
from psychopy import core, visual, event, gui, parallel
import subject # for user prompt
import shuffler # for shuffling stimuli list
from common import * #for window size and all that good stuff
import numpy #for generating jitter

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
    
    num_trials = 84
    if not num_trials%4==0:
        print "Number of trials has to be divisible by 4 to ensure 50%-25%-25% ratio is preserved"
        exit()
    
    #trials has to be divisible by 72
    trials = 72
    #if for some reason you want more than 72 trials (not recommended -- takes much longer to run, also need to ease up on repeats)
    if num_trials>trials:
        temp = num_trials/72
        trials = trials + 72*(num_trials/72)
    
    repeats = 4
    
    keeping_track=[]
    #create stimuli, jitters
    stimuli=create_stimuli(num_trials,trials,repeats)
    print stimuli
    
    #generating jitter lists
    first_jitter = generate_jitter(1.5,5.5,num_trials, repeats)
    fixation_jitter = generate_jitter(1.9,8.4,num_trials,repeats)
    for i in range(0,num_trials):
        keeping_track.append(i)
    num_or_image=[]
    for s in stimuli:
        #if it's a number
        if len(s[0])==1:
            num_or_image.append(0)
        else:
            num_or_image.append(1)
    
    
    
    
    
    ###CREATE WINDOW
    #win = visual.Window(size=screen_size, units='pix', fullscr=True, rgb = background_color)
    win = visual.Window(size=screen_size, units='pix', rgb = background_color)
    win.setRecordFrameIntervals(True)
    win.setMouseVisible(False)
    mouse = event.Mouse(visible=False, newPos=None, win=win)
    
    ###CREATE STIMULI
    onscr_stim = visual.TextStim(win, "", height =text_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    #dot_stim = visual.ImageStim(win, "", pos=[0,0])
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
    for trial_no,display in zip(keeping_track,num_or_image):
        if display==0:
            #io.clearEvents('serial')
            #event.clearEvents()
            
            #First Stimulus (.5 sec)
            onscr_stim.setText(stimuli[trial_no][0])
            while trial_clock.getTime()<.5:
                onscr_stim.draw()
                win.flip()
            trial_clock.reset()
            
            #Blank or fixation cross during jitter?
            #first jitter (1.5-5.5 sec)
            onscr_stim.setText("")
            while trial_clock.getTime()<first_jitter[trial_no]:
                onscr_stim.draw()
                win.flip()
            trial_clock.reset()
            
            #Second Stimulus (.5 sec)
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
            """        
                
            #fixation jitter (1.9-8.4 sec)
            while trial_clock.getTime()<fixation_jitter[trial_no]:
                fixation_cross.draw()
                win.flip()
        else:
            #io.clearEvents('serial')
            #event.clearEvents()
            
            #First Stimulus (.5 sec)
            dot_stim = visual.ImageStim(win, stimuli[trial_no][0], pos=[0,0])
            while trial_clock.getTime()<.5:
                dot_stim.draw()
                win.flip()
            trial_clock.reset()
            
            #Blank or fixation cross during jitter?
            #first jitter (1.5-5.5 sec)
            onscr_stim.setText("")
            while trial_clock.getTime()<first_jitter[trial_no]:
                onscr_stim.draw()
                win.flip()
            trial_clock.reset()
            
            #Second Stimulus (.5 sec)
            dot_stim = visual.ImageStim(win, stimuli[trial_no][1], pos=[0,0])
            while trial_clock.getTime()<.5:
                dot_stim.draw()
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
            """        
                
            #fixation jitter (1.9-8.4 sec)
            while trial_clock.getTime()<fixation_jitter[trial_no]:
                fixation_cross.draw()
                win.flip()
        


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
    list2=[1,2,3,4,5,6,7,8,9]
    list3=['symbolic','nonsymbolic']


    same_or_diff = shuffler.Condition(list1, "samediff", repeats)
    integer = shuffler.Condition(list2, "integer", repeats)
    numdot = shuffler.Condition(list3, "numdot", repeats)
    stimList = shuffler.MultiShuffler([same_or_diff,integer,format], trials).shuffle()
    
    
    
    samedifflist=[] #equal or not equal (greater/less)
    numlist=[] #stimulus integer
    numdotlist=[] #numeric or dot


    for stim in stimList:
        same_diff = getattr(stim, "samediff")
        num = getattr(stim, "integer")
        numdot = getattr(stim, "numdot")
        if same_diff=='same':
            samedifflist.append(same_diff)
            numlist.append(num)
            numdotlist.append(numdot)
        
        if same_diff=='greater':
            samedifflist.append(same_diff)
            numlist.append(num)
            numdotlist.append(numdot)
                
        
        if same_diff=='less':
            samedifflist.append(same_diff)
            numlist.append(num)
            numdotlist.append(numdot)
        

    #stimuli is a list of tuples where (first stimulus, second stimulus)
    stimuli=[]
    
    areaperimeter = shuffler.ListAdder(['area','perimeter'],(len(numlist)/4)).shuffle()
    areaperimeter_counter = 0
    
    #used stimli list
    used=[]
    
    #3 lists to store every png's for each condition
    equalto= glob.glob("stimuli/*_equal_*.png")
    lessthan=glob.glob("stimuli/*_lessthan_*.png")
    greaterthan=glob.glob("stimuli/*_greaterthan_*.png")
   
    
    for condition, stim, nd in zip(samedifflist,numlist,numdotlist):
        #equal number of dots
        if condition=='same' and nd =='symbolic':
            contains = "_%s_%s_%s_" % (stim,stim,areaperimeter[areaperimeter_counter])
            for e in equalto:
                if contains in e and e not in used:
                    temp = e[:-5] + '2.png'
                    stimuli.append([e,temp])
                    areaperimeter_counter+=1
                    used.append(e)
                    break


        #equal numbers
        if condition=='same' and nd =='nonsymbolic':
            stimuli.append(["%s" % stim,"%s"% stim])


        #2nd stimulus greater than 1st
        #generating dot stim
        if condition=='greater' and nd =='symbolic':
            contains = "greaterthan_%s" % (stim)
            ap=areaperimeter[areaperimeter_counter]
            for g in greaterthan:
                if contains in g and g not in used and ap in g :
                    temp = g[:-5] + '2.png'
                    stimuli.append([g,temp])
                    areaperimeter_counter+=1
                    used.append(g)
                    break

        #number stimulus
        if condition=='greater' and nd =='nonsymbolic':
            if stim ==9:
                stim = random.randrange(0,9)
                
            temp = random.randrange(stim+1,10)

            #if for some reason if it doesnt work
            if not temp>stim:
                print ("Second stimulus was not greater than first stimulus")
                exit()
            stimuli.append(("%s" % stim, "%s" % temp))


        #2nd stimulus less than 1st
        #generating dot stim
        if condition=='less' and nd=='symbolic':
            contains = "lessthan_%s" % (stim)
            ap=areaperimeter[areaperimeter_counter]
            for l in lessthan:
                if contains in l and l not in used and ap in l:
                    temp = l[:-5] + '2.png'
                    stimuli.append([l,temp])
                    areaperimeter_counter+=1
                    used.append(l)
                    break

            
        #generating number stim
        if condition=='less' and nd =='nonsymbolic':
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
    list1 = numpy.linspace (1.0,8.9, num = 80)
    time_list = []
    for l in list1:
        time_list.append(float("%.1f"%l))
    time_list=shuffler.ListAdder(time_list,1).shuffle()
    
    jitter = []
    counter = 0
    #because first jitter is between 1.5 and 5.5 while 2nd is between 1.9 and 8.4 sec
    for time in time_list:
        if time>=min_duration and time<=max_duration:
            counter+=1
            jitter.append(time)
        if counter==num_trials:
            break
    return jitter

main()