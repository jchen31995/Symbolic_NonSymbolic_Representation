


class Trial:
    def __init__(self,trial_no = 0, symbol = "",first_stim=0,second_stim=0,first_image="",second_image="",condition="",first_jitter=0,fixation_jitter=0,RT = 2.5, resp = 0,cresp=0):
        self.trial_no = trial_no
        self.symbol = symbol
        self.first_stim = first_stim
        self.second_stim = second_stim
        self.first_image = first_image
        self.second_image = second_image
        self.condition = condition
        self.first_jitter = first_jitter
        self.fixation_jitter = fixation_jitter
        self.RT = RT
        self.resp = resp
        self.cresp = cresp