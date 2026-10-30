"""Six illustrated, continuously animated photosynthesis sequences.

All geometry is drawn at the native 9:16 render resolution from reference
576x1024 coordinates. This deliberately avoids repeating the same leaf shot
throughout the documentary.
"""
from __future__ import annotations

import math
from PIL import ImageDraw

TAU=math.tau
LEAF=(81,224,159)
MINT=(128,245,198)
LIME=(167,245,132)
SUN=(255,206,111)
SKY=(127,189,249)
WATER=(100,198,246)
INK=(22,75,65)
PALE=(231,250,239)


def line(p,d,points,color,width=2,alpha=200):
    p.line(d,points,(*color,int(alpha)),width)


def circle(p,d,x,y,r,color,alpha=210,outline=None):
    p.circle(d,x,y,r,(*color,int(alpha)),
             (*outline,190) if outline else None,1.4)


def glow(p,im,x,y,r,color):
    p.glow_disc(im,x,y,r,color)


def arrow(p,d,points,color,phase=0,width=3):
    line(p,d,points,color,width,170)
    if len(points)<2:
        return
    a,b=points[-2:]
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    tip=[(b[0]-11*math.cos(angle-.55),b[1]-11*math.sin(angle-.55)),
         b,(b[0]-11*math.cos(angle+.55),b[1]-11*math.sin(angle+.55))]
    line(p,d,tip,color,width,230)


def leaf(p,d,cx,cy,scale,t,angle=0):
    """Multi-veined botanical leaf that sways without swapping static images."""
    sway=3.5*math.sin(t*.8+cx*.025)
    def rot(x,y):
        a=angle+sway*.007
        return (cx+scale*(x*math.cos(a)-y*math.sin(a)),
                cy+scale*(x*math.sin(a)+y*math.cos(a)))
    edge=[]
    for j in range(41):
        a=math.pi*j/40
        x=92*math.cos(a)
        y=-55*math.sin(a)
        edge.append(rot(x,y))
    for j in range(40,-1,-1):
        a=math.pi*j/40
        edge.append(rot(92*math.cos(a),41*math.sin(a)))
    d.polygon([p.p(*v) for v in edge],fill=(28,113,78,226))
    line(p,d,edge+[edge[0]],LEAF,2.6,226)
    line(p,d,[rot(-86,0),rot(91,0)],MINT,2.7,175)
    for side in (-1,1):
        for k in range(1,7):
            x=-72+k*22
            tip=rot(x+17,side*(24+12*math.sin(math.pi*k/7)))
            line(p,d,[rot(x,0),tip],LEAF,1.2,105)
    # Small moving epidermis highlights, attached to the swaying blade.
    for k in range(11):
        x=-69+(k*37)%135
        y=(11+(k%4)*4)*(1 if k%2 else -1)
        xx,yy=rot(x,y)
        circle(p,d,xx,yy,1.3,MINT,48+(k%4)*20)


def sun(p,im,d,x,y,t):
    glow(p,im,x,y,30,SUN)
    circle(p,d,x,y,30,SUN,244)
    for k in range(16):
        a=TAU*k/16+t*.1
        q=36+2*math.sin(t*1.1+k)
        line(p,d,[(x+q*math.cos(a),y+q*math.sin(a)),
                  (x+(q+13)*math.cos(a),y+(q+13)*math.sin(a))],
             SUN,2.6,135)


def moving_beads(p,im,d,points,t,count,color,speed=.23,size=3.5):
    for k in range(count):
        u=(t*speed+k/max(1,count))%1
        at=u*(len(points)-1)
        i=min(len(points)-2,int(at))
        f=at-i
        x=points[i][0]*(1-f)+points[i+1][0]*f
        y=points[i][1]*(1-f)+points[i+1][1]*f
        circle(p,d,x,y,size,color,round(100+125*math.sin(math.pi*u)))
        if k%4==0:
            glow(p,im,x,y,2.1,color)


def molecules(p,d,x,y,kind,t=0,scale=1):
    if kind=="water":
        circle(p,d,x,y,4.3*scale,WATER,225)
        for a in (-.55,.55):
            circle(p,d,x+7*scale*math.sin(a),y+7*scale*math.cos(a),
                   2.6*scale,PALE,220)
    elif kind=="oxygen":
        for dx in (-4,4):
            circle(p,d,x+dx*scale,y,4*scale,SKY,222)
        line(p,d,[(x-2*scale,y-2*scale),(x+2*scale,y-2*scale)],PALE,1,140)
    else:
        circle(p,d,x-5*scale,y,3.6*scale,PALE,230)
        circle(p,d,x,y,4.8*scale,(170,183,201),225)
        circle(p,d,x+5*scale,y,3.6*scale,PALE,230)


def plant(p,d,t,soil=True):
    """Botanical branching stem; leaves rotate independently."""
    stem=[(291,735),(285,678),(292,616),(286,566),(293,503),(292,451)]
    line(p,d,stem,(92,193,124),8,235)
    line(p,d,[(290,728),(290,610),(290,513)],LIME,1.7,126)
    leaf(p,d,231,529,.75,t,-.58)
    leaf(p,d,357,603,.7,t,.6)
    leaf(p,d,258,448,.65,t,-.7)
    leaf(p,d,329,468,.55,t,.47)
    if soil:
        soil_y=731
        d.polygon([p.p(*q) for q in [(49,soil_y),(526,soil_y),
                  (526,846),(49,846)]],fill=(72,60,57,230))
        line(p,d,[(49,soil_y),(526,soil_y)],(184,141,110),3,230)
        for i in range(14):
            x=290+(i-7)*11
            yy=730+15+((i*23)%48)
            endpoint=x+(i-7)*10
            line(p,d,[(290,730),(x,yy),(endpoint,810+((i*11)%27))],
                 (171,157,106),1.2,136)


def sugar(p,d,x,y,t,scale=1):
    r=22*scale
    coords=[(x+r*math.cos(TAU*k/6+math.pi/6),
             y+r*math.sin(TAU*k/6+math.pi/6)) for k in range(6)]
    d.polygon([p.p(*pt) for pt in coords],fill=(50,128,88,190))
    line(p,d,coords+[coords[0]],LIME,2.5,230)
    for k in range(3):
        a=TAU*k/3+t*.12
        circle(p,d,x+9*scale*math.cos(a),y+9*scale*math.sin(a),
               2.2*scale,MINT,160)


def scene_sunlight(p,im,d,t):
    # Scene 0: direct photon absorption, moving sunlight and a large leaf.
    sun(p,im,d,123,417,t)
    leaf(p,d,350,581,1.65,t,-.22)
    for k in range(10):
        start=(161+((k*31)%100),449+((k*19)%75))
        end=(278+((k*29)%130),550+((k*13)%110))
        line(p,d,[start,end],SUN,1.3,45)
        u=(t*.40+k/10)%1
        x=start[0]+(end[0]-start[0])*u
        y=start[1]+(end[1]-start[1])*u
        glow(p,im,x,y,3,SUN)
    for k in range(9):
        x=305+(k*33)%155
        y=537+(k*23)%97
        circle(p,d,x,y,1.8,LIME,82)


def scene_roots(p,im,d,t):
    # Scene 1: xylem transports absorbed water from roots to foliage.
    plant(p,d,t)
    for k in range(19):
        progress=(t*.23+k/19)%1
        xx=290+3*math.sin(progress*11+k)
        yy=814-315*progress
        molecules(p,d,xx,yy,"water",t,.75)
    for k in range(24):
        x=68+(k*47)%438
        y=752+(k*43)%89
        circle(p,d,x,y,1.5,WATER,65+(k%3)*27)
    arrow(p,d,[(347,691),(347,585),(330,506)],WATER)


def scene_stomata(p,im,d,t):
    # Scene 2: opening made by two guard cells; CO2 diffuses inward.
    cx,cy=286,568
    for band in range(4):
        r=157-band*19
        p.circle(d,cx,cy,r,None,(*LEAF,60),1.4)
    aperture=24+5*math.sin(t*.65)
    for side in (-1,1):
        outer=[]
        inner=[]
        for j in range(37):
            v=-1+2*j/36
            x=cx+side*(aperture+38*math.sqrt(max(0,1-v*v)))
            outer.append((x,cy+128*v))
            inner.append((cx+side*(aperture+6*(1-v*v)),cy+128*v))
        polygon=outer+list(reversed(inner))
        d.polygon([p.p(*q) for q in polygon],fill=(43,156,103,230))
        line(p,d,outer,LEAF,3.3,240)
        line(p,d,inner,MINT,2,170)
        for k in range(9):
            v=-.8+k*.2
            x=cx+side*(aperture+24+6*math.cos(k*2.4+t*.15))
            circle(p,d,x,cy+110*v,4.1,LIME,170)
    # Distinct CO2 molecules descend through the dark central pore.
    for k in range(9):
        u=(t*.18+k/9)%1
        yy=381+370*u
        xx=cx+5*math.sin(k*2.4+u*5)
        molecules(p,d,xx,yy,"co2",t,.75)
    p.text(d,"CO₂",286,394,17,(*PALE,225),bold=True)


def scene_chloroplast(p,im,d,t):
    # Scene 3: layered thylakoids inside a chloroplast; sugars downstream.
    cx,cy=258,558
    p.circle(d,cx,cy,161,(25,103,74,236),(*MINT,185),3)
    p.circle(d,cx,cy,148,None,(*LEAF,60),2)
    for stack in range(4):
        x=169+stack*57
        y=504+17*(stack%2)
        for disc in range(6):
            y0=y+disc*17
            p.circle(d,x,y0,21,(48,165,106,229),(*LIME,150),1.3)
            line(p,d,[(x-20,y0),(x+20,y0)],(159,241,160),1,89)
    for k in range(10):
        u=(t*.25+k/10)%1
        x=57+166*u
        y=424+100*u
        circle(p,d,x,y,3.3,SUN,205)
    arrow(p,d,[(389,556),(441,574),(472,613)],LIME)
    for k in range(3):
        sugar(p,d,463+26*math.sin(k*2+1.4),615+k*35,t,.59)
    # Sugars are a downstream output of a multi-step process, not photons.
    p.text(d,"SUGARS",461,714,13,(*LIME,225),bold=True)


def scene_oxygen(p,im,d,t):
    # Scene 4: paired oxygen atoms leave the photosynthetic leaf.
    leaf(p,d,270,609,1.7,t,.12)
    for k in range(22):
        u=(t*.19+k/22)%1
        x=277+170*u+16*math.sin(u*6+k)
        y=635-255*u+7*math.cos(k*2+u*8)
        molecules(p,d,x,y,"oxygen",t,.70+(k%3)*.15)
    arrow(p,d,[(370,582),(437,498),(473,440)],SKY)
    p.text(d,"O₂",455,399,19,(*SKY,240),bold=True)


def scene_food_web(p,im,d,t):
    # Scene 5: a simple energy path with distinct living organisms.
    leaf(p,d,127,574,.73,t,-.17)
    # Insect: antennae, head, wings, articulated legs and abdomen.
    cx,cy=285,577
    p.circle(d,cx,cy,18,(84,171,165,235),(*MINT,185),1.7)
    p.circle(d,cx+22,cy,10,(67,165,139,235),(*MINT,150),1.4)
    for side in (-1,1):
        wing=[(cx-7,cy),(cx-36,cy+side*33),
              (cx-12,cy+side*47),(cx+10,cy+side*11)]
        d.polygon([p.p(*pt) for pt in wing],fill=(111,205,203,110))
        line(p,d,wing,MINT,1.3,144)
        for k in range(3):
            line(p,d,[(cx-13+k*13,cy+side*8),
                      (cx-27+k*14,cy+side*22)],MINT,1.6,151)
    for k in range(2):
        line(p,d,[(cx+25,cy-6),(cx+37+8*k,cy-15-7*k)],MINT,1.5,145)
    # Bird: animated wing shape, body silhouette, pointed beak and tail.
    bx,by=462,552
    wing=24*math.sin(t*4)
    body=[(bx-44,by+7),(bx-8,by-18),(bx+28,by-10),
          (bx+49,by+1),(bx+24,by+22),(bx-19,by+19)]
    d.polygon([p.p(*pt) for pt in body],fill=(73,150,175,226))
    line(p,d,body+[body[0]],SKY,2.5,210)
    d.polygon([p.p(*pt) for pt in [(bx+41,by-4),(bx+67,by+3),
                                   (bx+40,by+11)]],fill=(*SUN,210))
    line(p,d,[(bx-8,by+3),(bx-37,by-27-wing),(bx+18,by-8)],SKY,4,200)
    circle(p,d,bx+25,by-7,3.3,PALE,236)
    arrow(p,d,[(185,560),(210,552),(248,552)],LIME,0,2.7)
    arrow(p,d,[(330,558),(360,547),(399,547)],LIME,0,2.7)
    moving_beads(p,im,d,[(183,565),(218,552),(248,552)],t,3,LIME,.31,2.4)
    moving_beads(p,im,d,[(331,563),(360,548),(397,548)],t,3,LIME,.30,2.4)
    p.text(d,"ENERGY FLOWS",287,716,14,(*MINT,195),bold=True)


SCENES=(scene_sunlight,scene_roots,scene_stomata,
        scene_chloroplast,scene_oxygen,scene_food_web)


def draw(p,im,t,scene_index,phase):
    d=ImageDraw.Draw(im,"RGBA")
    # A softly moving dust layer makes the environmental volume continuous.
    for k in range(19):
        x=55+((k*91+t*(2.2+k%4))%460)
        y=404+((k*83+t*(1.5+k%3))%300)
        circle(p,d,x,y,.85+(k%3)*.25,LIME,35+(k%4)*11)
    SCENES[min(len(SCENES)-1,max(0,scene_index))](p,im,d,t)
