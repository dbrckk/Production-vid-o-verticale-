"""Story-driven visual metaphors for topics without a curated physical simulation.

Six distinct, continuously animated diagrams are selected by the source
storyboard's visual tag. They never display invented dates, figures or claims.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

TAU=math.tau
MINT=(101,238,205)
GOLD=(252,196,113)
BLUE=(115,166,238)
WHITE=(236,244,255)

VISUAL_TAGS=frozenset(("focus","globe","timeline","network","compare","question"))


def _dot(p,d,x,y,r,color=MINT,alpha=230):
    p.circle(d,x,y,r,(*color,alpha))


def _line(p,d,pts,color=BLUE,width=2.5,alpha=160):
    p.line(d,pts,(*color,alpha),width)


def draw(p,im,visual:str,t:float,phase:float,scene_index:int):
    """Render one six-act semantic diagram; time changes its geometry."""
    d=ImageDraw.Draw(im,"RGBA")
    q=max(0.,min(1.,phase))
    smooth=q*q*(3-2*q)
    cx,cy=288,570
    if visual=="focus":
        # Reveal the concept: expanding selection rings and radial evidence.
        for j in range(5):
            radius=42+(j+1)*30+4*math.sin(t*.8+j)
            p.circle(d,cx,cy,radius,None,(*BLUE,max(20,112-18*j)),1.6)
        p.glow_disc(im,cx,cy,41,GOLD)
        for j in range(24):
            a=j*TAU/24+t*.22
            radius=81+smooth*102+(j%3)*8
            _dot(p,d,cx+radius*math.cos(a),cy+.85*radius*math.sin(a),
                 1.7+(j%3)*.4, MINT if j%3 else GOLD,150)
        for i in range(3):
            angle=i*TAU/3+t*.12
            _line(p,d,[(cx+63*math.cos(angle),cy+63*math.sin(angle)),
                       (cx+147*math.cos(angle),cy+147*math.sin(angle))],
                  GOLD,3,130)

    elif visual=="globe":
        # The topic's larger context. Generic topics are never presented as
        # physical planets unless the narration itself explicitly says Earth.
        for r in (84,139,190):
            p.circle(d,cx,cy,r,None,(*BLUE,105),1.7)
        for j in range(11):
            a=j*TAU/11+t*.3
            radius=100+40*math.sin(j*3.7+t*.15)
            x=cx+radius*math.cos(a)
            y=cy+.73*radius*math.sin(a)
            _dot(p,d,x,y,5.5,MINT if j%3 else GOLD,225)
            if j%2==0:
                _line(p,d,[(cx,cy),(x,y)],BLUE,2,85)
        p.glow_disc(im,cx,cy,24,GOLD)
        a=t*.5
        p.circle(d,cx+194*math.cos(a),cy+132*math.sin(a),9,(*GOLD,235))
        # Clockwise arc is a visual camera-guide, not a factual orbit.
        _line(p,d,[(cx-165,cy+136),(cx-126,cy+161),(cx-70,cy+181)],MINT,2,105)

    elif visual=="timeline":
        # Animated process beats; no fictitious years or numeric values.
        start_x=63
        stations=[(start_x+112*i,554+39*math.sin(i*.65)) for i in range(5)]
        _line(p,d,stations,BLUE,4,145)
        for j,(x,y) in enumerate(stations):
            filled=smooth*4>=j
            p.circle(d,x,y,19,(24,42,60,220),(*(MINT if filled else BLUE),240),3)
            if filled:_dot(p,d,x,y,6,GOLD,245)
            if j:
                _line(p,d,[(x,y-35),(x,y-66)],BLUE,1.5,80)
        position=smooth*4
        i=min(3,int(position))
        f=position-i
        x=stations[i][0]*(1-f)+stations[i+1][0]*f
        y=stations[i][1]*(1-f)+stations[i+1][1]*f
        p.glow_disc(im,x,y,7,GOLD)
        for j in range(17):
            x=84+j*25
            y=722+12*math.sin(t*1.4+j*.5)
            _dot(p,d,x,y,1.8,BLUE,85)

    elif visual=="network":
        nodes=[]
        for j in range(9):
            a=j*TAU/9+t*.06
            radius=134+14*math.sin(j*1.9+t*.8)
            nodes.append((cx+radius*math.cos(a),cy+radius*math.sin(a)*.78))
        for j,pos in enumerate(nodes):
            for other in (nodes[(j+1)%9],nodes[(j+3)%9]):
                _line(p,d,[pos,other],BLUE,1.8,95)
                progress=(t*.28+j*.12)%1
                x=pos[0]*(1-progress)+other[0]*progress
                y=pos[1]*(1-progress)+other[1]*progress
                _dot(p,d,x,y,2.7,GOLD,215)
        for j,(x,y) in enumerate(nodes):
            p.glow_disc(im,x,y,5,MINT if j%3 else GOLD)
        p.circle(d,cx,cy,34,(19,70,77,220),(*MINT,215),2.6)
        _line(p,d,[(cx-12,cy),(cx+12,cy)],WHITE,3,215)

    elif visual=="compare":
        # Two comparable forms without misleading fabricated bar magnitudes.
        for side,base in ((0,168),(1,405)):
            p.circle(d,base,563,97,None,(*(MINT if side else BLUE),140),2.4)
            r=60+23*math.sin(t*.55+side*1.4)
            for j in range(7):
                angle=j*TAU/7+t*(.5 if side else -.5)
                x=base+r*math.cos(angle)
                y=563+r*.7*math.sin(angle)
                _dot(p,d,x,y,5, GOLD if side else MINT,200)
            p.circle(d,base,563,32,(*(MINT if side else BLUE),100),
                     (*(MINT if side else BLUE),210),2)
        _line(p,d,[(288,440),(288,704)],BLUE,1.6,85)
        a=(math.sin(t*1.9)+1)/2
        for j in range(7):
            x=238+j*16
            y=745-30*math.sin(j*.6+t*.5)
            _dot(p,d,x,y,2+(j%2),GOLD,round(75+80*a))

    elif visual=="question":
        p.glow_disc(im,cx,cy,75,GOLD)
        p.circle(d,cx,cy,114,None,(*MINT,165),2.5)
        for j in range(27):
            a=j*TAU/27+t*.22
            radius=164+28*math.sin(t*.7+j*.45)
            x=cx+radius*math.cos(a)
            y=cy+radius*.8*math.sin(a)
            _dot(p,d,x,y,2.2,MINT if j%2 else GOLD,120+(j%3)*33)
        # A dynamic question mark is a visual prompt, not an unsupported claim.
        p.text(d,"?",cx,cy,137,(*WHITE,248),bold=True)
        span=130*smooth
        _line(p,d,[(cx-span,759),(cx+span,759)],GOLD,4,150)

    else:
        raise ValueError("Unknown generic storyboard visual: "+str(visual))
