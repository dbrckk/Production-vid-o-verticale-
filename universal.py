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
    p.text(d,'CONTINUE WATCHING',288,y,15,(*color,240),bold=True)

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

def topic_category(topic: str) -> str:
    text=topic.casefold()
    categories=(
        ('ocean',('océan','mer ','vague','marin','ocean','sea ','corail','plage','eau ')),
        ('volcano',('volcan','magma','lave','eruption','éruption')),
        ('space',('soleil','planète','lune','galax','espace','astron','univers','satellite','mars')),
        ('health',('santé','médec','soin','cœur','coeur','virus','health','vaccin','maladie')),
        ('tech',('informat','numéri','intelligence artificielle','logiciel','robot','ia ','technolog','ordinateur','cyber')),
        ('economy',('économie','budget','argent','entreprise','bourse','trade','prix','inflation','finance')),
    )
    for category,keys in categories:
        if any(k in text for k in keys):return category
    return 'general'

def topic_symbol(p,im,category,phase):
    """Distinct topic-led procedural motifs. No stock imagery, no external models."""
    if category=='general':return
    d=ImageDraw.Draw(im,'RGBA')
    x,y=288,579
    if category=='ocean':
        for row in range(4):
            yy=y-70+row*54
            points=[(65+k*9,yy+11*math.sin(k*.31+phase*math.tau+row*.7)) for k in range(51)]
            p.glow_line(im,points,MINT if row%2==0 else BLUE,3.8,2)
        p.circle(d,420,493,27,(233,191,111,135),(255,216,128,230),1.7)
    elif category=='volcano':
        p.line(d,[(70,724),(197,588),(252,520),(314,520),(370,593),(505,724)],(*MINT,230),4)
        p.glow_line(im,[(288,520),(272,570),(242,613),(230,710)],GOLD,8,6)
        for k in range(22):
            px=x+math.sin(k*2.4)*max(8,95-k*2)
            py=506-k*7+(phase*42)%28
            p.circle(d,px,py,1.5+(k%3),(*GOLD,160))
    elif category=='space':
        p.planet(im,x,y,117)
        p.circle(d,x,y,170,None,(*BLUE,170),1.7)
        for i in range(14):
            angle=i*math.tau/14+phase*.4
            p.glow_disc(im,x+170*math.cos(angle),y+170*math.sin(angle),2,MINT)
    elif category=='health':
        points=[(73,560),(168,560),(204,530),(233,626),(276,470),(317,573),(355,550),(500,550)]
        p.glow_line(im,points,MINT,5,3.7)
        for r in range(3):
            p.circle(d,x,y,140+r*29,None,(*BLUE,90-r*23),1.3)
    elif category=='tech':
        p.circle(d,x,y,115,(21,29,55,215),(*MINT,220),2)
        for i in range(8):
            offset=-89+i*26
            p.line(d,[(x+offset,y-150),(x+offset,y-114)],(*BLUE,160),2)
            p.line(d,[(x+offset,y+114),(x+offset,y+150)],(*BLUE,160),2)
            p.line(d,[(x-150,y+offset),(x-114,y+offset)],(*BLUE,160),2)
            p.line(d,[(x+114,y+offset),(x+150,y+offset)],(*BLUE,160),2)
        p.glow_line(im,[(245,580),(272,610),(321,545)],GOLD,5,4)
    elif category=='economy':
        points=[(90,696),(156,645),(226,670),(291,562),(355,596),(420,504),(489,436)]
        p.glow_line(im,points,MINT,6,3)
        for px,py in points:p.glow_disc(im,px,py,5,GOLD)
        p.line(d,[(84,732),(502,732)],(*BLUE,100),1.5)

def frame(p,t:float,cfg:dict):
    """True continuous animation and synced spoken-word captions."""
    from kinetic import draw
    scenes=cfg['scenes']
    ix=next((i for i,s in enumerate(scenes) if t<float(s['end'])),len(scenes)-1)
    scene=scenes[ix]
    start,end=float(scene['start']),float(scene['end'])
    phase=max(0,min(1,(t-start)/max(.001,end-start)))
    im=p.base.copy()
    category=topic_category(cfg['topic'])
    draw(p,im,category,t,ix,phase)
    d=ImageDraw.Draw(im,'RGBA')
    p.text(d,'ENGLISH  /  MOTION DOCUMENTARY',288,64,12,(*MINT,230),bold=True)
    # The title reveals smoothly as narration begins; it never jumps between slides.
    alpha=round(245*min(1,(t-start)/.30)) if ix else 245
    title=scene['headline']
    # Hide the title during the opening few frames rather than drawing static slides.
    if alpha>0:
        _wrap(p,d,title,157,size=27,max_lines=3,bold=True,color=LIGHT)
    p.line(d,[(48,255),(528,255)],(*BLUE,95),2)
    p.glow_line(im,[(48,255),(48+480*min(t/float(cfg['duration']),1),255)],MINT,3.1,2.1)
    p.glow_disc(im,48+480*min(t/float(cfg['duration']),1),255,3,GOLD)
    d=ImageDraw.Draw(im,'RGBA')
    if scene.get('metric'):
        _wrap(p,d,scene['metric'],322,size=14,max_lines=2,color=MINT,bold=True)
    # Voice-driven karaoke. Falls back to English scene captions for silent preview.
    cues=cfg.get('word_cues') or []
    if cues:
        matching=[c for c in cues if c['scene']==ix]
        selected=next((i for i,c in enumerate(matching) if c['start']<=t<c['end']),None)
        if selected is None:
            selected=next((i for i,c in enumerate(matching) if t<c['start']),len(matching)-1)
        if matching and selected>=0:
            lo=max(0,selected-2);hi=min(len(matching),selected+3)
            block=matching[lo:hi]
            widths=[d.textbbox((0,0),c['word'],font=p.font(18,True))[2]/p.s for c in block]
            total=sum(widths)+12*max(0,len(block)-1)
            if total>516:
                block=[matching[selected]]
                widths=[d.textbbox((0,0),block[0]['word'],font=p.font(18,True))[2]/p.s]
                total=sum(widths)
            x=288-total/2
            for c,w in zip(block,widths):
                p.text(d,c['word'],x+w/2,858,18,(*(GOLD if c is matching[selected] else LIGHT),255),bold=True)
                x+=w+12
    else:
        _wrap(p,d,scene['caption'],858,size=19,max_lines=4)
    p.text(d,f'{ix+1:02d} / {len(scenes):02d}',288,969,12,(*LIGHT,165),bold=True)
    return im.convert('RGB')
