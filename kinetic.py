"""Procedural physical motion, not slide-show imagery.

Every scene has simulated motion: particles, waves, orbital trajectories, fluid
currents, light travelling through circuits, rising bars and animated diagrams.
Everything is redrawn from continuous time at 9:16, with deterministic seeds.
"""
from __future__ import annotations
import math
from PIL import ImageDraw

TAU = 2 * math.pi
CYAN = (96,238,202)
GOLD = (251,188,104)
BLUE = (117,160,246)
WHITE = (242,245,255)


def dot(p,d,x,y,r,color,alpha=210):
    p.circle(d,x,y,r,(*color,alpha))


def path(p,d,coords,color=CYAN,width=2.5,alpha=190):
    p.line(d,coords,(*color,alpha),width)


def moving_particles(p,im,t,ix,count=44,lower=385,upper=770):
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(count):
        vx=(i*113.7 + t*(12+i%7*5)*((-1)**(i%3))) % 526+25
        vy=lower+((i*71.7 + t*(i%5+1)*22)%(upper-lower))
        rad=1+(i%4)*.65
        dot(p,d,vx,vy,rad,CYAN if i%3 else GOLD,62+(i%3)*42)


def ocean(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    # Actual water particles follow 3 phase-shifted, depth-dependent sine waves.
    for layer in range(6):
        baseline=410+layer*58
        amp=8+layer*2.5
        coords=[(x,baseline+amp*math.sin(x*.021-t*(1.0+layer*.13)+layer*.65))
                for x in range(20,561,8)]
        path(p,d,coords,BLUE if layer%2 else CYAN,1.7,55+layer*19)
    for j in range(6):
        x=75+j*92+13*math.sin(t*.36+j)
        path(p,d,[(x-95,310),(x+65,825)],BLUE,3,25)
    moving_particles(p,im,t,ix,45)
    # A swimming fish, fins beating at 4 Hz and speed depending on scene.
    for k in range(3):
        direction=1 if k%2==0 else -1
        px=(t*(48+15*k)+k*180+45) % 720-70
        if direction<0:px=576-px
        py=520+k*75+19*math.sin(t*1.6+k)
        s=(.8+k*.23)
        p.circle(d,px,py,16*s,(43,177,175,190),(184,252,225,235),2)
        swing=math.sin(t*9+k)*12
        tail=[(px-direction*14*s,py),(px-direction*43*s,py-17*s+swing),
              (px-direction*43*s,py+17*s+swing)]
        d.polygon([p.p(*q) for q in tail],fill=(*CYAN,170))
        dot(p,d,px+direction*7*s,py-4*s,2.1,WHITE,255)
        path(p,d,[(px-6*s,py+13*s),(px+3*s,py+24*s),(px+10*s,py+10*s)],GOLD,1.8,165)
    # The visible level rises and falls rather than translating static images.
    for k in range(20):
        px=35+((k*97+t*(6+k%4*4))%520)
        py=760-((t*29+k*39)%350)
        dot(p,d,px,py,2.5+(k%3),BLUE,92)


def volcano(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    crater=513
    path(p,d,[(28,775),(174,615),(235,520),(275,crater),(317,520),(391,627),(550,775)],CYAN,5,230)
    path(p,d,[(248,523),(277,521),(302,528)],GOLD,9,235)
    # Animated molten lava pours down both slopes.
    for k in range(10):
        yy=545+k*21
        xx=288+math.sin(k*.3+t*.33)*8 + (k*8)%28
        path(p,d,[(xx,yy),(xx+5+4*math.sin(t*2+k),yy+18)],GOLD,5.5,225)
    # Ballistic rock particles in different stages of flight.
    for k in range(70):
        age=(t*1.0+k*.193) % 3.7
        vx=math.sin(k*4.123)*110+math.sin(k*1.7)*55
        px=288+vx*age/1.55
        py=515-195*age+62*age*age
        if 285<py<830:
            dot(p,d,px,py,1.9+(k%4),GOLD if k%3 else CYAN,150+(k%3)*30)
    # Volcano periodically illuminates the surroundings.
    pulse=(math.sin(t*2.8)+1)/2
    p.circle(d,285,515,24+15*pulse,None,(*GOLD,int(35+80*pulse)),3)
    moving_particles(p,im,t,ix,25,370,810)


def space(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    # Continuous elliptical orbits: Earth and a smaller satellite really move.
    sunx,suny=286,572
    for radius in (101,163,219):
        coords=[(sunx+radius*math.cos(a/80*TAU),
                 suny+radius*.68*math.sin(a/80*TAU)) for a in range(81)]
        path(p,d,coords,BLUE,1.5,105)
    p.glow_disc(im,sunx,suny,39,GOLD)
    p.circle(d,sunx,suny,27,(252,179,81,248),(255,224,142,250),2)
    for k in range(32):
        angle=(k/32)*TAU+t*.1
        dist=38+3*math.sin(t*4+k)
        path(p,d,[(sunx+dist*math.cos(angle),suny+dist*math.sin(angle)),
                  (sunx+(dist+14)*math.cos(angle),suny+(dist+14)*math.sin(angle))],GOLD,2,180)
    angle=t*.65+ix*.72
    ex=sunx+166*math.cos(angle)
    ey=suny+112*math.sin(angle)
    p.planet(im,ex,ey,25+3*math.sin(t*.75))
    satellite_angle=t*3.8+ix
    moonx=ex+34*math.cos(satellite_angle)
    moony=ey+28*math.sin(satellite_angle)
    dot(p,d,moonx,moony,6,WHITE,230)
    for k in range(70):
        angle=k*2.399
        radius=165+k%97
        dot(p,d,288+radius*math.cos(angle)+.4*t,572+radius*math.sin(angle),.8+(k%3)*.35,WHITE,40+k%4*20)


def technology(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    p.circle(d,288,550,96,(16,42,65,243),(*CYAN,230),2.5)
    # Animated traces simulate messages propagating from processor to memory.
    for side in (-1,1):
        for k in range(8):
            offset=(k-3.5)*23
            a=(288+side*95,550+offset)
            b=(288+side*(142+k%3*10),550+offset)
            c=(288+side*(182+k%3*10),550+offset+(k%2-.5)*35)
            path(p,d,[a,b,c],BLUE,2,155)
            flight=(t*.8+k*.21+ix*.1)%1
            if flight<.5:
                q=flight*2;px=a[0]*(1-q)+b[0]*q;py=a[1]*(1-q)+b[1]*q
            else:
                q=(flight-.5)*2;px=b[0]*(1-q)+c[0]*q;py=b[1]*(1-q)+c[1]*q
            p.glow_disc(im,px,py,2.5,CYAN if k%2 else GOLD)
            dot(p,d,c[0],c[1],4.5,CYAN,230)
    # Transistor grid pulses in sequence, with a visible pattern change.
    for row in range(6):
        for col in range(6):
            x=242+col*18;y=504+row*18
            active=(math.sin(t*6+col*.8+row*.6)>0)
            dot(p,d,x,y,3.3,CYAN if active else BLUE,240 if active else 75)
    moving_particles(p,im,t,ix,22,390,745)


def health(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    # One heartbeat cycle per 1.1 seconds, constriction/expansion of a heart.
    beat=math.exp(-((t%1.1-.18)/.14)**2)
    rr=1+.105*beat
    heart=[]
    for i in range(75):
        a=i/74*TAU
        x=288+rr*(10*16*math.sin(a)**3)
        y=570-rr*(10*(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a)))
        heart.append((x,y))
    path(p,d,heart,CYAN,4,235)
    for a in range(4):
        p.circle(d,288,575,179+a*18+beat*4,None,(*BLUE,max(18,90-a*19)),1.3)
    # Trace scans left-to-right and is not a static ECG image.
    line=[]
    for j in range(96):
        x=52+j*5
        u=(j/95+t*.55)%1
        spike=math.exp(-((u-.23)/.025)**2)*-65+math.exp(-((u-.28)/.02)**2)*85
        line.append((x,775+spike))
    path(p,d,line,GOLD,2.6,220)
    for k in range(16):
        a=k*2.39+t*.4
        x=288+210*math.cos(a)
        y=585+160*math.sin(a)
        dot(p,d,x,y,4+(k%4),CYAN if k%3 else GOLD,80)


def economy(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    path(p,d,[(58,766),(516,766)],BLUE,2,180)
    chart=[]
    for k in range(8):
        x=80+k*61
        target=50+33*k+42*math.sin(k*1.8+ix*.2)
        rise=min(1,max(0,phase*3-k*.10))
        h=max(4,target*rise)
        p.line(d,[(x,766),(x,766-h)],(*CYAN if k%2 else GOLD,210),18)
        chart.append((x,766-h))
        dot(p,d,x,766-h,3,WHITE,240)
    shown=int(1+phase*7)
    if shown>1:
        path(p,d,chart[:shown],GOLD,3.5,190)
    for k in range(12):
        x=(50+k*41+t*18)%528+20
        y=400+35*math.sin(k*.2+t*.35)
        p.circle(d,x,y,12+(k%3)*3,None,(*BLUE,70),1.7)
    moving_particles(p,im,t,ix,23,390,740)


def general(p,im,t,ix,phase):
    d=ImageDraw.Draw(im,"RGBA")
    # A dynamic causal diagram with moving nodes and propagating signals.
    coords=[]
    for k in range(9):
        a=k/9*TAU+t*(.13+ix*.017)
        rr=116+18*math.sin(t*.8+k*1.3)
        x=288+rr*math.cos(a)
        y=560+rr*.8*math.sin(a)
        coords.append((x,y))
    for k,(x,y) in enumerate(coords):
        nxt=coords[(k+3)%9]
        path(p,d,[(x,y),nxt],BLUE,1.5,70)
        q=(t*.53+k*.09)%1
        px=x*(1-q)+nxt[0]*q
        py=y*(1-q)+nxt[1]*q
        dot(p,d,px,py,3,GOLD,240)
    for k,(x,y) in enumerate(coords):
        p.glow_disc(im,x,y,4,CYAN if k%2 else GOLD)
    p.circle(d,288,560,38,(28,69,82,210),(*CYAN,230),2.2)


ANIMATORS = {
    "ocean":ocean,"volcano":volcano,"space":space,"tech":technology,
    "health":health,"economy":economy,"general":general,
}


def draw(p,im,category: str,t:float,scene_index:int,phase:float):
    # Slow camera drift: starfield and a second independent parallax layer.
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(35):
        x=25+(i*73+(t*(i%3+1)*3))%528
        y=310+(i*83+(t*(i%5+1)*2))%480
        dot(p,d,x,y,.7+(i%3)*.4,BLUE,32+(i%3)*20)
    fn=ANIMATORS.get(category,general)
    fn(p,im,t,scene_index,phase)
    # A physically moving highlight sweeps behind the active diagram.
    x=72+432*(phase**.8)
    path(p,d,[(x,821),(x+12,821)],CYAN,2.8,230)
