import glob

for name in glob.glob(stimuli/*):
    if "equal" in name:
        shutile.move(name, "/stimuli/equal")