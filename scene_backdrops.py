"""Original premium 2D science environments: cached light, depth and motion.

Rendered with Pillow/NumPy, never online stock images, 3D or paid services.
Heavy color gradients are composed *once per video* and reused across all
frames. Foreground physics and subtitles remain separate layers.
"""
from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw

PALETTES={
    "ocean": ((4,32,48),(4,87,102),(15,18,46)),
    "earthquake": ((29,31,46),(25,64,75),(14,19,41)),
    "volcano": ((34,19,35),(101,47,36),(21,16,36)),
    "space": ((16,16,40),(42,33,76),(11,13,33)),
    "weather": ((13,32,51),(32,72,101),(16,27,56)),
    "biology": ((12,35,39),(25,72,59),(12,26,41)),
}


def environment(p,category: str) -> Image.Image:
    """Return an opaque RGBA scene background, cached at final resolution."""
    if category not in PALETTES:
        return p.base.copy()
    cache=getattr(p,"_cinematic_backdrops",None)
    if cache is None:
        cache={}
        p._cinematic_backdrops=cache
    if category in cache:
        return cache[category].copy()

    w,h=p.width,p.height
    x=np.linspace(0.,1.,w,dtype=np.float32)[None,:]
    y=np.linspace(0.,1.,h,dtype=np.float32)[:,None]
    top,middle,bottom=PALETTES[category]
    depth=np.clip((y-.10)/.79,0,1)
    upper=np.clip(depth/.52,0,1)
    lower=np.clip((depth-.52)/.48,0,1)
    arr=np.empty((h,w,3),dtype=np.float32)
    for c in range(3):
        arr[:,:,c]=(top[c]*(1-upper)+middle[c]*upper)*(1-lower)+bottom[c]*lower
    # Diffuse volumetric lighting follows the physical environment.
    if category=="ocean":
        light=np.exp(-((x-.35-.15*y)/(.16+.15*y))**2)*(1-np.clip(y,0,1))**1.4
        light+=.45*np.exp(-((x-.80+.14*y)/(.10+.14*y))**2)*(1-y)**1.6
        cloud=.5+.5*np.sin(13*x+8*y)*np.sin(17*y-3*x)
        arr[:,:,0]+=4*light
        arr[:,:,1]+=29*light+2*cloud
        arr[:,:,2]+=31*light
    elif category=="earthquake":
        fault=np.exp(-((x-.5)/(.17+.10*y))**2)*np.exp(-((y-.67)/.29)**2)
        strata=(np.sin(y*112+3*np.sin(x*10))*np.sin(y*41+x*6))*.5+.5
        arr[:,:,0]+=20*fault+strata*3
        arr[:,:,1]+=10*fault+strata*2
        arr[:,:,2]+=3*fault
    elif category=="volcano":
        glow=np.exp(-((x-.51)/(.18+.12*y))**2-((y-.59)/.24)**2)
        smoke=(np.sin(13*x+14*y)*np.sin(7*y-17*x)+1)*.5
        arr[:,:,0]+=44*glow+6*smoke
        arr[:,:,1]+=13*glow+4*smoke
        arr[:,:,2]+=3*glow+8*smoke
    elif category=="space":
        nebula=np.exp(-((x-.45-.10*np.sin(y*8))/.29)**2-((y-.51)/.29)**2)
        arr[:,:,0]+=17*nebula;arr[:,:,1]+=5*nebula;arr[:,:,2]+=31*nebula
    elif category=="weather":
        sun=np.exp(-((x-.26)/.25)**2-((y-.33)/.29)**2)
        arr[:,:,0]+=18*sun;arr[:,:,1]+=27*sun;arr[:,:,2]+=33*sun
    elif category=="biology":
        leafglow=np.exp(-((x-.51)/.30)**2-((y-.57)/.26)**2)
        arr[:,:,1]+=24*leafglow;arr[:,:,2]+=12*leafglow

    # Strong, soft lens-vignette is baked only once (not per video frame).
    vignette=np.clip(1-.35*(((x-.50)/.63)**2+((y-.51)/.7)**2),.48,1)
    arr*=vignette[:,:,None]
    cache[category]=Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")
    return cache[category].copy()


def _stroke(p,d,coords,fill,width=1):
    p.line(d,coords,fill,width)


def add_parallax(p,im,category:str,t:float,scene_index:int):
    """Meaningful animated atmospheric elements beneath the focal diagram.

    All movement is analytic in continuous time, so adjacent 60 FPS frames are
    smooth; random coordinates are deterministic per element.
    """
    if category not in PALETTES:
        return
    d=ImageDraw.Draw(im,"RGBA")
    if category=="ocean":
        # Surface-caustic streaks and a distant, slowly swaying kelp field.
        for j in range(11):
            origin=36+j*52
            phase=t*(.35+.05*(j%3))+j*1.7
            x=origin+17*math.sin(phase)
            points=[(x+12*math.sin(phase+v*.019),845-v) for v in range(0,154,13)]
            _stroke(p,d,points,(30,117,113,95),1.9)
            for v in (54,102):
                sway=12*math.sin(phase+v*.019)
                p.circle(d,x+sway+8,845-v,5,(37,123,104,80))
        for j in range(13):
            x=45+(j*57+t*(3+j%4))%495
            y=410+32*math.sin(t*.45+j*2)
            _stroke(p,d,[(x,y),(x+21,y-2)],(110,212,205,37),1.2)
    elif category=="volcano":
        # Atmospheric ash billows rise from a coherent eruptive vent.
        for j in range(19):
            age=(t*.34+j*.15)%2.5
            x=288+57*math.sin(age*1.6+j*2.4)*(.5+age*.4)
            y=526-age*105+14*math.sin(j*1.7)
            r=8+age*14+(j%4)*3
            alpha=max(17,int(70*(1-age/3.2)))
            p.circle(d,x,y,r,(76+int(age*9),73,83,alpha))
        for j in range(13):
            x=31+j*45
            shimmer=.5+.5*math.sin(t*.42+j*.8)
            _stroke(p,d,[(x,827),(x+14,808)],(214,102,63,round(29+35*shimmer)),1.2)
    elif category=="earthquake":
        # Stratigraphic sediment veins and gentle mantle convection remain
        # subordinate to the main fault illustration.
        for j in range(5):
            y=797+j*28
            points=[(x,y+5*math.sin(x*.019+j*.9+t*.055)) for x in range(20,560,14)]
            _stroke(p,d,points,(69,120,130,50+j*5),1.5)
        for j in range(10):
            a=t*.22+j*math.tau/10
            x=288+205*math.cos(a)
            y=855+22*math.sin(a)
            p.circle(d,x,y,1.5,(240,176,110,85))
    elif category=="space":
        for j in range(65):
            x=24+(j*123)%528+t*(.09+.04*(j%3))
            y=339+(j*211)%425
            brightness=45+round(50*(.5+.5*math.sin(t*.7+j*1.3)))
            p.circle(d,x,y,.7+(j%3)*.3,(173,185,242,brightness))
    elif category=="weather":
        for j in range(7):
            offset=(t*(10+j*2)+j*85)%670-48
            y=354+j*41
            _stroke(p,d,[(offset,y),(offset+38,y-8),(offset+81,y-4)],(136,191,220,45),2.0)
    elif category=="biology":
        for j in range(19):
            a=j*math.tau/19+t*.2
            r=139+9*math.sin(t*.67+j)
            p.circle(d,288+r*math.cos(a),565+.78*r*math.sin(a),2.0,(110,217,172,70))
