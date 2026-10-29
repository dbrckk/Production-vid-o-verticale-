"""Continuous scene-specific cinematic animation layers.

All positions derive from time, not pre-rendered slide images. The six acts
progress from emergence to mechanisms, consequences, and final reveal.
"""
from __future__ import annotations
import math
from PIL import ImageDraw

TAU=math.tau
CYAN=(96,238,202)
GOLD=(251,188,104)
BLUE=(117,160,246)

def ease(x):
    x=max(0.,min(1.,x))
    return x*x*(3-2*x)

def animate(p,im,t,scene_index,phase):
    d=ImageDraw.Draw(im,"RGBA")
    cx,cy=288,574
    q=ease(phase)
    act=scene_index%6
    if act==0:
        # A visible burst of objects from a common origin.
        for i in range(34):
            angle=i*TAU/34+math.sin(i*7.3)*.1
            radius=20+q*(70+(i*19)%155)
            x=cx+radius*math.cos(angle)
            y=cy+radius*.8*math.sin(angle)
            p.circle(d,x,y,1.8+i%3,(*(CYAN if i%3 else GOLD),int(220*(1-.35*q))))
    elif act==1:
        # A live scanning cross-section: light physically travels over the subject.
        scan=90+410*q
        p.line(d,[(scan,370),(scan,773)],(*CYAN,105),2)
        for i in range(20):
            x=90+i*21
            y=440+120*math.sin(i*.3+t*.65)
            if x<=scan:
                p.circle(d,x,y,3,(*GOLD,200))
        p.line(d,[(90,783),(scan,783)],(*CYAN,170),3)
    elif act==2:
        # Cause-and-effect waves propagate outward.
        for i in range(5):
            r=20+((t*.27+i/5)%1)*230
            opacity=int(150*(1-r/255))
            p.circle(d,cx,cy,r,None,(*BLUE,max(0,opacity)),2)
        for i in range(10):
            x=80+i*44
            y=700-160*ease(max(0,q-i*.065))
            p.circle(d,x,y,4,(*GOLD,195))
    elif act==3:
        # Moving trajectories and an animated object that follows the path.
        path=[(82,710),(155,645),(228,682),(300,545),(379,572),(490,420)]
        p.line(d,path,(*BLUE,110),3)
        section=q*(len(path)-1)
        j=min(len(path)-2,int(section))
        k=section-j
        x=path[j][0]*(1-k)+path[j+1][0]*k
        y=path[j][1]*(1-k)+path[j+1][1]*k
        p.glow_disc(im,x,y,8,GOLD)
        p.circle(d,x,y,13,None,(*CYAN,180),2)
    elif act==4:
        # Animated comparison: elements grow in sequence, rather than appear.
        for i in range(7):
            x=91+i*65
            amplitude=65+(i*41)%180
            height=amplitude*ease((q-i*.09)*2.2)
            p.line(d,[(x,750),(x,750-height)],(*(CYAN if i%2 else GOLD),190),9)
            p.circle(d,x,750-height,5,(*GOLD,225))
    else:
        # Final reveal: converging light rays, a rotating orbital indicator.
        for i in range(24):
            a=i*TAU/24+t*.3
            r=190-90*q
            x=cx+r*math.cos(a)
            y=cy+r*math.sin(a)
            p.line(d,[(x,y),(cx+25*math.cos(a),cy+25*math.sin(a))],(*CYAN,int(28+65*q)),2)
        a=t*.8
        p.circle(d,cx+108*math.cos(a),cy+108*math.sin(a),7,(*GOLD,230))
