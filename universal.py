"""Original vector motion design usable for any topic, without external assets."""
from __future__ import annotations
import hashlib
import math
from PIL import Image,ImageDraw
LIGHT=(245,247,255)
MINT=(96,238,202)
GOLD=(251,188,104)
BLUE=(117,160,246)

def _wrap(p,d,text,y,*,size=24,max_lines=4,color=LIGHT,bold=False):
    words=text.split()
    for sz in range(size,11,-1):
        font=p.font(sz,bold)
        lines=[];line=''
        for word in words:
            candidate=f'{line} {word}'.strip()
            if d.textbbox((0,0),candidate,font=font)[2]>492*p.s and line:
                lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        if len(lines)<=max_lines and all(d.textbbox((0,0),s,font=font)[2]<=492*p.s for s in lines):
            for i,s in enumerate(lines):
                p.text(d,s,288,y+(i-(len(lines)-1)/2)*sz*1.48,sz,(*color,250),bold=bold)
            return
    p.text(d,'SUJET LONG : VOIR DESCRIPTION',288,y,15,(*color,240),bold=True)

def _geometry(p,im,kind,phase,seed):
    d=ImageDraw.Draw(im,'RGBA')
    cx,cy=288,578
    p.draw_stars(im,phase*4,.42)
    if kind=='focus':
        for ring in range(3):
            rad=111+ring*42+math.sin(phase*math.tau)*4
            p.circle(d,cx,cy,rad,None,(*BLUE,max(35,120-30*ring)),1.8)
        for k in range(10):
            a=k*math.tau/10+phase*.45
            px=cx+182*math.cos(a);py=cy+182*math.sin(a)
            p.glow_disc(im,px,py,3,MINT if k%3 else GOLD)
        p.glow_disc(im,cx,cy,52,GOLD)
        p.circle(d,cx,cy,33,(229,161,74,130),(255,219,128,255),2.5)
        for i in range(7):
            a=(i+1)*.83
            p.circle(d,cx+30*math.cos(a),cy+30*math.sin(a),4,(255,242,198,180))
    elif kind=='globe':
        p.planet(im,cx,cy,140)
        for k in range(3):p.circle(d,cx,cy,154+k*26,None,(*BLUE,110-k*30),1)
        for i in range(4):
            a=i*math.tau/4+phase*.6
            p.glow_disc(im,cx+170*math.cos(a),cy+170*math.sin(a),3,MINT)
    elif kind=='timeline':
        points=[(85+i*100,500+math.sin(seed+i*1.8)*40) for i in range(5)]
        p.glow_line(im,points,MINT,5,2)
        for i,(x,y) in enumerate(points):
            p.glow_disc(im,x,y,7,GOLD if i%2==0 else MINT)
            p.text(d,f'{i+1:02d}',x,y+42,14,(*LIGHT,235),bold=True)
        p.line(d,[(75,700),(505,700)],(120,135,192,140),1)
        for i in range(5):p.circle(d,85+i*100,700,2,(*BLUE,170))
    elif kind=='network':
        nodes=[]
        for i in range(9):
            a=math.tau*i/9+phase*.25
            rr=125+24*math.sin(i*2.5+seed)
            nodes.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
        for i,xy in enumerate(nodes):
            for other in (nodes[(i+1)%9],nodes[(i+3)%9]):
                p.line(d,[xy,other],(*BLUE,70),1.4)
        for i,(x,y) in enumerate(nodes):p.glow_disc(im,x,y,6,GOLD if i%3==0 else MINT)
        p.glow_disc(im,cx,cy,22,GOLD)
        for xy in nodes[::2]:p.line(d,[(cx,cy),xy],(*MINT,95),1.2)
    elif kind=='compare':
        values=[(seed*13+i*17)%94+21 for i in range(5)]
        for i,v in enumerate(values):
            x=95+i*95;y=760-v*3
            p.glow_line(im,[(x,760),(x,y)],MINT if i%2 else GOLD,5,13)
            p.circle(d,x,y,7,(*LIGHT,255))
        p.line(d,[(66,760),(509,760)],(*BLUE,200),2)
        for r in range(4):
            y=400+r*80
            p.line(d,[(65,y),(509,y)],(*BLUE,30),1)
    elif kind=='question':
        p.glow_disc(im,cx,cy,92,GOLD)
        p.circle(d,cx,cy,132,None,(*MINT,155),2)
        for i in range(12):
            a=i*math.tau/12+phase*.14
            p.glow_disc(im,cx+157*math.cos(a),cy+157*math.sin(a),2,MINT)
        p.text(d,'?',cx,cy,151,(*LIGHT,255),bold=True)

def frame(p,t:float,cfg:dict):
    scenes=cfg['scenes']
    ix=next((i for i,s in enumerate(scenes) if t<float(s['end'])),len(scenes)-1)
    scene=scenes[ix]
    start,end=float(scene['start']),float(scene['end'])
    phase=max(0,min(1,(t-start)/(end-start)))
    seed=int(hashlib.sha256(cfg['topic'].encode()).hexdigest()[:8],16)%101
    im=p.base.copy()
    _geometry(p,im,scene['visual'],phase,seed)
    if ix and phase<.08:
        old=p.base.copy()
        _geometry(p,old,scenes[ix-1]['visual'],1,seed)
        im=Image.blend(old,im,phase/.08)
    d=ImageDraw.Draw(im,'RGBA')
    p.text(d,'VERTICAL  /  EXPLAINER',288,64,13,(*MINT,235),bold=True)
    _wrap(p,d,scene['headline'],161,size=28,max_lines=3,bold=True)
    p.line(d,[(48,255),(528,255)],(*BLUE,95),2)
    p.glow_line(im,[(48,255),(48+480*min(t/float(cfg['duration']),1),255)],MINT,3.1,2.1)
    p.glow_disc(im,48+480*min(t/float(cfg['duration']),1),255,3,GOLD)
    d=ImageDraw.Draw(im,'RGBA')
    if scene.get('metric'):_wrap(p,d,scene['metric'],323,size=15,max_lines=2,color=MINT,bold=True)
    _wrap(p,d,scene['caption'],860,size=20,max_lines=4)
    p.text(d,f'{ix+1:02d} / {len(scenes):02d}',288,968,12,(*LIGHT,165),bold=True)
    return im.convert('RGB')
