from ShapeMaster import *
import glob
import os

if not os.path.exists("/stimuli"):
    os.makedirs("/stimuli")

#since ShapeMaster designed such that you can make shapes of two different colors
colors = ((255,255,255),(255,255,255))
bgcolor = (0, 0, 0)
box = (640, 480) #region of screen occupied by dots

shape = 'circle'

n1s = [1,2,3,4,5,6,7,8,9]
condition = ['lessthan','greaterthan','equal']


#how many of each condition you want to generate
num_pngs=5
keeping_track=[]
for i in range(1,num_pngs+1):
    keeping_track.append(i)

#file path will be something like circle__equal_3_3_area_S1 (shape_number_condition_firststimulus_secondstimulus_areaperimeter_stimnum)
#match the areas
area = 0.045

shapeMaster = ShapeMaster(box, [area, area], shape=shape, sizemeasure = 'area', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)
for k in keeping_track:
    for n1 in n1s:
        for c in condition:
            if c=='equal':
                n2=n1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_area_v%s" % (n1,n2,k)
                shapeMaster.drawSingle(name)
            if c=='lessthan' and n1!=1:
                n2=n1-1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_area_v%s" % (n1, n2,k)
                shapeMaster.drawSingle(name)
            if c=='greaterthan' and n1!=9:
                n2=n1+1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_area_v%s" % (n1,n2,k)
                shapeMaster.drawSingle(name)


#match the perimeters
perimeter = .2

shapeMaster = ShapeMaster(box, [perimeter, perimeter], shape=shape, sizemeasure = 'perimeter', colors = colors, bgcolor = bgcolor, outline=(0, 0, 0), drawOutline=True)
for k in keeping_track: 
    for n1 in n1s:
        for c in condition:
            if c=='equal':
                n2=n1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_perimeter_v%s" % (n1,n2,k)
                shapeMaster.drawSingle(name)
            if c=='lessthan' and n1!=1:
                n2=n1-1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_perimeter_v%s" % (n1, n2, k)
                shapeMaster.drawSingle(name)
            if c=='greaterthan' and n1!=9:
                n2=n1+1
                shapeMaster.shapeArranger([n1, n2])
                name = "%s_%s_perimeter_v%s" % (n1,n2, k)
                shapeMaster.drawSingle(name)