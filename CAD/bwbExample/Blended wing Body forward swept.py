# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 20:09:30 2017

@author: wingc
"""
import FreeCAD, Draft, Part
import importAirfoilDAT
import math
from FreeCAD import Base
#
#
FreeCAD.newDocument("Blended Wing Body multi taper")

'''
FUNDAMENTAL INPUT PARAMETERS
'''
#'''
#Aerodynamic & structural inputs
#'''
##Max take off weight
#MTOW = 406e3 #kg
##Max Lift coefficient with slats at take-off
#Clmax = 1.28
##stall speed
#v = 80 #m/s
##cruise mach
#M = 0.82

#aerofoils
'''
input the system path for each aerofoil
'''

bodyaerofoil = str() #NACA25112
wingaerofoil = str() #SC20714
wingletaerofoil = str() #NACA0012
##define original aerofoil thickness ratios, see airfoil file name NACA XXX12, SCXXX14
bodyorig = 0.12
wingorig = 0.14
wingletorig = 0.12
##define desired thickness ratios
tbody = 0.188
twinglet = 0.08
ttip = 0.08
dt = tbody-ttip
#Aspect Ratio, AR
#WHOLE BWB (WING + CENTRE BODY)
AR = 3.86 #3.5 <= AR <= 4
#sref area
S = 1091e6
#centreline chord
cr = 39700
#sweep
wingsweep = -48 #LEADING EDGE SWEEP, range: 35 <= wingsweep <= 45
bodysweep = 57.6
wingletsweep = 45
taper = 0.1335 #FORWARD SWEEP: MAX TAPER = 0.14, AFT SWEEP: MAX TAPER = 0.228
taper_winglet = 0.3
#CENTRE BODY FRACTION OF HALF SPAN
acentre = 0.3
#outer wing incidence angle
incidence = 1
#tip twist angle
EPS = 1.5
#define dihedral angle in degrees
dihedral = 4.6

'''
THE FOLLOWING CAN BE ALTERED (WITH CARE) OR LEFT AS IS
'''
#OUTER WING SPAN FRACTIONS 
awing = 1-acentre
#OVERALL span b
b = pow(S*AR,0.5) #span in mm, range: [ ] <= b <= 800000
#OUTER WING SPAN
bd = awing*b
#outer wing aerofoil position FUNCTION OF OUTER SPAN BD
akink = 0.2463
#section sweep, coefficients
sweep01 = 0.305*bodysweep
sweep12 = bodysweep
sweep23 = bodysweep
sweep34 = bodysweep
sweep45 = bodysweep
sweep56 = wingsweep
sweep67 = sweep56
sweep6t = sweep56
#winglet sweep
sweepW = wingsweep
#OUTER WING TWIST/UNIT LENGTH
twist = -EPS/(bd/2)
##winglet dihedral
wingletdihedral=70
#tail fin height
ht = 0.133*b


'''
CALCULATE DEPENDENT PARAMATERS
'''
#CENTREBODY SECTION POSITIONS AS FUNCTION OF CENTREBODY WIDTH
a1 = 0.1349 #SECTION 1
a2 = 0.4048 #SECTION 2
a3 = a2+(1-a2)/4
a4 = a2+(1-a2)/2
#blend region
ablend = 0.1
#centre body
z0 = 0
z5 = acentre*b/2
z1 = a1*z5
z2 = a2*z5
z3 = a3*z5
z4 = a4*z5
#body - wing blend
z6 = z5 + ablend*bd/2
#outer wing
z7 = z5 + akink*bd/2
ztpos = b/2
#kink aft sweep
x1 = z1*(math.tan(sweep01*(math.pi)/180))
x2 = x1 + (z2-z1)*(math.tan(sweep12*(math.pi)/180))
x3 = x2 + (z3-z2)*(math.tan(sweep23*(math.pi)/180))
x4 = x3 + (z4-z3)*(math.tan(sweep34*(math.pi)/180))
x5 = x4 + (z5-z4)*(math.tan(sweep45*(math.pi)/180))
#wing blend position
x6 = x5 + (z6-z5)*(math.tan(sweep56*(math.pi)/180))
#outboard wing position
x7 = x6 + (z7-z6)*(math.tan(sweep67*(math.pi)/180))

#wing tip position
xtpos = x7 + (ztpos-z7)*(math.tan(sweep6t*(math.pi)/180))
ytpos = (ztpos - z7)*(math.tan(dihedral*(math.pi)/180))
#position winglet tip aerofoil
ztwpos = ztpos + 0.05*b
ytwpos = ytpos + (ztwpos-ztpos)*(math.tan(wingletdihedral*(math.pi)/180))
xtwpos = xtpos + (ytwpos - ytpos)*(math.tan(sweepW*(math.pi)/180))
#centre body tapers
taper01 = 0.994*(1 - x1/cr)
taper02 = 0.975*(1 - x2/cr)
taper03 = 0.95*(1 - x3/cr)
taper04 = 0.9*(1-x4/cr)
taper05 = 0.75*(1-x5/cr)
#centre body
c1 = taper01*cr
c2 = taper02*cr
c3 = taper03*cr
c4 = taper04*cr
ct = taper*cr
#outboard wing
c5 = taper05*cr
taper5t = ct/c5

if wingsweep<0:
    taper07 = taper05 + (taper-taper05)/(ztpos-z5)*(z7-z5)
    ctw = 1.5*ct
    xtwpos = x2 + c2 - ctw
    ytwpos = 0
    ztwpos = z2
    ctwt = ctw*taper_winglet
    ytwtpos = ytwpos + ht
    ztwtpos = ztwpos + ht/math.tan(wingletdihedral*(math.pi)/180)
    xtwtpos = xtwpos + ht*math.tan(wingletsweep*(math.pi)/180)
    t_ytwt = twinglet
    ytwt = ctwt*(t_ytwt/wingletorig)
else:
    taper07 = 2.264*taper
    ztwpos = ztpos + 0.05*b
    ytwpos = ytpos + (ztwpos-ztpos)*(math.tan(wingletdihedral*(math.pi)/180))
    xtwpos = xtpos + (ytwpos - ytpos)*(math.tan(sweepW*(math.pi)/180))
    ctw = ct*taper_winglet

c7 = taper07*cr
taper57 = c7/c5
taper06 = taper05 + (taper07-taper05)/(z7-z5)*(z6-z5)
c6 = c5 + (c7-c5)/(z7-z5)*(z6-z5)

print(taper01,taper02,taper03,taper04,taper05,taper06,taper07,taper)
print(cr,c1,c2,c3,c4,c5,c6,ct)

#winglet
#section twist
twist7 = incidence + twist*(z7-z5)
twist_tip = twist7 + twist*(ztpos - z7)
#SECTION THICKNESS RATIOS
t1 = tbody
t2 = tbody - dt/z5 * z2
t3 = tbody - dt/z5 * z3
t4 = tbody - dt/z5 * z4
t5 = ttip
t6 = ttip
t7 = ttip
#Y SCALE FACTORS
ybody = cr*(tbody/bodyorig)
y1 = t1/bodyorig * c1
y2 = t2/bodyorig * c2
y3 = t3/bodyorig * c3
y4 = t4/bodyorig * c4
y5 = t5/bodyorig * c5
y6 = t6/wingorig * c6
y7 = t7/wingorig * c7
yt = ct*(ttip/wingorig)
ytw = ctw*(twinglet/wingletorig)

#print(x1,x2,x3,x4,xtpos)
#print(ytpos,ytwpos)
#print(z3,z1,z2,z4,ztwpos)
#print(cr,c1,c2,c3,c4,ct,ctw)
#print(taper01,taper02,taper03,taper04,taper05)
#print(t1,t2,t3,t4)
#print(ybody,y1,y2,y3,y4,yt,ytw)


#import centre body (root) aerofoil data
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(cr,ybody,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

##import kink (outer centrebody) aerofoil from library
#####1
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c1,y1,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline001").Placement = FreeCAD.Placement(FreeCAD.Vector(x1,0,z1),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

#####2
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c2,y2,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline002").Placement = FreeCAD.Placement(FreeCAD.Vector(x2,0,z2),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

###3 start of outer wing
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c3,y3,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline003").Placement = FreeCAD.Placement(FreeCAD.Vector(x3,0,z3),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

#####4
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c4,y4,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline004").Placement = FreeCAD.Placement(FreeCAD.Vector(x4,0,z4),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

##5
importAirfoilDAT.insert(bodyaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c5,y5,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline005").Placement = FreeCAD.Placement(FreeCAD.Vector(x5,0,z5),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

##centre-body - wing blending region.
##6
importAirfoilDAT.insert(wingaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c6,y6,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline006").Placement = FreeCAD.Placement(FreeCAD.Vector(x6,0,z6),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

#OUTBOARD WING SECTIONS
##7
importAirfoilDAT.insert(wingaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(c7,y7,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline007").Placement = FreeCAD.Placement(FreeCAD.Vector(x7,0,z7),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-twist7))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

##tip
importAirfoilDAT.insert(wingaerofoil,FreeCAD.ActiveDocument.Name)
points = FreeCAD.ActiveDocument.ActiveObject.Points
Draft.makeBSpline(points, closed=True)
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(ct,yt,0),center=FreeCAD.Vector(0,0,0),legacy=True)
FreeCAD.ActiveDocument.getObject("BSpline008").Placement = FreeCAD.Placement(FreeCAD.Vector(xtpos,ytpos,ztpos),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-twist_tip))
FreeCAD.ActiveDocument.removeObject("DWire")
FreeCAD.ActiveDocument.recompute()

if wingsweep<0:
    importAirfoilDAT.insert(wingletaerofoil,FreeCAD.ActiveDocument.Name)
    points = FreeCAD.ActiveDocument.ActiveObject.Points
    Draft.makeBSpline(points, closed=True)
    Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(ctw,ytw,0),center=FreeCAD.Vector(0,0,0),legacy=True)
    FreeCAD.ActiveDocument.getObject("BSpline009").Placement = FreeCAD.Placement(FreeCAD.Vector(xtwpos,ytwpos,ztwpos),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),-wingletdihedral))
    FreeCAD.ActiveDocument.removeObject("DWire")
    FreeCAD.ActiveDocument.recompute()
    importAirfoilDAT.insert(wingletaerofoil,FreeCAD.ActiveDocument.Name)
    points = FreeCAD.ActiveDocument.ActiveObject.Points
    Draft.makeBSpline(points, closed=True)
    Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(ctwt,ytwt,0),center=FreeCAD.Vector(0,0,0),legacy=True)
    FreeCAD.ActiveDocument.getObject("BSpline010").Placement = FreeCAD.Placement(FreeCAD.Vector(xtwtpos,ytwtpos,ztwtpos),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),-wingletdihedral))
    FreeCAD.ActiveDocument.removeObject("DWire")
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.ActiveDocument.addObject('Part::Loft','LEFT_WINGLET')
    FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline009, FreeCAD.ActiveDocument.BSpline010]
    FreeCAD.ActiveDocument.ActiveObject.Solid=True
    FreeCAD.ActiveDocument.ActiveObject.Ruled=False
    FreeCAD.ActiveDocument.ActiveObject.Closed=False
    FreeCAD.ActiveDocument.recompute()
else:
    importAirfoilDAT.insert(wingletaerofoil,FreeCAD.ActiveDocument.Name)
    points = FreeCAD.ActiveDocument.ActiveObject.Points
    Draft.makeBSpline(points, closed=True)
    Draft.scale(FreeCAD.ActiveDocument.ActiveObject,delta=FreeCAD.Vector(ctw,ytw,0),center=FreeCAD.Vector(0,0,0),legacy=True)
    FreeCAD.ActiveDocument.getObject("BSpline009").Placement = FreeCAD.Placement(FreeCAD.Vector(xtwpos,ytwpos,ztwpos),FreeCAD.Rotation(FreeCAD.Vector(1,0,0),-wingletdihedral))
    FreeCAD.ActiveDocument.removeObject("DWire")
    FreeCAD.ActiveDocument.recompute()
    FreeCAD.ActiveDocument.addObject('Part::Loft','LEFT_WINGLET')
    FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline008, FreeCAD.ActiveDocument.BSpline009]
    FreeCAD.ActiveDocument.ActiveObject.Solid=True
    FreeCAD.ActiveDocument.ActiveObject.Ruled=False
    FreeCAD.ActiveDocument.ActiveObject.Closed=False
    FreeCAD.ActiveDocument.recompute()


##loft bewtween surfaces
#LEFT WING
FreeCAD.ActiveDocument.addObject('Part::Loft','CENTREBODY_1_L')
FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline,FreeCAD.ActiveDocument.BSpline001,FreeCAD.ActiveDocument.BSpline002 ]
FreeCAD.ActiveDocument.ActiveObject.Solid=True
FreeCAD.ActiveDocument.ActiveObject.Ruled=False
FreeCAD.ActiveDocument.ActiveObject.Closed=False
FreeCAD.ActiveDocument.recompute()

FreeCAD.ActiveDocument.addObject('Part::Loft','CENTREBODY_2_L')
FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline002, FreeCAD.ActiveDocument.BSpline003,FreeCAD.ActiveDocument.BSpline004, FreeCAD.ActiveDocument.BSpline005]
FreeCAD.ActiveDocument.ActiveObject.Solid=True
FreeCAD.ActiveDocument.ActiveObject.Ruled=False
FreeCAD.ActiveDocument.ActiveObject.Closed=False
FreeCAD.ActiveDocument.recompute()

FreeCAD.ActiveDocument.addObject('Part::Loft','OUTER_WING_1_L')
FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline005,FreeCAD.ActiveDocument.BSpline006,FreeCAD.ActiveDocument.BSpline007]
FreeCAD.ActiveDocument.ActiveObject.Solid=True
FreeCAD.ActiveDocument.ActiveObject.Ruled=False
FreeCAD.ActiveDocument.ActiveObject.Closed=False
FreeCAD.ActiveDocument.recompute()

FreeCAD.ActiveDocument.addObject('Part::Loft','OUTER_WING_2_L')
FreeCAD.ActiveDocument.ActiveObject.Sections=[FreeCAD.ActiveDocument.BSpline007,FreeCAD.ActiveDocument.BSpline008]
FreeCAD.ActiveDocument.ActiveObject.Solid=True
FreeCAD.ActiveDocument.ActiveObject.Ruled=False
FreeCAD.ActiveDocument.ActiveObject.Closed=False
FreeCAD.ActiveDocument.recompute()

#centrebody fusion
FreeCAD.activeDocument().addObject("Part::MultiFuse","CENTREBODY_FUSION_L")
FreeCAD.activeDocument().CENTREBODY_FUSION_L.Shapes = [FreeCAD.activeDocument().CENTREBODY_2_L,FreeCAD.activeDocument().CENTREBODY_1_L]
FreeCAD.ActiveDocument.recompute()

##LEFT OUTER WING FUSION
#FreeCAD.activeDocument().addObject("Part::MultiFuse","LEFT_OUTER_WING_FUSION")
#FreeCAD.activeDocument().LEFT_OUTER_WING_FUSION.Shapes = [FreeCAD.activeDocument().LEFT_WINGLET,FreeCAD.activeDocument().OUTER_WING_2_L,FreeCAD.activeDocument().OUTER_WING_1_L]
#FreeCAD.ActiveDocument.recompute()
#
##LEFT WING + CENTREBODY FUSION
#FreeCAD.activeDocument().addObject("Part::MultiFuse","LEFT_WING_FUSION")
#FreeCAD.activeDocument().LEFT_WING_FUSION.Shapes = [FreeCAD.activeDocument().LEFT_OUTER_WING_FUSION,FreeCAD.activeDocument().CENTREBODY_FUSION_L]
#FreeCAD.ActiveDocument.recompute()
#
#
##MIRROR TO CREATE RIGHT WING
#__doc__=FreeCAD.ActiveDocument
#__doc__.addObject("Part::Mirroring",'RIGHT_WING_FUSION')
#__doc__.ActiveObject.Source=__doc__.getObject("LEFT_WING_FUSION")
#__doc__.ActiveObject.Label=u"RIGHT_WING_FUSION"
#__doc__.ActiveObject.Normal=(0,0,1)
#__doc__.ActiveObject.Base=(0,0,0)
#del __doc__


###MIRROR TO CREATE RIGHT CENTRE BODY & WING
##
##__doc__=FreeCAD.ActiveDocument
##__doc__.addObject("Part::Mirroring",'CENTREBODY_FUSION_R')
##__doc__.ActiveObject.Source=__doc__.getObject("CENTREBODY_FUSION_L")
##__doc__.ActiveObject.Label=u"CENTREBODY_FUSION_R"
##__doc__.ActiveObject.Normal=(0,0,1)
##__doc__.ActiveObject.Base=(0,0,0)
##del __doc__
###__doc__=FreeCAD.ActiveDocument
##__doc__.addObject("Part::Mirroring",'WING_FUSION_R')
##__doc__.ActiveObject.Source=__doc__.getObject("WING_FUSION_L")
##__doc__.ActiveObject.Label=u"WING_FUSION_R"
##__doc__.ActiveObject.Normal=(0,0,1)
##__doc__.ActiveObject.Base=(0,0,0)
##del __doc__
##
#####FUSE BWB
###
####__objs__=[]
####__objs__.FreeCADend(FreeCAD.ActiveDocument.getObject("BWB_FUSION"))
####import Mesh
####Mesh.export(__objs__,u"C:\Users\Alex\Documents\University of strathclyde\4th year\me420 dissertation\freecad\BWB.stl")
####del __objs__
####FreeCAD.ActiveDocument.recompute()
###
##
##
