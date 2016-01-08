from ShapeMaster import *
import glob
import shutil

bgcolor = (255,255,255)
colors = (0, 0, 0)
box = (640, 480) #region of screen occupied by dots

shape = 'circle'

n1s = [1,2,3,4,5,6,7,8,9]
n2s = [1,2,3,4,5,6,7,8,9]


#how many of each condition you want to generate
num_pngs=1
keeping_track=[]
for i in range(1,num_pngs+1):
    keeping_track.append(i)





#file path will be something like circle__equal_3_3_area_S1 (shape_number_condition_firststimulus_secondstimulus_areaperimeter_stimnum)
#match the areas
area = 0.045

shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)
for k in keeping_track:
    for n1 in n1s:
        for n2 in n2s:
            shapeMaster.shapeArranger([n1, n2])
            if n2==n1:
                name = "%s_equal_%s_%s_area" % (k,n1,n2)
            if n2<n1:
                name = "%s_lessthan_%s_%s_area" % (k, n1, n2)
            if n2>n1:
                name = "%s_greaterthan_%s_%s_area" % (k, n1,n2)
            shapeMaster.drawSingle(name)


#match the perimeters
perimeter = 0.8

shapeMaster = ShapeMaster(box, [perimeter, perimeter], shape=shape, sizemeasure = 'perimeter', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)
for k in keeping_track: 
    for n1 in n1s:
        for n2 in n2s:
            shapeMaster.shapeArranger([n1, n2])
            if n2==n1:
                name = "%s_equal_%s_%s_perimeter" % (k, n1,n2)
            if n2<n1:
                name = "%s_lessthan_%s_%s_perimeter" % (k, n1, n2)
            if n2>n1:
                name = "%s_greaterthan_%s_%s_perimeter" % (k,n1,n2)
            shapeMaster.drawSingle(name)
