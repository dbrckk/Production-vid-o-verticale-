"""Data-driven astronomy storyboard renderer. All imagery is procedural and offline."""
from __future__ import annotations

import math
from PIL import Image, ImageDraw

ALLOWED_VISUALS = frozenset({'sun', 'light_path', 'countdown', 'orbit', 'ice', 'galaxy'})
INK = (247, 244, 255)
CYAN = (102, 241, 197)
AMBER = (255, 191, 107)


def validate_storyboard(cfg: dict) -> None:
    if cfg.get('mode') != 'storyboard':
        raise ValueError('mode must be storyboard')
    duration = float(cfg.get('duration', 0))
    scenes = cfg.get('scenes')
    if not math.isfinite(duration) or not 1 <= duration <= 180 or not isinstance(scenes, list) or not scenes:
        raise ValueError('Storyboard requires a duration (1-180s) and scenes')
    previous = 0.0
    for scene in scenes:
        if not isinstance(scene, dict) or scene.get('visual') not in ALLOWED_VISUALS:
            raise ValueError('Invalid scene or visual')
        start, end = float(scene.get('start', -1)), float(scene.get('end', -1))
        if not math.isfinite(start) or not math.isfinite(end) or abs(start - previous) > .0001 or end <= start or end > duration + .0001:
            raise ValueError('Scenes must cover the timeline without gaps or overlaps')
        for key in ('headline', 'caption'):
            val = scene.get(key)
            if not isinstance(val, str) or not val.strip() or len(val) > 240:
                raise ValueError('Each scene needs a nonempty headline and caption (max 240 chars)')
        previous = end
    if abs(previous - duration) > .0001:
        raise ValueError('Last scene must end at duration')


def scene_at(cfg: dict, t: float):
    scenes = cfg['scenes']
    for i, scene in enumerate(scenes):
        if t < float(scene['end']):
            return i, scene
    return len(scenes)-1, scenes[-1]


def write_lines(p, d, text: str, x: float, center_y: float, max_width: float,
                max_lines: int, size: int, fill, bold=False):
    """Pixel-measured wrapping; shrink font to remain within phone-safe margins."""
    words = text.split()
    if not words:
        return
    for font_size in range(size, 11, -1):
        font = p.font(font_size, bold)
        lines = []
        current = ''
        for word in words:
            proposal = (current + ' ' + word).strip()
            if d.textbbox((0,0), proposal, font=font)[2] / p.s > max_width and current:
                lines.append(current)
                current = word
            else:
                current = proposal
        if current:
            lines.append(current)
        if len(lines) <= max_lines and all(d.textbbox((0,0), line, font=font)[2] / p.s <= max_width for line in lines):
            line_height = font_size * 1.42
            for k, line in enumerate(lines):
                p.text(d, line, x, center_y + (k - (len(lines)-1)/2)*line_height, font_size, fill, bold=bold)
            return
    raise ValueError('Text is too long to fit safely: ' + text[:70])


def sun(p, im, x, y, r, t, opacity=1.0):
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    d = ImageDraw.Draw(layer, 'RGBA')
    gold = (255, 174, 70)
    p.glow_disc(layer,x,y,r,gold)
    d = ImageDraw.Draw(layer, 'RGBA')
    for n in range(30):
        a = n*2*math.pi/30+t*.05
        length = r*(1.22 + .10*math.sin(t*2.3+n))
        p.line(d, [(x+math.cos(a)*r*1.06,y+math.sin(a)*r*1.06),
                    (x+math.cos(a)*length,y+math.sin(a)*length)],
               (255,170,73,110),2.2)
    p.circle(d,x,y,r,(255,143,56,255),(255,220,138,255),2)
    for n in range(7):
        a = n*2*math.pi/7 + t*.2
        p.circle(d,x+math.cos(a)*r*.57,y+math.sin(a)*r*.57,r*.09,None,(255,220,149,110),1.3)
    if opacity != 1.0:
        layer.putalpha(layer.getchannel('A').point(lambda v:round(v*opacity)))
    im.alpha_composite(layer)


def earth(p, im, x, y, r, frozen=False, night=False):
    # Painter owns the vector Earth with original procedural continents and rings.
    p.planet(im,x,y,r)
    d = ImageDraw.Draw(im,'RGBA')
    if night:
        p.circle(d,x,y,r*.96,(8,13,42,175))
        for n in range(16):
            a=n*2.4
            px=x+r*.70*math.sin(a);py=y+r*.63*math.cos(a)
            p.circle(d,px,py,1.5,(255,212,118,190))
    if frozen:
        p.circle(d,x,y,r*.96,(127,207,244,110),(197,242,255,230),2)
        for n in range(8):
            a=n*2*math.pi/8
            qx=x+.65*r*math.cos(a); qy=y+.65*r*math.sin(a)
            p.line(d,[(qx-r*.18,qy-r*.1),(qx,qy),(qx+r*.13,qy-r*.07)],
                  (215,251,255,195),2)


def visual(p, im, kind: str, t: float, phase: float):
    d = ImageDraw.Draw(im,'RGBA')
    if kind == 'sun':
        p.draw_stars(im,t,.45)
        sun(p,im,288,568,124,t)
        for i in range(3):
            p.circle(d,288,568,166+i*35+5*math.sin(t*.6+i),
                     None,(245,171,99,65-15*i),1.3)
    elif kind == 'light_path':
        p.draw_stars(im,t,.65)
        sun(p,im,113,576,57,t)
        earth(p,im,464,576,48)
        p.line(d,[(165,576),(408,576)],(129,170,195,100),1.7)
        for n in range(11):
            v = ((n/11+phase*2.6)%1)
            x = 169+v*239
            p.glow_disc(im,x,576,2.1,(255,222,116))
        write_lines(p,d,'149,6 MILLIONS DE KM',288,748,470,1,17,(*CYAN,250),True)
    elif kind == 'countdown':
        p.draw_stars(im,t,.65)
        earth(p,im,288,584,102,night=phase>.50)
        for i in range(20):
            a=(i/20)*math.tau
            p.circle(d,288+150*math.sin(a),584+150*math.cos(a),1.5,(*CYAN,150))
        # A visual countdown arc, not a claim that story seconds equal physical minutes.
        x0,y0=p.p(288-162,584-162);x1,y1=p.p(288+162,584+162)
        d.arc((x0,y0,x1,y1),start=-90,end=-90+max(1,round(360*phase)),
              fill=(*AMBER,235),width=max(2,round(5*p.s)))
        write_lines(p,d,'8 min 20 s',288,769,475,1,28,(*CYAN,255),True)
    elif kind == 'orbit':
        p.draw_stars(im,t,.85)
        sun(p,im,185,556,47,t,opacity=.28)
        x0,y0=p.p(55,393);x1,y1=p.p(515,768)
        d.arc((x0,y0,x1,y1),start=203,end=353,fill=(137,150,218,185),width=max(1,round(2*p.s)))
        px=292+phase*188
        py=640-phase*145
        earth(p,im,px,py,39,night=True)
        p.glow_line(im,[(px-95,py+74),(px+65,py-53)],CYAN,3.8,2)
        write_lines(p,d,'LA TERRE POURSUIT SA ROUTE',288,787,495,2,17,(*CYAN,245),True)
    elif kind == 'ice':
        p.draw_stars(im,t,.8)
        earth(p,im,288,583,124,frozen=True,night=True)
        for i in range(55):
            a=(i*97.3)%360
            rr=144+(i*17%125)
            sx=288+rr*math.cos(math.radians(a)+t*.035)
            sy=583+rr*math.sin(math.radians(a))+t*(i%3+1)*3
            p.circle(d,sx,sy,1+(i%3)*.5,(191,238,255,135))
        write_lines(p,d,'UN REFROIDISSEMENT PROGRESSIF',288,788,495,2,15,(202,242,255,250),True)
    elif kind == 'galaxy':
        p.draw_stars(im,t,1)
        for n in range(90):
            a=n*2.399+phase*.38
            rr=10+(n/90)**.7*230
            p.circle(d,288+math.cos(a)*rr,559+math.sin(a)*rr*.7,
                     1.6+(n%3)*.5,(159,178,255,65+n%3*35))
        earth(p,im,288,559,54,night=True)
        p.glow_line(im,[(246,618),(330,618)],CYAN,4,2)
    else:
        raise ValueError('Unsupported visual: ' + kind)


def draw_storyboard(p, t: float, cfg: dict):
    """Smooth crossfade of entire vector scenes; HUD never contains hardcoded paper labels."""
    ix, scene = scene_at(cfg,t)
    start,end = float(scene['start']),float(scene['end'])
    phase=max(0,min(1,(t-start)/(end-start)))
    im = p.base.copy()
    visual(p,im,scene['visual'],t,phase)
    fade = min(1,(t-start)/.45) if ix else 1
    if ix and fade < 1:
        previous = p.base.copy()
        visual(p,previous,cfg['scenes'][ix-1]['visual'],t,1)
        im = Image.blend(previous,im,fade)
    d=ImageDraw.Draw(im,'RGBA')
    # Header and safe margins match the parent 9:16 design vocabulary.
    p.text(d, f'SCIENCE  /  EXPLIQUÉE EN {float(cfg["duration"]):g} S',288,62,13,(*CYAN,180),bold=True)
    write_lines(p,d,scene['headline'],288,160,490,3,26,(*INK,250),True)
    p.line(d,[(60,247),(516,247)],(148,145,186,120),2)
    prog=60+456*(min(t,float(cfg['duration']))/float(cfg['duration']))
    p.glow_line(im,[(60,247),(prog,247)],CYAN,3,2)
    p.glow_disc(im,prog,247,3,AMBER)
    d=ImageDraw.Draw(im,'RGBA')
    write_lines(p,d,scene['caption'],288,862,490,3,21,(*INK,245),False)
    stamp=scene.get('metric')
    if stamp:
        write_lines(p,d,str(stamp),288,315,480,2,19,(*CYAN,245),True)
    p.text(d,f'{ix+1:02d}  /  {len(cfg["scenes"]):02d}',288,961,11,(165,155,197,185),bold=True)
    return im.convert('RGB')
