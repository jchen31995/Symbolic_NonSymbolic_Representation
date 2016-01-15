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
import trial #for stim creation


#LEFT TO DO: Creating 2nd Stimuli
#            Checking timing
#            Setting up SR Box
#            Debugging Dot Generation for 1-1
#            Adjusting Stimulus/Text Size/Color

def main():
    #num_trials has to be divisible by 72 (divisible by 9:all 9 numbers have to be shown and divisble by 4:50%-25%-25%)
    num_trials = 72
    if not num_trials%9==0:
        print "Each number must be shown. Number of trials has to be divisible by 9"
        exit()
    if not num_trials%4==0:
        print "Number of trials has to be divisible by 4 to ensure 50%-25%-25% ratio is preserved"
        exit()
    
    #trials has to be divisible by 72
    trials = 72
    #if for some reason you want more than 72 trials (not recommended -- takes much longer to run, also need to ease up on repeats[line 76])
    if num_trials>trials:
        temp = num_trials/72
        trials = trials + 72*(num_trials/72)
    repeats = 4
    
    #create stimuli
    trial_list=create_stimuli(num_trials,trials,repeats)
    print len(trial_list)
    
    #user GUI
    #if you want to trigger scanner, getting conditions
    info = create_user_prompt()
    trigger = info['Trigger fMRI']
    if trigger in ['yes', 'y']:
        trigger=True
    else:
        trigger=False
        
    practice = False
    if info['Practice'] == 'yes':
        practice = True
    
    input_method = info['Input']
    
    #UNCOMMENT TO TEST SRBOX AND KEYBOARD
    #start the iohub server and get the keyboard and PST box devices
    #iohub_config = {'serial.Serial': dict(name='serial', port='COM3', baud=19200,event_parser = dict(byte_diff=True))}
    #io = launchHubServer(**iohub_config)
    
    #srbox = io.devices.serial
    if input_method=='srbox':
        #for participant use
        srbox=io.devices.serial
        srbox.enableEventReporting(True)
    
        # Source: https://psychtoolbox-3.googlecode.com/svn/beta/Psychtoolbox/PsychHardware/CMUBox.m
        print('Switching response box to streaming mode and switching on lamp #3...')
        srbox.write(chr(numpy.uint8(128+32+64+4)))
        core.wait(0.25)
        print('...done.')
        
        
        #for researcher use
        kb = io.devices.keyboard
        kb.enableEventReporting(True)
    
    # initializes data collection for PST box and keyboard
    if input_method=='kb':
        kb = io.devices.keyboard
        kb.enableEventReporting(True)

    #serial adapter
    if trigger:
        ser = serial.Serial(port=7)
        ser.write(chr(numpy.uint8(128+32+64+1))) 
    

    ###CREATE WINDOW
    #win = visual.Window(size=screen_size, units='pix', fullscr=True, rgb = background_color)
    win = visual.Window(size=screen_size, units='pix', rgb = background_color)
    win.setRecordFrameIntervals(True)
    win.setMouseVisible(False)
    mouse = event.Mouse(visible=False, newPos=None, win=win)
    
    ###CREATE STIMULI
    onscr_num_stim = visual.TextStim(win, "", height =stim_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    onscr_dot_stim = visual.ImageStim(win, "blank.png", pos=[0,0])
    fixation_cross = visual.TextStim(win, "+", height = stim_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    onscr_jitter = visual.TextStim(win, "", height =stim_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    prompt_screen = visual.TextStim(win, "Same or different?", height =text_height, pos=[0,0], color=text_color, font='Courier New', bold=True)
    
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
    
    #iterating through every stimuli
    stim_dur = .5
    input_dur = 2.5
    input_method = info['Input']
    
    for trial in trial_list:
        #io.clearEvents('serial')
        #event.clearEvents()
        
        #for checking how accurate the time is to expected -- should we output to CSV?
        stopwatch_times=[]
        if trial.symbol=='nonsymbolic':
            trial_clock.reset()
            #First Stimulus (.5 sec)
            timing= draw_numStimulus(onscr_num_stim,win,trial.first_stim,trial_clock,stim_dur)
            stopwatch_times.append(timing)
            
            #Blank or fixation cross during jitter?
            #first jitter (1.5-5.5 sec)
            trial_clock.reset()
            timing = draw_jitter(onscr_jitter, trial_clock, win,trial.first_jitter)
            stopwatch_times.append(timing)
            
            #Second Stimulus (.5 sec)
            trial_clock.reset()
            timing= draw_numStimulus(onscr_num_stim,win,trial.second_stim,trial_clock,stim_dur)
            stopwatch_times.append(timing)
            
            #TODO: blank screen for 2500 msec ==2.5 sec or until subject responds
            #get_input(srbox,kb,trial_clock, input_method,trial,input_dur,fixation_cross,prompt_screen,win)

                
            #fixation jitter (1.9-8.4 sec)
            trial_clock.reset()
            timing = draw_jitter(fixation_cross, trial_clock, win,trial.fixation_jitter)
            stopwatch_times.append(timing)
            print stopwatch_times
            

           
        else:
            trial_clock.reset()
            #First Stimulus (.5 sec)
            timing= draw_dotStimulus(onscr_dot_stim,win,trial.first_image,trial_clock,stim_dur)
            stopwatch_times.append(timing)
            
            #Blank or fixation cross during jitter?
            #first jitter (1.5-5.5 sec)
            trial_clock.reset()
            timing = draw_jitter(onscr_jitter, trial_clock, win,trial.first_jitter)
            stopwatch_times.append(timing)
            
            #Second Stimulus (.5 sec)
            trial_clock.reset()
            timing= draw_dotStimulus(onscr_dot_stim,win,trial.second_image,trial_clock,stim_dur)
            stopwatch_times.append(timing)
            
            #TODO: blank screen for 2500 msec ==2.5 sec or until subject responds
            #get_input(srbox,kb,trial_clock, input_method,trial,input_dur,fixation_cross,prompt_screen,win)
            #fixation jitter (1.9-8.4 sec)
            trial_clock.reset()
            timing = draw_jitter(fixation_cross, trial_clock, win,trial.fixation_jitter)
            stopwatch_times.append(timing)
            print stopwatch_times
        
        logtocsv(sub,trial,stopwatch_times)
        
    sub.printData()
    print clock.getTime()
        

def create_user_prompt():
    config_data = get_config()

    #creates user prompt
    info = {'Subject':666, 'scan_id':'?', 'Session':1, 'Trigger fMRI': 'no','Experiment':'symbols', 'Input': 'srbox'}

    if config_data:
        for key in config_data.keys():
            info[key] = config_data[key]

    info = infoGUI(info)
    return info

#draws number stimuli
def draw_numStimulus(onscr_stim,window,stimulus,clock,stim_dur):
    onscr_stim.setText(stimulus)
    while clock.getTime()< stim_dur:
        onscr_stim.draw()
        window.flip()
    return clock.getTime()

#draws dot stimuli
def draw_dotStimulus(dot_stim,window, stimulus, clock, stim_dur):
    dot_stim .setImage(stimulus)
    while clock.getTime()<stim_dur:
        dot_stim.draw()
        window.flip()
    return clock.getTime()
    
#draws jitter 
def draw_jitter(onscr_jitter, clock, win,jitter_dur):
    while clock.getTime()<jitter_dur:
        onscr_jitter.draw()
        win.flip()
    return clock.getTime()


#gets user input
def get_input(srbox,kb,trial_clock, method,trial,input_dur,fixation_cross,prompt_screen,win):
    input_clock = core.Clock()
    if method == 'kb':
        #while loop keeps going until we get input
        prompt_screen.draw()
        win.flip()
        while trial_clock.getTime()<input_dur:        
            key = kb.getEvents()
            if key:
                trial.RT = input_clock.getTime()
                trial.resp = key[0].current_byte
                if key == 'q' or key=='escape':
                    exit()
                print key
                break
        while input_clock.getTime()<input_dur:
            fixation_cross.draw()
            win.flip()

    if method == 'srbox':
        prompt_screen.draw()
        win.flip()
        while trial_clock.getTime()<input_dur:        
            key = srbox.getEvents()
            quit = kb.getEvents()
            if key:
                trial.RT = input_clock.getTime()
                trial.key = key[0].current_byte
                print trial.key
                break
            if quit:
                if quit[0].key=='q' or quit[0].key=='escape':
                    exit()
        while input_clock.getTime()<input_dur:
            fixation_cross.draw()
            win.flip()



#log current trial to output csv
def logtocsv(sub,trial,stopwatch_times):
    sub.inputData(trial.trial_no, 'Symbol', trial.symbol)
    sub.inputData(trial.trial_no, '1st Stim', trial.first_stim)
    sub.inputData(trial.trial_no, '2nd Stim', trial.second_stim)
    sub.inputData(trial.trial_no, '1st Image', trial.first_image)
    sub.inputData(trial.trial_no, '2nd Image', trial.second_image)
    sub.inputData(trial.trial_no, 'condition', trial.condition)
    sub.inputData(trial.trial_no, 'First jitter', trial.first_jitter)
    sub.inputData(trial.trial_no, 'Fixation jitter', trial.fixation_jitter)
    sub.inputData(trial.trial_no, 'RESP', trial.resp)
    sub.inputData(trial.trial_no, 'CRESP', trial.cresp)
    sub.inputData(trial.trial_no, 'RT', trial.RT)

#Requirement that num_trials divisible by 36 (all 9 numbers must be seen in one block and 4 to preserve 50-25-25)
def create_stimuli(num_trials,trials,repeats):
    list1=['same1','same2','greater','less']
    list2=[1,2,3,4,5,6,7,8,9]
    list3=['symbolic','nonsymbolic']


    samedifflist = shuffler.Condition(list1, "condition", repeats)
    numlist = shuffler.Condition(list2, "num", repeats)
    numdotlist = shuffler.Condition(list3, "nd", repeats)
    stimList = shuffler.MultiShuffler([samedifflist,numlist,numdotlist], trials).shuffle()
    
    
    
    #DEBUGGING
    nd_list=[]
    num_sym = 0
    num_nonsym = 0
    for stim in stimList:
        nd = getattr(stim, "nd")
        if nd == 'symbolic':
            num_sym+=1
        if nd == 'nonsymbolic':
            num_nonsym+=1
        nd_list.append(nd)
    
        
    
    #generating jitter lists
    first_jitter = generate_jitter(1.5,5.5,num_trials, repeats)
    fixation_jitter = generate_jitter(1.9,8.4,num_trials,repeats)
    
    
    
    #stimuli is a list of tuples where (first stimulus, second stimulus)
    stimuli=[]
    #*****
    areaperimeter = shuffler.Shuffler(['area','perimeter'],(num_trials/2),repeats).shuffle()
    areaperimeter_counter = 0
    
    
    
    #used stimli list
    used=[]
    
    #3 lists to store every png's for each condition
    imagelist= glob.glob("stimuli\*.png")
    
    stimuli_list=[]
    trial_no=1
    
    for stim,jitter1,jitter2 in zip(stimList,first_jitter,fixation_jitter):
        #get attributes from stimList
        condition = getattr(stim, "condition")
        num = getattr(stim, "num")
        nd = getattr(stim, "nd")

            
        if num==9 and condition=='greater':
            num=random.randrange(1,9)
        
        if num==1 and condition=='less':
            num=random.randrange(2,10)
        
        #equal number of dots
        if (condition=='same1' or condition=='same2') and nd =='symbolic':
            contains = "_%s_%s_%s_S1" % (num,num,areaperimeter[areaperimeter_counter])
            for image1 in imagelist:
                if contains and "S1" in image1 and image1 not in used:
                    image2 = image1[:-5] + '2.png'
                    stimuli.append([image1,image2])
                    areaperimeter_counter+=1
                    used.append(image1)
                    temp = trial.Trial(trial_no, nd, num, num,image1,image2,condition,jitter1,jitter2, cresp=1)
                    stimuli_list.append(temp)
                    break


        #equal numbers
        if (condition=='same1' or condition=='same2') and nd =='nonsymbolic':
            stimuli.append(["%s" % num,"%s"% num])
            temp = trial.Trial(trial_no, nd, num,num,condition=condition, first_jitter=jitter1,fixation_jitter=jitter2, cresp=1)
            
            stimuli_list.append(temp)

        #2nd stimulus greater than 1st
        #generating dot stim
        if condition=='greater' and nd =='symbolic':
            num2=num+1
            contains = "%s_%s_%s" % (num,num2,areaperimeter[areaperimeter_counter])
            for image1 in imagelist:
                if contains and "S1" in image1 and image1 not in used:                                                                         
                    image2 = image1[:-5] + '2.png'
                    stimuli.append([image1,image2])
                    areaperimeter_counter+=1
                    used.append(image1)
                    temp = trial.Trial(trial_no, nd, num, num2, image1, image2, condition, jitter1, jitter2,2)
                    stimuli_list.append(temp)
                    break

        #number stimulus
        if condition=='greater' and nd =='nonsymbolic':
            if num ==9:
                num = random.randrange(0,9)
            num2 = num+1

            stimuli.append(["%s" % num, "%s" % num2])
            temp = trial.Trial(trial_no, nd, num, num2, condition=condition,first_jitter=jitter1,fixation_jitter=jitter2, cresp=2)
            stimuli_list.append(temp)


        #2nd stimulus less than 1st
        #generating dot stim
        if condition=='less' and nd=='symbolic':
            num2=num-1
            contains = "%s_%s_%s" % (num,num2,areaperimeter[areaperimeter_counter])
            for image1 in imagelist:
                if contains and "S1" in image1 and image1 not in used:
                    image2 = image1[:-5] + '2.png'
                    stimuli.append([image1,image2])
                    areaperimeter_counter+=1
                    used.append(image1)
                    temp = trial.Trial(trial_no, nd, num, num2, image1, image2, condition, jitter1, jitter2, 2)
                    stimuli_list.append(temp)
                    break

            
        #generating number stim
        if condition=='less' and nd =='nonsymbolic':
            if num==1:
                num = random.randrange(2,10)
                
            num2 = num-1

            temp = trial.Trial(trial_no, nd, num, num2, condition=condition, first_jitter=jitter1, fixation_jitter=jitter2, cresp=2)
            stimuli_list.append(temp)
        
        trial_no+=1
    

    return stimuli_list


#generates a list of jitter between min_dur and max_dur
def generate_jitter(min_duration,max_duration,num_trials, repeats):
    num = 160 + 160*(num_trials/80)
    list1 = numpy.linspace (1.0,8.9, num)
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