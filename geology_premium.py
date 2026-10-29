"""Premium, physically motivated 2D geologic artwork.

No stock textures, paid imagery, 3D, or static slide assets: mineral grains,
layered rock, displaced strata, and stress glints are generated as vector
geometry. Coordinates are the established 576 x 1024 painting space.
"""
from __future__ import annotations
import math
from PIL import ImageDraw

TAU=math.tau
LIME=(107,235,206)
TEAL=(58,161,165)
AMBER=(253,188,98)
BLUE=(122,164,225)
DUST=(174,197,208)


def _polygon(p,d,points,color):
    d.polygon([p.p(x,y) for x,y in points],fill=color)


def mineral_plate(p,im,d,x0,x1,shift,tint,t):
    """A lithosphere cross-section with non-flat wavy rock stratification.

    The strata are *not* noise translated as slides: each contour responds to
    the plate displacement while revealing continuous deep-earth layers.
    """
    y0=590+shift
    _polygon(p,d,[(x0,y0),(x1,y0+3),(x1,782),(x0,782)],tint)
    # Layers give geology visible depth. Their highlights are restrained
    # enough that earthquake arrows and subtitles retain visual priority.
    hues=[
        (44,99,108,190),(30,83,106,197),(57,76,109,212),
        (63,64,103,220),(31,55,92,222)
    ] if tint[0]<55 else [
        (93,79,106,195),(79,73,109,205),(68,75,113,218),
        (66,64,101,222),(47,52,91,224)
    ]
    for band,(level,color) in enumerate(zip((608,640,672,709,744),hues)):
        amp=2.8+band*.3
        strip=[]
        for j in range(13):
            x=x0+(x1-x0)*j/12
            y=level+shift*(.85-band*.075)+amp*math.sin(j*.51+band*1.3+t*.08)
            strip.append((x,y))
        _polygon(p,d,strip+[(x1,782),(x0,782)],color)
        p.line(d,strip,(*(LIME if band%2==0 else BLUE),52+10*(band%2)),1.4)
    # Sediment grains and internal microfractures, deterministic and bounded
    # strictly to their host rock polygon.
    span=x1-x0
    for j in range(46):
        rx=x0+12+(j*67%max(13,int(span-24)))
        ry=612+(j*43%152)+shift*.28
        if rx>=x1-8 or ry>=777:continue
        r=.65+(j%4)*.31
        p.circle(d,rx,ry,r,(*(AMBER if j%9==0 else DUST),48+(j%3)*22))
        if j%8==0:
            p.line(d,[(rx-5,ry+2),(rx,ry-3),(rx+4,ry+1)],
                   (*BLUE,72),1.1)
    mineral_depth(p,d,x0,x1,y0,shift,t)
    # Mineral surface has a fine double rim and a moving low-contrast gleam.
    p.line(d,[(x0,y0),(x1,y0+3)],(*LIME,235),3.6)
    p.line(d,[(x0,y0+7),(x1,y0+10)],(*AMBER,53),1.8)
    for j in range(12):
        x=x0+9+((j*49+t*4.6)%(max(15,span-18)))
        y=y0+(j%3)*1.9
        p.circle(d,x,y,1.2,(*LIME,90))



def mineral_depth(p,d,x0,x1,y0,shift,t):
    """Sediment grain parallax and stratigraphic microstructure.

    Every geological plate gets layered fault hatching and illuminated
    sediment seams. All detail is deterministic and smoothly animated.
    """
    span=x1-x0
    if span<30:
        return
    for band in range(4):
        level=625+band*37+shift*(.82-band*.12)
        coords=[]
        for j in range(31):
            x=x0+4+(span-8)*j/30
            y=level+2.8*math.sin(j*.36+band*1.6+t*.055)
            coords.append((x,y))
        p.line(d,coords,(*((110,212,204) if band%2==0 else (191,162,129)),46+band*8),.9)
        for k in range(9):
            x=x0+9+((k*79+band*31)%(max(10,int(span)-18)))
            y=level+6+((k*13+band*7)%17)
            p.line(d,[(x-2,y+2),(x+3,y-1)],(*DUST,38+(k%3)*16),.8)
    # Tiny, asymmetrically lit crystal inclusions create geological depth.
    for k in range(20):
        x=x0+9+((k*97+19)%(max(10,int(span)-18)))
        y=611+(k*41%150)+shift*.30
        r=.7+(k%3)*.32
        p.circle(d,x,y,r,(*((225,191,140) if k%5==0 else (117,186,185)),75))
        if k%4==0:
            p.line(d,[(x-1.5,y-1.5),(x+2,y+1)],(*DUST,52),.8)


def stress_highlights(p,im,d,t,scene,phase):
    """Heat and luminous fracture on a fault, never gratuitous neon sparks."""
    if scene not in (1,2):return
    intensity=(.25+phase*.64) if scene==1 else (.85*math.exp(-1.6*phase))
    for k in range(9):
        y=548+k*24
        x=285+6*math.sin(k*.78+t*.48)
        width=5+14*intensity*math.sin(k*.72+1.9)**2
        p.line(d,[(x-width,y-4),(x,y+6),(x+width*.5,y+16)],
               (*AMBER,round(34+111*intensity)),2.0)
    if scene==2:
        # Light pulses travel *from* the rupture, not uniformly from the sky.
        for k in range(6):
            r=18+(phase*.8+k/6)%1*96
            opacity=round(70*(1-(r-18)/100))
            p.circle(d,287,601,r,None,(*AMBER,max(0,opacity)),1.3)


def building_facades(p,im,d,t,phase):
    """Window reflections, rooflines and foundations move with each building."""
    for side in (0,1):
        x=169 if side==0 else 410
        amp=(2.8 if side==0 else 10)*math.sin(t*12.4+side*1.2)
        top=485 if side==0 else 539
        left=x-53+amp
        right=x+53+amp
        # Top is physically attached to the existing building geometry.
        p.line(d,[(left-4,top-8),(right+4,top-8)],(*DUST,185),3)
        p.line(d,[(left+9,top+4),(left+9,691)],(*BLUE,73),2)
        p.line(d,[(right-10,top+4),(right-10,691)],(*LIME,67),2)
        row_count=5 if side==0 else 4
        for row in range(row_count):
            y=top+27+row*29
            if y>681:continue
            for col in range(3):
                xx=x-30+col*30+amp
                a=p.p(xx-8,y-7)
                b=p.p(xx+8,y+7)
                d.rounded_rectangle((*a,*b),radius=max(1,round(p.s*2)),
                                    fill=(108,200,208,97+((row+col)%2)*40),
                                    outline=(*LIME,78),width=max(1,round(p.s)))
                p.line(d,[(xx,y-7),(xx,y+7)],(*DUST,78),.8)
        # A clear foundation ties the building to the soil motion.
        p.line(d,[(left-9,703),(right+9,703)],(*(AMBER if side else LIME),110),3.2)




def building_response(p,d,bx,base_y,height,t,amplitude,seed=0):
    """Draw a flexible frame building, with a continuous damped shear response.

    Each floor has a different lateral displacement (zero at the foundation,
    maximum at the roof), unlike a rigid rectangular block translated as one.
    The illustration shows qualitative relative shaking, not a measured model.
    """
    floors=5 if height>=200 else 4
    width=100
    def floor_shift(level):
        fraction=level/floors
        # Smooth time-dependent structural displacement with mild harmonic
        # response; zero displacement at the soil/foundation interface.
        return amplitude*fraction**1.55*(
            math.sin(t*(5.4+seed*.27)+seed*.8)
            +.22*math.sin(t*(10.1+seed*.31)+seed*1.7)
        )
    left=bx-width/2
    right=bx+width/2
    levels=[]
    for k in range(floors+1):
        y=base_y-height*k/floors
        dx=floor_shift(k)
        levels.append((y,dx))
    # Lit sidewall follows the actual deforming structure rather than
    # a flat moving rectangle.
    poly=[(left+dx,y) for y,dx in levels]
    poly += [(right+dx,y) for y,dx in reversed(levels)]
    _polygon(p,d,poly,(29,56,77,225))
    for k in range(floors):
        y0,dx0=levels[k]
        y1,dx1=levels[k+1]
        p.line(d,[(left+dx0,y0),(left+dx1,y1)],(*BLUE,185),2.2)
        p.line(d,[(right+dx0,y0),(right+dx1,y1)],(*BLUE,185),2.2)
        # Interior bracing illustrates the load path through each storey.
        p.line(d,[(left+dx0,y0),(right+dx1,y1)],(*TEAL,66),1)
        p.line(d,[(right+dx0,y0),(left+dx1,y1)],(*TEAL,66),1)
        p.line(d,[(left+dx1,y1),(right+dx1,y1)],(*LIME,175),2.0)
        window_y=(y0+y1)/2
        window_dx=(dx0+dx1)/2
        for column in (-1,0,1):
            x=bx+column*26+window_dx
            p.circle(d,x,window_y,4.0,(*((241,187,114) if (k+column+seed)%4==0 else (107,207,204)),168))
    yroof,roofshift=levels[-1]
    p.line(d,[(left-5+roofshift,yroof),(right+5+roofshift,yroof)],(*LIME,220),3.1)
    # Foundation anchors stay fixed to the soil.
    p.line(d,[(left-12,base_y+2),(right+12,base_y+2)],(*DUST,180),2.4)
    return roofshift


def seismic_wavefield(p,im,t,phase):
    """Moving P/S wave trains, refracted rays and attenuating ground motion.

    A physically motivated editorial visualization: wavefronts expand from
    one hypocentre, weaker transverse trains lag the compressional waves,
    and short coherent surface displacement follows their arrival.
    """
    d=ImageDraw.Draw(im,"RGBA")
    cx,cy=280,605
    # Continuous radial fronts with an offset arrival speed for the S wave.
    for family,speed,color in ((0,130,LIME),(1,77,BLUE)):
        for front in range(4):
            travel=(t*speed+front*96) % 460
            alpha=max(0,round(150*(1-travel/460)**1.35))
            if alpha<4:
                continue
            pts=[]
            for k in range(79):
                a=math.tau*k/78
                distortion=1+0.035*math.sin(5*a+t*.4+front)
                r=travel*distortion
                pts.append((cx+r*math.cos(a),cy+r*.70*math.sin(a)))
            p.line(d,pts,(*color,alpha),1.6 if family==0 else 1.2)
            # Light only the leading edge; no distracting generic neon rings.
            a=t*(.12 if family==0 else -.10)+front*1.6
            p.circle(d,cx+travel*math.cos(a),cy+.70*travel*math.sin(a),
                     2.2,(*color,min(190,alpha+30)))
    # Rock strata oscillate in place as a small amplitude travelling wave.
    for layer in range(4):
        y0=715+layer*31
        points=[]
        for j in range(62):
            x=38+j*8
            distance=abs(x-cx)
            arrival=(t*105-distance)
            envelope=max(0,1-abs(arrival-115)/180)
            dy=(5.0-layer*.65)*envelope*math.sin((distance-t*105)*.12)
            points.append((x,y0+dy))
        p.line(d,points,(*DUST,46+layer*11),1.0)

def earthquake_art(p,im,t,scene,phase):
    """Publish-ready detailing after the explanatory simulation draws its shapes."""
    d=ImageDraw.Draw(im,"RGBA")
    if scene in (0,1,2):
        stress_highlights(p,im,d,t,scene,phase)
    elif scene==4:
        building_facades(p,im,d,t,phase)
    elif scene==3:
        seismic_wavefield(p,im,t,phase)
        # Small travelling P-wave illumination runs above the surface.
        for j in range(21):
            x=70+j*22
            y=649+7*math.sin(x*.04)
            highlight=.5+.5*math.sin(t*2.9-j*.29)
            p.circle(d,x,y,1.2+1.7*highlight,(*LIME,round(36+94*highlight)))
    elif scene==5:
        # Trace illumination follows the analysis graph, not a HUD progress bar.
        xx=101+(t*.18%1)*374
        p.line(d,[(xx,460),(xx,720)],(*LIME,49),1.2)
