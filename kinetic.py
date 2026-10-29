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


def ocean(p, im, t, ix, phase):
    """Six physically animated editorial treatments of a single ocean subject."""
    d = ImageDraw.Draw(im, "RGBA")
    # Continuously moving water surface persists across all six chapters.
    for layer in range(4):
        baseline=400+layer*102
        coords=[(x,baseline+(7+layer*2)*math.sin(x*.022-t*(1.2+layer*.16)+layer*.7))
                for x in range(20,561,8)]
        path(p,d,coords,BLUE if layer%2 else CYAN,1.6,55+layer*13)
    if ix==0:
        # Opening life: independent fish with undulating tails in moving flow.
        for k in range(5):
            direction=1 if k%2==0 else -1
            px=(t*(45+k*10)+k*133+20)%700-65
            if direction<0:px=576-px
            py=460+k*64+20*math.sin(t*1.2+k)
            r=10+2*k
            p.circle(d,px,py,r,(31,156,181,210),(*CYAN,240),2)
            tail=[(px-direction*r,py),(px-direction*(r+22),py-15+7*math.sin(t*7+k)),
                  (px-direction*(r+22),py+15+7*math.sin(t*7+k))]
            d.polygon([p.p(*q) for q in tail],fill=(*CYAN,190))
            dot(p,d,px+direction*4,py-3,2,WHITE,255)
        moving_particles(p,im,t,ix,38,410,760)
    elif ix==1:
        # Wind over the sea: gust streaks and wind-driven surface drift.
        for k in range(12):
            x=(k*89+t*78)%700-95
            y=380+k%4*58
            length=38+(k%4)*20
            path(p,d,[(x,y),(x+length,y-8*math.sin(t*.8+k))],CYAN,2.8,160)
        for k in range(25):
            x=35+(k*97+t*40)%506
            y=508+(k%5)*45+8*math.sin(t*2+k)
            dot(p,d,x,y,2,BLUE,145)
        path(p,d,[(76,703),(144,669),(213,636),(282,606),
                  (350,573),(420,540),(491,498)],GOLD,4,215)
        for k in range(4):
            pos=(t*.2+k*.25)%1
            x=76+415*pos
            y=703-205*pos
            p.glow_disc(im,x,y,3.6,GOLD)
    elif ix==2:
        # Cooling and salinity change density: particles sink vertically.
        p.circle(d,130,414,55,(38,149,186,75),(*BLUE,185),2)
        p.circle(d,440,414,55,(235,155,59,65),(*GOLD,180),2)
        for k in range(55):
            x=70+(k*83)%455
            if k%2:
                y=425+(t*42+k*26)%330  # dense cool particles sink
                dot(p,d,x,y,2+(k%3),BLUE,170)
            else:
                y=746-(t*31+k*34)%310  # lighter warm fluid rises
                dot(p,d,x,y,2+(k%3),GOLD,155)
        for k in range(6):
            x=130+56*k
            path(p,d,[(x,486),(x-16*math.sin(t+k*.7),694)],BLUE,2,85)
        path(p,d,[(140,758),(433,758)],CYAN,2.5,185)
    elif ix==3:
        # Global thermohaline circulation: a deep looping conveyor with moving tracers.
        pts=[(90,463),(177,431),(291,460),(414,519),(475,612),
             (426,711),(293,752),(159,704),(96,602),(90,463)]
        path(p,d,pts,BLUE,4,185)
        for k in range(12):
            progress=(t*.055+k/12)%1
            segment=progress*(len(pts)-1)
            i=int(segment)
            q=segment-i
            x=pts[i][0]*(1-q)+pts[i+1][0]*q
            y=pts[i][1]*(1-q)+pts[i+1][1]*q
            p.glow_disc(im,x,y,4,CYAN if k%2 else GOLD)
        p.circle(d,288,581,75,None,(*CYAN,95),2)
        moving_particles(p,im,t,ix,12,430,740)
    elif ix==4:
        # Ocean heat transfer: warm and cold tracers exchange along moving streams.
        path(p,d,[(56,702),(182,642),(288,565),(391,480),(518,405)],GOLD,5,185)
        path(p,d,[(56,421),(184,491),(288,573),(390,647),(518,722)],BLUE,5,185)
        for k in range(22):
            progress=(t*.13+k/22)%1
            x=56+462*progress
            hot_y=702-297*progress+8*math.sin(t+progress*6)
            cold_y=421+301*progress-8*math.sin(t+progress*6)
            dot(p,d,x,hot_y,3+(k%3),GOLD,175)
            dot(p,d,x,cold_y,3+(k%3),BLUE,175)
        p.circle(d,288,564,92,None,(*CYAN,100),1.7)
    else:
        # Concluding map-like streams: dynamic spiralling currents around a globe.
        cx,cy=288,575
        p.planet(im,cx,cy,100)
        for ring in range(3):
            rr=128+ring*27
            pts=[(cx+rr*math.cos(j*.09+t*.12+ring*.6),
                  cy+.67*rr*math.sin(j*.09+t*.12+ring*.6)) for j in range(71)]
            path(p,d,pts,CYAN if ring%2 else GOLD,2,75)
            for k in range(5):
                a=t*(.6+ring*.13)+k*TAU/5
                dot(p,d,cx+rr*math.cos(a),cy+.67*rr*math.sin(a),3.5,
                    CYAN if ring%2 else GOLD,225)
        moving_particles(p,im,t,ix,26,400,760)

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
        p.line(d,[(x,766),(x,766-h)],(*(CYAN if k%2 else GOLD),210),18)
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


def earthquake(p, im, t, ix, phase):
    """Fault slip, outward seismic waves and a scrolling seismograph."""
    d=ImageDraw.Draw(im,"RGBA")
    pulse=max(0.0,math.sin(t*3.2+ix*.35))
    shift=(3+ix*1.5)*math.sin(t*2.8) if ix>=2 else math.sin(t*.8)*1.7
    left=[(28,613+shift),(265,600+shift),(275,724),(28,751)]
    right=[(286,602-shift),(550,628-shift),(550,750),(276,724)]
    d.polygon([p.p(*xy) for xy in left],fill=(39,72,90,210))
    d.polygon([p.p(*xy) for xy in right],fill=(62,58,91,210))
    path(p,d,[(25,612+shift),(265,600+shift)],CYAN,4,210)
    path(p,d,[(286,602-shift),(550,628-shift)],BLUE,4,210)
    path(p,d,[(272,600),(285,632),(267,664),(286,702),(275,724)],GOLD,4,220)
    for ring in range(6):
        age=(t*.54+ring/6+ix*.08)%1
        p.circle(d,276,608,30+age*205,None,(*GOLD,int((1-age)**1.4*170)),2.8)
    for i in range(50):
        x=40+(i*91.31)%505
        y=395+(i*37.2)%150
        dot(p,d,x+3*math.sin(t*2+i),y+7*pulse*math.sin(i*1.7),
            1+(i%3)*.5,CYAN if i%4 else GOLD,65)
    graph=[]
    for i in range(101):
        x=40+i*4.95
        q=i/100*9-t*2.5
        amp=(6+45*pulse)*math.exp(-((q%3.2)-1.2)**2/.12)
        graph.append((x,831+amp*math.sin(q*16)))
    path(p,d,graph,CYAN,2.6,235)


def weather(p, im, t, ix, phase):
    """Moving convection cells, cloud banks, rain and wind trajectories."""
    d=ImageDraw.Draw(im,"RGBA")
    for band in range(3):
        y=429+band*130
        pts=[(x,y+16*math.sin(x*.012-t*(.55+band*.15)+band))
             for x in range(45,551,8)]
        path(p,d,pts,BLUE if band%2 else CYAN,2.4,125)
    for j in range(4):
        x=(j*162+t*(17+j*4))%760-85
        y=397+(j%2)*105+10*math.sin(t*.4+j)
        for dx,dy,r in [(-32,7,27),(-5,-8,37),(32,4,29),(60,14,22)]:
            p.circle(d,x+dx,y+dy,r,(86,126,166,140),(*BLUE,70),1.4)
        if ix>=2:
            for k in range(12):
                rx=x-35+(k%6)*23
                ry=y+44+(t*(65+k%4*7)+k*39)%220
                if 380<ry<782:path(p,d,[(rx,ry),(rx-5,ry+12)],CYAN,1.6,150)
    for k in range(15):
        x=(t*80+k*71)%680-40
        y=639+(k%4)*45
        path(p,d,[(x,y),(x+47+10*math.sin(t+k),y-7)],
             GOLD if k%5==0 else CYAN,2.0,105+(k%3)*32)
    for k in range(12):
        a=t*(.75+k%3*.11)+k*TAU/12
        dot(p,d,289+111*math.cos(a),603+145*math.sin(a),2.5,
            GOLD if k%2 else CYAN,195)


def biology(p, im, t, ix, phase):
    """Leaf photosynthesis with moving photons, transported water and oxygen."""
    d=ImageDraw.Draw(im,"RGBA")
    leaf=[(288,734),(215,688),(173,584),(186,470),(288,399),
          (394,470),(410,577),(355,690)]
    d.polygon([p.p(*xy) for xy in leaf],fill=(20,103,82,165))
    path(p,d,leaf+[leaf[0]],CYAN,3.4,225)
    path(p,d,[(288,727),(288,421)],GOLD,3,165)
    for side in (-1,1):
        for k in range(4):
            y=470+k*58
            path(p,d,[(288,y+49),(288+side*(30+k*8),y)],CYAN,1.7,120)
    for k in range(24):
        x=225+(k%6)*25+5*math.sin(t*.8+k)
        y=489+(k//6)*42+5*math.cos(t*.7+k)
        dot(p,d,x,y,max(1,4.5+1.4*math.sin(t*2+k)),CYAN,125+(k%3)*26)
    for k in range(19):
        progress=(t*.33+k/19)%1
        dot(p,d,59+progress*224,341+progress*170,2.6,GOLD,210)
    for k in range(20):
        progress=(t*.38+k/20)%1
        dot(p,d,284+5*math.sin(k+t),857-progress*130,2.2,BLUE,185)
    for k in range(19):
        age=(t*.28+k/19)%1
        dot(p,d,328+age*145+19*math.sin(k+t*.4),584-age*223,2.5,WHITE,150)


ANIMATORS = {
    "ocean":ocean,"volcano":volcano,"space":space,"tech":technology,
    "health":health,"economy":economy,"general":general,
    "weather":weather,"earthquake":earthquake,"biology":biology,
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
