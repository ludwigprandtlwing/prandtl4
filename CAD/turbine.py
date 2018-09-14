# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:09:58 2017

@author: Nejc
"""

# important data
n_blades = 3 # number of blades
r_hub = 57 # radius of hub parabola
l_hub = 120 # length of hub parabola
m_hub = 28 # hub displacement on z-axis
hub_steps = 15 # resolution of hub ellipse

#############

import FreeCAD
import Part
import Draft
import math
import re
import os

import numpy as np

# fetch the profiles file
input_file = os.path.dirname(__file__) + "/blade.txt"
print(input_file)

# cross-section data:
# [ a list of cross sections; each cross-section is a list of: xyz-points
#   [[], [], [], ...] # foil 1
#   [[], [], [], ...] # foil 2
# ]

foils = [[]] # contains lists of cross-section coordinates

num_re = re.compile("[+-]?\d\.\d+e[+-]\d+") # scientific notation

with open(input_file, "r") as blade_file:   
    # first line contains the name of the qblade profile
    blade_file.readline()
    # the next line contains the 'x y z' titles
    blade_file.readline()
    
    # every line that doesn't contain an xyz-point denotes a new cross-section
    for line in blade_file:
        foil_coords = re.findall(num_re, line)
            
        if len(foil_coords) == 3: # a coordinate point
            # these lines should already have coordinates
            x = float(foil_coords[0])*1000
            # y-coordinate should be the same for the whole cross-section, 
            # but isn't, wtf, qBlade?
            # only read the y-value once per cross-section
            if len(foils[-1]) == 0: # this whil be the first entry for this section
                y = float(foil_coords[1])*1000
            
            z = float(foil_coords[2])*1000

            foils[-1].append([x, y, z])

        else: # end of this cross-section
            foils.append([])
            y = None

# clean up mess from qBlade:
for i in range(len(foils)):
    # some cross-sections are doubled
    f = foils[i]
    l = len(f)

    if l > len(foils[0]): # some lists in the end are doubled
        foils[i] = foils[i][:l/2]

for f in foils:
    l = len(f)

    del f[l/2] # the first value repeats in the middle
    del f[0] # but is not needed in the beginning
    del f[-1] # nor in the end

# create a new freecad document
doc = FreeCAD.newDocument("CoppeliaRotor")

# create splines with cross-sections
def pointsToVectors(points_list):
    return[FreeCAD.Vector(p[0], p[1], p[2]) for p in points_list]

def pointsToWire(points_list):
    return Draft.makeWire(pointsToVectors(points_list), closed=True)

xs_wires = []

for f in foils:
    xs_wires.append(pointsToWire(f))

blade = doc.addObject('Part::Loft','Blade')
blade.Solid = True
blade.Sections = xs_wires

# calculate points for the hub half-ellipse
# it's all in yz-plane
l_hub = float(l_hub)
r_hub = float(r_hub)

ys = list(np.linspace(0, r_hub, hub_steps))
zs = [m_hub - l_hub/r_hub*(r_hub**2 - y**2)**0.5 for y in ys]

ys.append(0)
zs.append(m_hub)

ys.append(ys[0])
zs.append(zs[0])

hub_profile = Draft.makeWire([FreeCAD.Vector(0, ys[i], zs[i]) for i in range(len(ys))])

hub = doc.addObject("Part::Revolution", "Hub")
hub.Source = hub_profile
hub.Axis = (0.00,0.00,1.00)
hub.Base = (0.00,0.00,0.00)
hub.Angle = 360.
hub.Solid = True

# fuse the blade and the hub
fusion_object = doc.addObject("Part::MultiFuse","Fusion")
fusion_object.Shapes = [blade, hub]

# copy the blade a number of times
array = Draft.makeArray(fusion_object, FreeCAD.Vector(0, 0, 0), 360, n_blades)
array.Fuse = True

doc.recompute()
