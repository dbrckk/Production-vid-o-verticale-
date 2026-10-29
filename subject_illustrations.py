"""Premium hand-authored 2D subjects for vertical science documentaries.

These are frame-by-frame animated animals and geological structures, not
pre-composed slideshow imagery or 3D renderings. The visual geometry responds
continuously to absolute story time and works at every supported resolution.
"""
from __future__ import annotations

import math
from PIL import ImageDraw

SEA_LIGHT=(119,231,215)
SEA_DARK=(23,93,116)
SEA_FLASH=(240,217,154)
LAVA=(255,178,78)
ROCK=(53,57,82)


def fish(p,d,x,y,r,direction,t,identity):
    """Stylized but anatomically coherent swimming fish with live tail and fins.

    Body, back, ventral fin and caudal fin are connected; the tail oscillates
    in phase with the swim cycle while the head remains stable in world space.
    """
    if direction not in (-1,1):
        raise ValueError("fish direction must be -1 or 1")
    sway=math.sin(t*(5.5+identity*.23)+identity*.8)
    nose=x+direction*r*1.64
    tailbase=x-direction*r*.9
    caudal=tailbase-direction*(r*.77+.18*r*sway)
    upper=y-r*.75
    lower=y+r*.68
    body=[
        (nose,y),(x+direction*r*.82,upper),
        (x-direction*r*.35,y-r*.85),(tailbase,y-r*.34),
        (tailbase,y+r*.34),(x-direction*r*.33,y+r*.73),
        (x+direction*r*.86,y+r*.35),
    ]
    pbody=[p.p(*pt) for pt in body]
    # Distinct outline and inner shaded belly create volume at 1080p without 3D.
    d.polygon(pbody,fill=(34,119,139,245))
    p.line(d,body,(*SEA_LIGHT,205),1.35)
    d.polygon([p.p(tailbase,y-r*.32),
               p.p(caudal,y-r*(1.18+.16*sway)),
               p.p(caudal+direction*r*.22,y),
               p.p(caudal,y+r*(1.10-.16*sway)),
               p.p(tailbase,y+r*.32)],fill=(52,166,173,240))
    d.polygon([p.p(x+direction*r*.31,y-r*.71),
               p.p(x-direction*r*.49,y-r*1.36),
               p.p(x-direction*r*.36,y-r*.77)],fill=(35,166,165,222))
    d.polygon([p.p(x-direction*r*.14,y+r*.54),
               p.p(x-direction*r*.55,y+r*1.03),
               p.p(x+direction*r*.36,y+r*.57)],fill=(65,173,163,170))
    # On-body specular stripe, fine gill crease and tiny bright eye.
    p.line(d,[(x-direction*r*.65,y-r*.25),
              (x+direction*r*.95,y-r*.29)],(*SEA_LIGHT,165),1)
    p.line(d,[(x+direction*r*.92,y-r*.31),
              (x+direction*r*.92,y+r*.34)],(15,64,88,135),.85)
    p.circle(d,x+direction*r*1.20,y-r*.16,max(1.2,r*.105),(246,249,240,250))
    p.circle(d,x+direction*r*1.23,y-r*.15,max(.65,r*.05),(18,54,68,255))
    # Reflected caustic highlights slide over the body.
    gleam=(.5+.5*math.sin(t*1.2+identity*.73))
    p.circle(d,x-direction*r*.15+gleam*r*.46,y-r*.28,1.3,(*SEA_FLASH,round(60+70*gleam)))


def _revealed_path(points, fraction):
    """Arc-length-based one-way lava advance; never jumps back to the vent."""
    q=max(0.0,min(1.0,float(fraction)))
    lengths=[math.dist(points[i],points[i+1]) for i in range(len(points)-1)]
    limit=sum(lengths)*q
    result=[points[0]]
    for i,length in enumerate(lengths):
        if limit<=0:
            break
        step=min(1.0,limit/max(length,1e-6))
        a,b=points[i],points[i+1]
        result.append((a[0]+(b[0]-a[0])*step,a[1]+(b[1]-a[1])*step))
        limit-=length
        if step<1:
            break
    return result


def volcanic_structure(p,im,t,scene_index=4,phase=1.0):
    """Layered volcanic cone and directional lava fractures behind main data.

    Cliffs, rim and fracture zones have distinct silhouettes and internally
    consistent light: hot cracks illuminate nearby rock faces only.
    """
    d=ImageDraw.Draw(im,"RGBA")
    cliff=[
        (0,857),(38,783),(110,726),(162,656),(224,548),
        (250,526),(279,531),(305,526),(343,563),(419,691),
        (506,767),(576,850),(576,916),(0,916),
    ]
    d.polygon([p.p(*pt) for pt in cliff],fill=(39,39,58,250))
    # Far-side blue slate strata vs warm volcanic cone.
    bands=[
        ([(44,806),(164,671),(230,571),(260,559),(281,570),
          (279,609),(223,637),(155,753),(78,840)],(64,65,84,241)),
        ([(310,575),(348,632),(417,747),(505,821),(553,856),
          (483,820),(404,779),(347,677)],(70,55,65,236)),
        ([(112,760),(182,695),(218,647),(243,628),
          (209,684),(157,774)],(90,68,70,230)),
    ]
    for points,color in bands:
        d.polygon([p.p(*pt) for pt in points],fill=color)
    # Repeated gently shifted contour marks communicate genuine mineral layers.
    for row in range(7):
        left=87+row*12
        y=698+row*20
        points=[(left,y),(left+45,y-9),(left+91,y-23)]
        p.line(d,points,(141,115,115,110),1.1)
        rpoints=[(405+row*9,y-24),(436+row*9,y-11),(465+row*9,y+5)]
        p.line(d,rpoints,(166,115,108,105),1)
    # Fine rock facets: original irregular polygons add depth to the cone.
    for j in range(32):
        side=-1 if j%2 else 1
        x=288+side*(35+(j*23)%172)
        y=581+(j*43)%205
        if not (578<y<791):
            continue
        opacity=38+(j%4)*13
        facet=[(x-4,y+4),(x+2,y-7),(x+13,y-1),(x+7,y+7)]
        d.polygon([p.p(*point) for point in facet],
                  fill=((140,125,117,opacity) if side<0 else (166,111,91,opacity)))
        if j%3==0:
            p.line(d,[(x-5,y+6),(x+11,y+7)],(199,143,111,65),.9)
    # Stage-specific geology prevents identical volcanic slides across the story.
    # Magma is trapped for the first three beats and only reaches the outer
    # slopes when the narrative actually introduces an eruption.
    if scene_index>=3:
        branches=(
            [(286,525),(306,563),(337,628),(371,693),(402,756),(452,813)],
            [(287,528),(273,580),(246,643),(221,700),(183,757)],
            [(314,555),(347,611),(364,656),(389,718),(422,768)],
        )
        q=max(0.0,min(1.0,float(phase)))
        q=q*q*(3-2*q)
        # One lifecycle: emergence, downslope advance and cooling.
        # The leading front never jumps back to the crater.
        advance=(.045+.34*q) if scene_index==3 else (
            (.385+.615*q) if scene_index==4 else 1.0)
        for branch,points in enumerate(branches):
            progress=max(.0,min(1.,advance-branch*.12))
            visible=_revealed_path(points,progress)
            if len(visible)<2:
                continue
            cooling=(.42+.43*(1-q)) if scene_index==5 else 1.0
            alpha=max(42,round(226*cooling))
            p.line(d,visible,(111,52,43,236),7.5-branch*.7)
            p.line(d,visible,(round(115+128*cooling),round(64+49*cooling),48,alpha),
                   4.3-branch*.3)
            p.line(d,visible,(255,round(100+105*cooling),88,round(150*cooling)),
                   max(1.2,2.2-branch*.3))
            if scene_index in (3,4):
                tip=visible[-1]
                p.circle(d,*tip,5.1,(*LAVA,225))
                p.circle(d,*tip,2.2,(255,237,149,245))
                for k in range(8):
                    a=(t*(.11+.025*branch)+k/8)%1
                    segment=_revealed_path(visible,a)
                    if segment:
                        px,py=segment[-1]
                        p.circle(d,px,py,1.0+(k%3)*.5,(*LAVA,90+(k%3)*32))
    rim_hot=scene_index>=2
    x0,y0=p.p(249,519)
    x1,y1=p.p(311,536)
    d.ellipse((x0,y0,x1,y1),
              fill=(213,87,42,243) if rim_hot else (69,65,75,244),
              outline=(255,198,90,245) if rim_hot else (126,124,133,210),
              width=max(1,round(2*p.s)))
    if scene_index>=3:
        # Rising cinders are strongest during the explosive scene, restrained
        # during cooling, and absent while the chamber is still sealed.
        count=50 if scene_index==3 else (22 if scene_index==4 else 9)
        for j in range(count):
            age=(t*(.4+j%3*.08)+j*.31)%3.1
            xx=281+math.sin(j*3.3+age*.75)*(13+age*25)
            yy=526-age*(64+(j%4)*6)+age*age*3.8
            if yy<262:
                continue
            p.circle(d,xx,yy,1+(j%3)*.4,
                     (250,159+(j%3)*16,88,round(100+115*(1-age/3.2))))
