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


def volcanic_structure(p,im,t):
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
    # Visible flowing magma follows the right cliff, advancing continuously
    # along the rock contour rather than a vertical linear progress bar.
    branches=(
        [(286,525),(306,563),(337,628),(371,693),(402,756),(452,813)],
        [(287,528),(273,580),(246,643),(221,700),(183,757)],
        [(314,555),(347,611),(364,656),(389,718),(422,768)],
    )
    for branch,points in enumerate(branches):
        p.line(d,points,(111,52,43,236),7.5-branch*.7)
        p.line(d,points,(241,112,48,204),4.3-branch*.3)
        p.line(d,points,(255,203,88,216),max(1.2,2.2-branch*.3))
        # Small lava beads visibly run along the corresponding physical path.
        progress=(t*(.13+branch*.018)+branch*.28)%1
        i=min(len(points)-2,int(progress*(len(points)-1)))
        q=progress*(len(points)-1)-i
        xx=points[i][0]*(1-q)+points[i+1][0]*q
        yy=points[i][1]*(1-q)+points[i+1][1]*q
        p.circle(d,xx,yy,4.6,(*LAVA,234))
    # Crater is a horizontal incandescent ellipse rim, not a simple line.
    x0,y0=p.p(249,519);x1,y1=p.p(311,536)
    d.ellipse((x0,y0,x1,y1),fill=(213,87,42,243),outline=(255,198,90,250),
              width=max(1,round(2*p.s)))
    # Directional vents and embers respond to buoyant rising gas.
    for j in range(37):
        age=(t*(.4+j%3*.08)+j*.31)%3.1
        xx=281+math.sin(j*3.3+age*.75)*(13+age*25)
        yy=526-age*(64+(j%4)*6)+age*age*3.8
        if yy<262:
            continue
        size=1+(j%3)*.4
        p.circle(d,xx,yy,size,(250,159+(j%3)*16,88,round(100+115*(1-age/3.2))))
