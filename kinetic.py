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
        # Physical fish silhouettes: tapered bodies, gills, dorsal/ventral fins,
        # articulated tails and reflected caustics. No moving clip-art circles.
        from subject_illustrations import fish
        for k in range(8):
            direction=1 if k%2==0 else -1
            speed=37+k*4.8
            px=(t*speed+k*93+16)%760-92
            if direction<0:
                px=576-px
            py=420+(k%5)*59+15*math.sin(t*.81+k*1.3)
            r=10.5+(k%4)*2.6
            fish(p,d,px,py,r,direction,t,k)
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
    """Scene-dependent physical eruption, not the same animated volcano six times."""
    from volcano_story import draw as draw_volcanic_chapter
    draw_volcanic_chapter(p,im,t,ix,phase)


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
    """Six visually distinct continuous physical sequences of a real earthquake.

    0 drifting plates; 1 accumulating frictional stress; 2 rapid fault slip;
    3 radiating seismic energy; 4 site-dependent building vibration;
    5 live seismometer recording. Every diagram is recomputed over time.
    """
    d = ImageDraw.Draw(im, "RGBA")
    cx,cy = 288,570
    wave = math.sin(t*3.8+ix*.3)
    pulse = .5+.5*wave

    def polygon(coords,fill):
        d.polygon([p.p(*pt) for pt in coords],fill=fill)

    def arrow(a,b,color=CYAN):
        path(p,d,[a,b],color,3.6,220)
        direction=math.atan2(b[1]-a[1],b[0]-a[0])
        r=13
        tips=[(b[0]-r*math.cos(direction-.50),b[1]-r*math.sin(direction-.50)),
              b,(b[0]-r*math.cos(direction+.50),b[1]-r*math.sin(direction+.50))]
        path(p,d,tips,color,3.6,230)

    def plate(x0,x1,shift=0,tint=(40,79,106,230)):
        from geology_premium import mineral_plate
        mineral_plate(p,im,d,x0,x1,shift,tint,t)

    if ix == 0:
        # Plate margins actually drift; convection cells move beneath them.
        drift=6*math.sin(t*.42)
        plate(30,272,-drift,(27,91,102,223))
        plate(299,546,drift,(58,64,104,227))
        path(p,d,[(272,590-drift),(288,630),(299,593+drift)],GOLD,3,230)
        for k in range(9):
            x=70+k*54
            y=454+16*math.sin(t*.55+k*.6)
            direction=1 if k<4 else -1
            arrow((x,y),(x+direction*30,y),CYAN if k%2 else BLUE)
        for k in range(16):
            a=k*TAU/16+t*.35
            x=288+140*math.cos(a)
            y=810+52*math.sin(a)
            if 740<y<874:dot(p,d,x,y,3,GOLD,140)

    elif ix == 1:
        # Stationary fault, but animated compression and a rising stress gauge.
        plate(30,271,0,(28,78,108,240))
        plate(301,546,0,(77,65,101,240))
        for k in range(6):
            yy=502+k*43
            x=270+6*math.sin(t*.7+k)
            path(p,d,[(x,yy),(292,yy+19),(x+4,yy+35)],GOLD,2.8,115+int(pulse*100))
        compression=20+10*pulse
        arrow((90+compression,470),(226+compression,470),GOLD)
        arrow((485-compression,470),(350-compression,470),GOLD)
        path(p,d,[(101,825),(475,825)],BLUE,3,70)
        progress=(phase*.92+.08)
        p.glow_line(im,[(103,825),(103+370*progress,825)],GOLD,5,3)
        for k in range(8):
            x=271+(k%3)*12;y=555+k*22
            dot(p,d,x,y,2.2,GOLD,130+round(100*pulse))

    elif ix == 2:
        # The rupture is a visible relative displacement along a jagged fault.
        # An actual one-way rupture with damped aftershocks, not a block
        # oscillating back and forth with the same displacement forever.
        onset=max(0,min(1,(phase-.12)/.26))
        rupture=onset*onset*(3-2*onset)
        aftershock=8*math.sin(max(0,phase-.38)*29)*math.exp(-max(0,phase-.38)*6)
        slip=3+32*rupture+aftershock
        plate(30,274,-slip,(33,100,103,230))
        plate(295,546,slip,(75,65,97,230))
        path(p,d,[(273,555-slip),(290,605),(272,649),(296,701),(278,779)],
             GOLD,5,250)
        p.glow_disc(im,288,599,6+8*pulse,GOLD)
        for k in range(38):
            age=(t*(.5+k%4*.05)+k/38)%1
            a=k*2.399
            distance=18+age*130
            x=287+math.cos(a)*distance
            y=600+math.sin(a)*distance*.78
            dot(p,d,x,y,max(.8,(1-age)*4.2),GOLD if k%2 else CYAN,
                round(155*(1-age)))
        arrow((76,458),(212,458),CYAN)
        arrow((500,490),(371,490),CYAN)

    elif ix == 3:
        # Seismic waves travel away from the epicentre, not static rings.
        polygon([(47,680),(110,644),(175,676),(245,640),
                 (328,655),(400,628),(529,660),(529,808),(47,808)],
                (37,70,93,185))
        path(p,d,[(47,680),(110,644),(175,676),(245,640),
                  (328,655),(400,628),(529,660)],CYAN,2.5,190)
        origin=(280,605)
        p.glow_disc(im,*origin,7,GOLD)
        for i in range(7):
            age=(t*.26+i/7)%1
            r=16+age*265
            p.circle(d,*origin,r,None,(*GOLD,round((1-age)**.8*220)),3)
            a=i*TAU/7+t*.25
            dot(p,d,origin[0]+r*math.cos(a),origin[1]+r*.8*math.sin(a),
                max(1,5*(1-age)),CYAN,200)
        arrow((110,493),(79,453),BLUE)
        arrow((461,478),(494,444),BLUE)

    elif ix == 4:
        # Compare site response: two different buildings and soil foundations.
        for side in (0,1):
            bx=169 if side==0 else 410
            gain=2.8 if side==0 else 10
            shake=gain*math.sin(t*12.4+side*1.2)
            soil=(56,77,94,215) if side==0 else (111,91,70,195)
            polygon([(bx-102,699),(bx+103,699),(bx+103,787),(bx-102,787)],soil)
            for k in range(4):
                y=721+k*18
                path(p,d,[(bx-97,y),(bx+97,y+3*math.sin(t*.7+k))],
                     BLUE if side==0 else GOLD,1.4,95)
            height=214 if side==0 else 160
            x0,y0=p.p(bx-53+shake,699-height)
            x1,y1=p.p(bx+53+shake,699)
            d.rounded_rectangle((x0,y0,x1,y1),radius=max(2,round(3*p.s)),
                                fill=(36,70,90,240),outline=(*CYAN,240),
                                width=max(1,round(2*p.s)))
            for row in range(5 if side==0 else 4):
                for col in range(3):
                    wx=bx-33+col*32+shake
                    wy=523+(row*30 if side==0 else 25+row*30)
                    if 482<wy<696:
                        p.circle(d,wx,wy,6,(125,222,207,140))
            # Keep factual comparisons above the illustration; the subtitle
            # band occupies the lower 16% of the publishing-safe frame.
            p.text(d,"FIRM GROUND" if side==0 else "SOFT SOIL",
                   bx,420,13,(*(CYAN if side==0 else GOLD),235),bold=True)
        for k in range(18):
            x=51+k*27
            y=690+2*math.sin(t*10+k)
            dot(p,d,x,y,2.0,GOLD,100)

    else:
        # A recording device with a dynamically scrolling real-valued trace.
        x0,y0=p.p(77,434);x1,y1=p.p(501,746)
        d.rounded_rectangle((x0,y0,x1,y1),
                            radius=max(5,round(15*p.s)),
                            fill=(18,36,65,245),outline=(*BLUE,230),
                            width=max(1,round(2*p.s)))
        for k in range(6):
            y=486+k*43
            path(p,d,[(94,y),(482,y)],BLUE,1.4,65)
        for k in range(10):
            x=100+k*42
            path(p,d,[(x,451),(x,731)],BLUE,1.4,55)
        points=[]
        for j in range(180):
            u=j/179
            x=99+381*u
            a=u*24-t*2.7
            burst=math.exp(-((a%6)-2.1)**2/.38)
            y=601+math.sin(a*16)*(7+75*burst)+3*math.sin(a*5)
            points.append((x,y))
        path(p,d,points,CYAN,3.1,230)
        sx=440
        sy=601+65*math.sin(t*7)
        p.glow_disc(im,sx,sy,4,GOLD)
    from geology_premium import earthquake_art
    earthquake_art(p,im,t,ix,phase)
    moving_particles(p,im,t,ix,16,385,818)


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


def draw(p,im,category: str,t:float,scene_index:int,phase:float,visual:str|None=None):
    # Slow camera drift: starfield and a second independent parallax layer.
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(35):
        x=25+(i*73+(t*(i%3+1)*3))%528
        y=310+(i*83+(t*(i%5+1)*2))%480
        dot(p,d,x,y,.7+(i%3)*.4,BLUE,32+(i%3)*20)
    if category == 'general' and visual is not None:
        from semantic_motion import draw as draw_semantic
        draw_semantic(p,im,visual,t,phase,scene_index)
    else:
        fn=ANIMATORS.get(category,general)
        fn(p,im,t,scene_index,phase)
        # Keep fallback motion only when no useful subject-specific scene exists.
        if category not in ANIMATORS or category == 'general':
            from motion_layers import animate
            animate(p,im,t,scene_index,phase)
    # A physically moving highlight sweeps behind the active diagram.
    x=72+432*(phase**.8)
    path(p,d,[(x,821),(x+12,821)],CYAN,2.8,230)
