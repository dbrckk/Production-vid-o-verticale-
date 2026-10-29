"""Six genuinely distinct 2D volcanic explanations.

The subject is the same volcano, but geometry, movement and lighting change
with the narrated physical process. Stages are 0 magma storage, 1 gas
pressure, 2 rock fractures, 3 eruption, 4 lava flow, and 5 cooling.
No static imagery is moved around as a slide.
"""
from __future__ import annotations

import math
from PIL import ImageDraw

AMBER=(255,196,100)
LAVA=(249,117,57)
TEAL=(106,229,210)
ASH=(149,147,162)


def clamp(v):
    return max(0.0,min(1.0,float(v)))


def ease(v):
    v=clamp(v)
    return v*v*(3-2*v)


def _ellipse(p,d,cx,cy,rx,ry,fill,outline=None,width=1):
    x0,y0=p.p(cx-rx,cy-ry)
    x1,y1=p.p(cx+rx,cy+ry)
    d.ellipse((x0,y0,x1,y1),fill=fill,outline=outline,
              width=max(1,round(width*p.s)))


def draw(p,im,t,scene_index,phase):
    from subject_illustrations import volcanic_structure

    stage=min(5,max(0,int(scene_index)))
    q=ease(phase)
    volcanic_structure(p,im,t,stage)
    d=ImageDraw.Draw(im,"RGBA")

    if stage==0:
        # Cutaway of the magma reservoir, with density-driven convection and
        # a stationary sealed conduit. The scene is deliberately NOT erupting.
        _ellipse(p,d,288,750,103,60,(112,48,52,244),(240,147,86,225),3.2)
        _ellipse(p,d,288,752,81,43,(189,70,52,230),(255,182,91,165),1.8)
        _ellipse(p,d,288,759,48,23,(245,137,62,205))
        for j in range(30):
            angle=j*math.tau/30+t*(.35+(j%4)*.04)
            radius=19+(j*17%64)
            x=288+radius*math.cos(angle)
            y=752+.49*radius*math.sin(angle)
            p.circle(d,x,y,2.1+(j%3)*.35,(*AMBER,130+j%3*27))
        p.line(d,[(288,690),(288,617),(286,550)],(126,67,68,245),13)
        p.line(d,[(288,690),(288,617),(286,550)],(240,117,64,170),4)
        for j in range(6):
            a=(t*.55+j)*math.tau/6
            x=288+76*math.cos(a);y=751+31*math.sin(a)
            p.circle(d,x,y,3,(*AMBER,190))

    elif stage==1:
        # Dissolved gases expand within a magma chamber as overburden
        # pressure evolves. Upward flux is encoded by moving bubbles.
        pressure=60+22*math.sin(t*.65)
        _ellipse(p,d,288,741,100,62,(128,54,50,240),(255,162,75,240),3)
        _ellipse(p,d,288,745,75,40,(227,103,55,217))
        _ellipse(p,d,288,741,pressure+42,pressure*.70+40,None,(253,164,90,101),2)
        for j in range(18):
            ascent=(t*(.16+j%4*.027)+j*.18)%1
            x=248+(j*31%81)+12*math.sin(ascent*6+j)
            y=770-214*ascent
            if y<530:
                continue
            radius=2.5+(j%4)*1.5+5*ascent
            p.circle(d,x,y,radius,(228,132,73,46),(250,207,123,176),1.3)
        for left,right in ((92,224),(484,353)):
            y=665
            p.line(d,[(left,y),(right,y-20)],(*AMBER,187),3)
            tip=(right,y-20)
            direction=1 if right>left else -1
            p.line(d,[tip,(right-direction*13,y-33)],(*AMBER,180),2.5)
            p.line(d,[tip,(right-direction*16,y-11)],(*AMBER,180),2.5)

    elif stage==2:
        # The fracture actually advances through the cone, with magma
        # packets moving from a chamber into the opening fault.
        _ellipse(p,d,288,752,93,56,(123,52,57,236),(246,159,95,205),2.6)
        crack=[
            (290,748),(297,707),(281,674),(298,638),
            (280,609),(291,572),(280,538),
        ]
        limit=1+int(q*(len(crack)-1))
        visible=crack[:max(2,limit)]
        p.line(d,visible,(105,38,42,235),14)
        p.line(d,visible,(*LAVA,232),6.2)
        p.line(d,visible,(*AMBER,235),2.8)
        for j in range(16):
            progress=(t*.22+j/16)%1
            index=min(len(crack)-2,int(progress*(len(crack)-1)))
            fraction=progress*(len(crack)-1)-index
            x=crack[index][0]*(1-fraction)+crack[index+1][0]*fraction
            y=crack[index][1]*(1-fraction)+crack[index+1][1]*fraction
            if progress<=q:
                p.circle(d,x,y,2.5,(*AMBER,224))
        # Short microfractures branch away from the advancing main fault.
        for j in range(5):
            activation=ease(q*1.5-j*.22)
            if activation==0:continue
            yy=700-j*34
            direction=-1 if j%2 else 1
            spread=30*activation
            p.line(d,[(288,yy),(288+direction*spread,yy-12*activation)],
                   (251,153,93,round(170*activation)),2.3)

    elif stage==3:
        # Explosive column: ash volume expands with buoyancy, rocks follow
        # ballistic trajectories, and seismic ripples spread from the vent.
        for j in range(28):
            age=(t*.44+j*.27)%3.0
            px=287+math.sin(age*.95+j*2.7)*(11+age*29)
            py=516-age*100+13*math.sin(j*.93)
            radius=10+age*16+(j%3)*3
            p.circle(d,px,py,radius,(95+(j%3)*8,84,91,round(86*(1-age/4))))
        for j in range(55):
            age=(t*.72+j*.143)%2.45
            velocity=100*math.sin(j*2.399)
            px=288+velocity*age*.7
            py=523-166*age+50*age*age
            if 240<py<816:
                p.circle(d,px,py,1.7+(j%4)*.48,
                         (255,156+(j%3)*23,80,round(240*(1-age/3))))
        for j in range(4):
            radius=20+((t*.32+j/4)%1)*125
            p.circle(d,288,530,radius,None,(255,183,108,round(85*(1-radius/165))),2.4)

    elif stage==4:
        # Slow, persistent effusive flow is brighter near its moving front
        # and darker in cooled regions; no unnecessary explosive particles.
        flow=[
            [(287,527),(306,567),(337,634),(374,696),(407,758),(459,811)],
            [(287,527),(273,578),(249,633),(223,693),(188,761)],
        ]
        for j,pts in enumerate(flow):
            front=(t*.12+j*.25)%1
            position=front*(len(pts)-1)
            segment=min(len(pts)-2,int(position))
            frac=position-segment
            x=pts[segment][0]*(1-frac)+pts[segment+1][0]*frac
            y=pts[segment][1]*(1-frac)+pts[segment+1][1]*frac
            p.circle(d,x,y,9,(*LAVA,186))
            p.circle(d,x,y,4,(*AMBER,249))
            for k in range(10):
                age=(t*.24+k*.19+j*.13)%1
                a=min(len(pts)-2,int(age*(len(pts)-1)))
                f=age*(len(pts)-1)-a
                xx=pts[a][0]*(1-f)+pts[a+1][0]*f
                yy=pts[a][1]*(1-f)+pts[a+1][1]*f
                p.circle(d,xx,yy,1.7,(254,154,72,192))

    else:
        # After eruption, hot rock cools while steam slowly rises. The magma
        # chamber is no longer erupting; the visible lava is subdued.
        for j in range(29):
            age=(t*.16+j*.127)%2.6
            x=(173 if j%2 else 408)+22*math.sin(j*2.1+age*.7)
            y=704-age*67
            radius=6+age*3+(j%4)
            p.circle(d,x,y,radius,(134,139,153,round(78*(1-age/3))))
        for j in range(24):
            x=93+j*17
            y=785+6*math.sin(x*.028+t*.23)
            warmth=(.5+.5*math.sin(t*.31+j*.8))
            p.circle(d,x,y,1.4+(j%3)*.35,
                     (200,131,91,round(48+58*warmth)))
