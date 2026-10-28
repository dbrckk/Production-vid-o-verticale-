#!/usr/bin/env python3
"""Deterministic, offline-first 9:16 exponential-scale motion-design studio.

All assets are original procedurally drawn vectors; no web API, paid service, or
copyrighted footage needed. Frames are streamed to FFmpeg (constant memory).
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_W, BASE_H = 576, 1024
PAPER_MM = 0.1
MOON_KM = 384400
LIGHTYEAR_KM = 9460730472580.8
SPACE = (16, 9, 34)
WHITE = (247, 244, 255)
MINT = (102, 241, 197)
GOLD = (255, 191, 107)
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(x: float, lo: float = 0, hi: float = 1) -> float:
    return max(lo, min(hi, x))


def smooth(t: float) -> float:
    t = clamp(t)
    return t * t * (3 - 2 * t)


def thickness_mm(folds: int, initial_mm: float = PAPER_MM) -> float:
    if folds < 0 or initial_mm <= 0:
        raise ValueError('folds must be nonnegative and paper thickness positive')
    return initial_mm * 2**folds


def format_distance(mm: float) -> str:
    if mm < 10:
        return f'{mm:.1f} mm'
    if mm < 1000:
        return f'{mm / 10:.1f} cm'
    if mm < 1e6:
        return f'{mm / 1000:,.1f} m'.replace(',', ' ')
    km = mm / 1e6
    if km < 1e9:
        return f'{km:,.0f} km'.replace(',', ' ')
    ly = km / LIGHTYEAR_KM
    if ly < 1:
        return f'{km / 1e6:,.0f} M km'.replace(',', ' ')
    if ly < 1e6:
        return f'{ly:,.0f} a.l.'.replace(',', ' ')
    return f'{ly / 1e9:,.1f} Md a.l.'.replace(',', ' ')


def fold_at(t: float, cfg: dict) -> int:
    """42-fold reveal, then accelerating cosmic epilogue; stable while paused."""
    start = float(cfg.get('start_at', 0.6))
    reveal = float(cfg.get('reveal_at', 22.0))
    burst = float(cfg.get('burst_at', 24.0))
    end = float(cfg.get('cosmic_end_at', 29.0))
    max_folds = int(cfg.get('max_folds', 103))
    target = min(int(cfg.get('target_folds', 42)), max_folds)
    if t < start:
        return 0
    if t < reveal:
        return min(target, int((t - start) / (reveal - start) * (target + 1)))
    if t < burst:
        return target
    if t < end:
        return min(max_folds, target + int((t - burst) / (end - burst) * (max_folds - target + 1)))
    return max_folds


@dataclass
class Palette:
    mint: tuple[int, int, int] = MINT
    gold: tuple[int, int, int] = GOLD
    white: tuple[int, int, int] = WHITE


class Painter:
    def __init__(self, width: int, height: int):
        if width < 288 or height != width * 16 // 9:
            raise ValueError('Output must be a 9:16 video, width >= 288 and multiple of 9')
        self.width, self.height = width, height
        self.s = width / BASE_W
        self.palette = Palette()
        self.fonts = {}
        self.base = self._background()
        self.stars = self._make_stars()

    def p(self, x: float, y: float) -> tuple[int, int]:
        return (round(x * self.s), round(y * self.s))

    def font(self, size: int, bold: bool = False):
        key = (size, bold)
        if key not in self.fonts:
            path = FONT_BOLD if bold else FONT_REG
            self.fonts[key] = ImageFont.truetype(path, round(size * self.s))
        return self.fonts[key]

    def _background(self) -> Image.Image:
        w, h = self.width, self.height
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        xx /= w
        yy /= h
        center = np.maximum(0, 1 - np.sqrt(((xx - 0.5) * 1.5) ** 2 + ((yy - 0.48) * 1.1) ** 2))
        vignette = np.clip(1 - 0.6 * (((xx - 0.5) / 0.75) ** 2 + ((yy - 0.5) / 0.9) ** 2), 0.25, 1)
        base = np.empty((h, w, 3), dtype=np.uint8)
        for k, (a, b) in enumerate(((10, 26), (7, 13), (22, 46))):
            base[:, :, k] = np.clip((a + b * center) * vignette, 0, 255).astype(np.uint8)
        return Image.fromarray(base, 'RGB').convert('RGBA')

    def _make_stars(self):
        rng = np.random.default_rng(3301)
        return [(float(rng.uniform(10, 566)), float(rng.uniform(290, 840)),
                 float(rng.uniform(.4, 1.6)), float(rng.uniform(0, 6.28))) for _ in range(170)]

    def line(self, d, points, fill, width=1, joint='curve'):
        d.line([self.p(*pt) for pt in points], fill=fill, width=max(1, round(width*self.s)), joint=joint)

    def circle(self, d, x, y, r, fill=None, outline=None, width=1):
        x0,y0=self.p(x-r,y-r);x1,y1=self.p(x+r,y+r)
        d.ellipse((x0,y0,x1,y1),fill=fill,outline=outline,width=max(1,round(width*self.s)))

    def text(self, d, text, x, y, size, fill, anchor='mm', bold=False):
        d.text(self.p(x,y),text,font=self.font(size,bold),anchor=anchor,fill=fill,stroke_width=0)

    def glow_line(self, layer, points, color=GOLD, radius=7, width=3):
        """Multi-pass layered bloom, retains a sharp high-luminance core."""
        d=ImageDraw.Draw(layer,'RGBA')
        for w, a in ((radius*5, 7),(radius*3, 17),(radius*1.6, 40),(width+3, 125)):
            self.line(d, points, (*color,a),w)
        self.line(d, points, (*color,235),width)
        self.line(d, points, (255,250,223,250),max(.8,width/3))

    def glow_disc(self, layer, x, y, r, color=MINT):
        d=ImageDraw.Draw(layer,'RGBA')
        for factor, alpha in ((2.4,9),(1.7,18),(1.25,42)):
            self.circle(d,x,y,r*factor,(*color,alpha))
        self.circle(d,x,y,r,(*color,210))
        self.circle(d,x,y,max(1,r*.42),(255,255,244,245))

    def hud(self, im: Image.Image, t: float, fold: int, cfg: dict):
        d=ImageDraw.Draw(im,'RGBA')
        lines=cfg.get('title_lines', ['Combien de plis pour', 'atteindre la Lune ?'])
        for idx, line in enumerate(lines[:2]):
            self.text(d,line,288,76+29*idx,22,(*WHITE,255),bold=True)
        goal=int(cfg.get('target_folds',42))
        if 22 <= t < 29.7:
            status=cfg.get('reveal_text','Seulement 42 plis !')
            self.text(d,status,288,151,20,(*MINT,255),bold=True)
        else:
            subtitle=f'{fold} plis  =  {format_distance(thickness_mm(fold,float(cfg.get("paper_mm",.1))))}'
            self.text(d,subtitle,288,151,17,(*MINT,245),bold=True)
        self.line(d,[(40,204),(536,204)],(140,135,173,126),2)
        for i in range(11):
            x=40+496*i/10
            self.circle(d,x,204,1.3,(230,215,240,130))
        progress=smooth(clamp(fold/max(goal,1)))
        x=40+496*progress
        self.glow_line(im,[(40,204),(x,204)],MINT,3.5,2.4)
        self.glow_disc(im,x,204,3.5,GOLD)
        self.glow_disc(im,536,204,5.2,(188,174,255))
        self.text(d,'LUNE',536,222,10,(195,176,227,220),bold=True)

    def draw_stars(self, im, t, amount=1):
        d=ImageDraw.Draw(im,'RGBA')
        for x,y,r,phase in self.stars[:round(len(self.stars)*amount)]:
            alpha=int(90+65*(.5+.5*math.sin(phase+t*1.25)))
            self.circle(d,x,y,r,(210,203,255,alpha))

    def ground(self, im, t):
        gl=Image.new('RGBA',im.size,(0,0,0,0))
        self.glow_line(gl,[(0,720),(576,720)],GOLD,4.8,2)
        im.alpha_composite(gl)
        d=ImageDraw.Draw(im,'RGBA')
        for i in range(12):
            dy=8+i*4.5
            alpha=max(0,int(28-i*2.5))
            self.line(d,[(0,720+dy),(576,720+dy)],(*GOLD,alpha),1)
        for i in range(20):
            x=(i*67+34)%576
            self.circle(d,x,710-35*((i*23)%11)/11,0.6,(255,223,173,70))

    def _cat(self,d,x,y,h):
        r=h/3.6
        self.circle(d,x,y-r*1.0,r,None,(*MINT,230),2)
        self.line(d,[(x-r*.83,y-r*1.45),(x-r*.7,y-r*2.3),(x-r*.12,y-r*1.85)],(*MINT,230),2)
        self.line(d,[(x+r*.83,y-r*1.45),(x+r*.7,y-r*2.3),(x+r*.12,y-r*1.85)],(*MINT,230),2)
        self.circle(d,x,y+r*.55,r*.85,None,(*MINT,210),2)
        self.circle(d,x-r*.4,y-r*1.1,1.7,(*MINT,255))
        self.circle(d,x+r*.4,y-r*1.1,1.7,(*MINT,255))
        self.line(d,[(x+r*.8,y+r),(x+r*1.3,y+r*.7),(x+r*1.25,y-r*.3)],(*MINT,170),2)

    def _person(self,d,x,y,h):
        r=h*.085; heady=y-h+r*1.3
        self.circle(d,x,heady,r,None,(*MINT,235),2.5)
        body_y=heady+r*1.8
        self.line(d,[(x,body_y),(x,y-h*.35)],(*MINT,235),5)
        self.line(d,[(x,y-h*.35),(x-h*.13,y)],(*MINT,235),4)
        self.line(d,[(x,y-h*.35),(x+h*.13,y)],(*MINT,235),4)
        self.line(d,[(x,body_y+h*.12),(x-h*.18,body_y+h*.4)],(*MINT,235),4)
        self.line(d,[(x,body_y+h*.12),(x+h*.2,body_y-h*.03)],(*MINT,235),4)

    def _tower(self,d,x,y,h):
        w=h*.30
        self.line(d,[(x-w/2,y),(x,y-h),(x+w/2,y)],(*MINT,215),2.4)
        for j in range(1,9):
            yy=y-h*j/9
            ww=w*(1-j/9)
            self.line(d,[(x-ww/2,yy),(x+ww/2,yy)],(*MINT,175),1)
        self.line(d,[(x-w/2,y),(x+w/2,y)],(*MINT,220),2.2)

    def _house(self,d,x,y,h):
        w=h*1.0
        self.line(d,[(x-w/2,y-h*.62),(x,y-h),(x+w/2,y-h*.62)],(*MINT,230),2)
        self.line(d,[(x-w*.42,y-h*.64),(x-w*.42,y),(x+w*.42,y),(x+w*.42,y-h*.64)],(*MINT,215),2)
        self.line(d,[(x-w*.16,y),(x-w*.16,y-h*.34),(x+w*.06,y-h*.34),(x+w*.06,y)],(*MINT,175),1)
        self.circle(d,x+w*.23,y-h*.43,h*.045,(*GOLD,160))

    def _mountain(self,d,x,y,h):
        pts=[(x-h*.70,y),(x-h*.38,y-h*.58),(x-h*.17,y-h*.35),(x+h*.12,y-h),(x+h*.62,y)]
        self.line(d,pts,(*MINT,210),2)
        self.line(d,[(x+h*.12,y-h),(x-h*.04,y-h*.67),(x+h*.07,y-h*.73)],(238,232,255,190),2)
        for k in range(3):
            self.circle(d,x+40+k*26,y-h*.74+25*k,8,None,(188,189,235,100),1)

    def icon_comparison(self, im, fold, initial_mm):
        # Fixed semantic landmarks, with size indicating relative scale.
        landmarks=[(8,'Dé',16,'dice'),(10,'Tasse',95,'mug'),(12,'Chat',300,'cat'),
                   (14,'Humain',1750,'person'),(18,'Maison',10000,'house'),
                   (22,'Tour Eiffel',330000,'tower'),(26,'Everest',8849000,'mountain')]
        if fold < 8: return
        candidate=max((v for v in landmarks if v[0]<=fold),key=lambda v:v[0])
        first,label,height_mm,kind=candidate
        d=ImageDraw.Draw(im,'RGBA')
        curr_mm=thickness_mm(fold, initial_mm)
        h=clamp(height_mm/curr_mm, .035, 1.9)*248
        h=max(10,min(355,h))
        x,y=186,720
        if kind=='dice':
            w=h*.85
            d.rounded_rectangle((*self.p(x-w/2,y-h),*self.p(x+w/2,y)),radius=round(9*self.s),outline=(*MINT,240),width=max(1,round(2*self.s)),fill=(37,83,75,120))
            for dx,dy in [(-.25,-.25),(.25,.25),(-.25,.25),(.25,-.25)]:self.circle(d,x+dx*w,y-h*.5+dy*h,2.5,(*MINT,245))
        elif kind=='mug':
            w=h*.67; d.rounded_rectangle((*self.p(x-w/2,y-h),*self.p(x+w/2,y)),radius=round(5*self.s),outline=(*MINT,225),width=max(1,round(2*self.s)),fill=(68,49,41,160))
            self.circle(d,x+w*.55,y-h*.54,w*.26,None,(*MINT,185),2)
            for k in range(3):
                self.line(d,[(x-w*.25+k*7,y-h-9),(x-w*.18+k*7,y-h-27)],(*GOLD,110),1.5)
        elif kind=='cat':self._cat(d,x,y,h)
        elif kind=='person':self._person(d,x,y,h)
        elif kind=='house':self._house(d,x,y,h)
        elif kind=='tower':self._tower(d,x,y,h)
        else:self._mountain(d,x,y,h)
        self.text(d,label,x,clamp(y-h-42,345,665),13,(*WHITE,240),bold=True)
        self.text(d,format_distance(height_mm),x,clamp(y-h-23,364,682),11,(*MINT,235))

    def terrestrial(self, im, t, fold, initial_mm):
        self.ground(im,t)
        self.icon_comparison(im,fold,initial_mm)
        # Actual exponential height mapped by a scene-following camera to maintain frame composition.
        h=210+34*math.sin(t*.7)
        if fold<6:h=max(5,8*2**(fold/2))
        x=351; y=720
        gl=Image.new('RGBA',im.size,(0,0,0,0))
        if fold<=4 and t<3:
            # Pivoting paper segment, with consistent hinge and motion trails.
            phase=(t*.5)%1
            for j in range(4,0,-1):
                angle=(phase-j*.09)*math.pi*.52
                self.glow_line(gl,[(x,y),(x+95*math.cos(angle),y-95*math.sin(angle))],GOLD,3.5,2)
            self.glow_line(gl,[(x,y),(x+95*math.cos(phase*math.pi*.52),y-95*math.sin(phase*math.pi*.52))],GOLD,4.5,3)
        else:
            self.glow_line(gl,[(x,y),(x,y-h)],GOLD,8,10)
        im.alpha_composite(gl)
        d=ImageDraw.Draw(im,'RGBA')
        self.text(d,'Chaque pli double l’épaisseur',288,803,17,(*WHITE,235),bold=True)
        self.text(d,'UNE CROISSANCE EXPONENTIELLE',288,839,11,(*MINT,170),bold=True)

    def planet(self, im, x, y, r, moon=False):
        # Crisp vector globe with atmospheric halo, latitudes and procedural landmasses.
        gl=Image.new('RGBA',im.size,(0,0,0,0))
        self.glow_disc(gl,x,y,r,(118,136,255) if not moon else (192,180,233))
        im.alpha_composite(gl)
        d=ImageDraw.Draw(im,'RGBA')
        if moon:
            self.circle(d,x,y,r,(93,87,132,225),(230,218,255,230),1.4)
            for a,b,c in [(-.3,-.2,.18),(.33,.18,.11),(.05,.5,.07)]:
                self.circle(d,x+a*r,y+b*r,c*r,None,(205,191,239,90),1)
            return
        self.circle(d,x,y,r,(19,52,100,250),(104,236,213,240),2)
        for phase in [-.6,0,.6]:
            rr=math.sqrt(max(.1,1-phase*phase))
            self.line(d,[(x-r*rr*math.cos(a/20*math.pi),y+phase*r+r*.05*math.sin(a/5)) for a in range(21)],(67,165,189,105),1)
        for i in [-.55,.0,.55]:
            self.circle(d,x+i*r*.2,y,r*math.sqrt(max(.18,1-i*i)),None,(81,173,203,48),1)
        # Stylised continents, not stock imagery.
        coords=[[(-.7,-.34),(-.46,-.61),(-.20,-.44),(-.25,-.15),(-.11,.04),(-.44,.18)],
                [(.05,-.50),(.48,-.37),(.6,-.12),(.36,.08),(.32,.37),(.1,.46),(-.06,.05)],
                [(-.41,.29),(-.15,.35),(-.06,.68),(-.22,.79)]]
        for pts in coords:
            d.polygon([self.p(x+a*r,y+b*r) for a,b in pts],fill=(34,163,138,150))

    def orbit_scene(self, im, t, fold):
        self.draw_stars(im,t,.85)
        d=ImageDraw.Draw(im,'RGBA')
        k=smooth((t-15)/6)
        cx=230-18*k;cy=713;earth_r=lerp(150,93,k)
        if fold>=36:earth_r=lerp(93,70,smooth((fold-36)/9))
        self.planet(im,cx,cy,earth_r)
        x2=444;moon_y=392
        self.planet(im,x2,moon_y,24,True)
        # Orbital route and vertical beam share the motion vocabulary of the reference.
        for j in range(65):
            theta=j/64*math.pi*1.18-math.pi*.5
            px=cx+210*math.cos(theta);py=cy+205*math.sin(theta)
            if j:
                theta0=(j-1)/64*math.pi*1.18-math.pi*.5
                self.line(d,[(cx+210*math.cos(theta0),cy+205*math.sin(theta0)),(px,py)],(161,155,211,50),1)
        gl=Image.new('RGBA',im.size,(0,0,0,0))
        self.glow_line(gl,[(352,720),(352,465)],GOLD,7,7)
        im.alpha_composite(gl)
        self.text(d,'TERRE',cx,cy+earth_r+34,14,(*MINT,220),bold=True)
        self.text(d,'LUNE',x2,moon_y-45,14,(*WHITE,230),bold=True)
        self.text(d,'384 400 km',x2,moon_y-23,11,(*MINT,200))
        footer='42 plis : plus loin que la Lune !' if t>=22 else 'De l’atmosphère jusqu’à l’espace…'
        self.text(d,footer,288,871,17,(*WHITE,242),bold=True)

    def cosmic(self, im, t, fold):
        self.draw_stars(im,t,1)
        d=ImageDraw.Draw(im,'RGBA')
        phase=clamp((t-24)/5)
        # Radial hyperspace streaks with deterministic positions / acceleration.
        cx,cy=288,543
        count=70
        speed=smooth(phase)
        for i in range(count):
            theta=2*math.pi*i/count+math.sin(i*4.1)*.12
            rr=58+(i*37%310)+70*speed
            le=8+70*speed*((i*29%7)/7+.2)
            color=(140,177,255,int(30+170*speed))
            self.line(d,[(cx+rr*math.cos(theta),cy+rr*math.sin(theta)),(cx+(rr+le)*math.cos(theta),cy+(rr+le)*math.sin(theta))],color,1.5)
        planet_r=lerp(50,117,smooth((t-26)/3))
        self.planet(im,288,730,planet_r)
        gl=Image.new('RGBA',im.size,(0,0,0,0))
        self.glow_line(gl,[(288,728),(288,410)],GOLD,7,6)
        im.alpha_composite(gl)
        if fold < 70:
            scale='LE SOLEIL' if fold<60 else 'ÉTOILES PROCHES'
        elif fold<89: scale='AU-DELÀ DES ÉTOILES'
        elif fold<103:scale='AUTRES GALAXIES'
        else:scale='L’UNIVERS OBSERVABLE'
        self.text(d,scale,288,368,14,(*MINT,235),bold=True)
        self.text(d,f'{fold} PLIS',288,870,23,(*WHITE,252),bold=True)
        self.text(d,format_distance(thickness_mm(fold)),288,909,16,(*MINT,245),bold=True)

    def frame(self, t: float, cfg: dict) -> Image.Image:
        if cfg.get('mode') == 'universal':
            from universal import frame
            return frame(self,t,cfg)
        if cfg.get('mode') == 'storyboard':
            from storyboard import draw_storyboard
            return draw_storyboard(self,t,cfg)
        im=self.base.copy()
        fold=fold_at(t,cfg)
        if t < 14.5:
            self.terrestrial(im,t,fold,float(cfg.get("paper_mm",.1)))
        elif t < 24:
            self.orbit_scene(im,t,fold)
        else:
            self.cosmic(im,t,fold)
        self.hud(im,t,fold,cfg)
        if t>=29.8:
            # Final legibility hold & subtle fade rather than external platform outro.
            d=ImageDraw.Draw(im,'RGBA')
            self.text(d,'42 PLIS POUR ATTEINDRE LA LUNE',288,963,12,(*WHITE,205),bold=True)
        return im.convert('RGB')


def make_audio(path: Path, duration: float, cfg: dict):
    """Original ambient pulse + scale-dependent rising sweeps, deterministic WAV."""
    import wave
    sr=24000
    n=round(duration*sr)
    arr=np.zeros(n,np.float32)
    chords=[(146.83,174.61,220.0),(130.81,164.81,196.0),(110.0,146.83,174.61),(130.81,164.81,220.0)]
    for start in np.arange(0,duration,4):
        a=int(start*sr);b=min(n,a+sr*4)
        tt=np.arange(b-a,dtype=np.float32)/sr
        # Smooth drifting original ambient chord.
        env=np.minimum(1,tt/.55)*np.minimum(1,(4-tt)/.65)
        for j,f in enumerate(chords[int(start//4)%4]):
            arr[a:b]+=(.035/(j+1)) *np.sin(2*np.pi*f*tt+0.15*np.sin(tt*1.1))*env
    for beat in np.arange(.6,duration-.2,.5):
        a=int(beat*sr);b=min(n,a+int(.11*sr));tt=np.arange(b-a,dtype=np.float32)/sr
        # Soft synthesized tick with no external sound samples.
        arr[a:b]+=(.12*np.sin(2*np.pi*(380+1500*tt)*tt)+.035*np.sin(2*np.pi*880*tt))*np.exp(-tt*38)
    markers = ([float(scene['start']) for scene in cfg['scenes'][1:]]
               if cfg.get('mode') in ('storyboard','universal') else [7.5,14.5,21.8,24.0,28.5])
    for when in markers:
        a=int(when*sr);b=min(n,a+int(.8*sr));tt=np.arange(b-a,dtype=np.float32)/sr
        arr[a:b]+=.10*np.sin(2*np.pi*(170*tt+300*tt**2))*np.sin(np.pi*np.minimum(1,tt/.8))
    arr=np.tanh(arr*2.6)*.85
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
        wav.writeframes((arr*32767).astype('<i2').tobytes())


def render(cfg:dict, output:Path, width:int=1080, fps:int=30, duration:float|None=None,
           preview:bool=False, voice:Path|None=None):
    duration=duration or float(cfg.get('duration',31))
    if duration<=0 or fps<1:raise ValueError('duration and fps must be positive')
    if width%9:raise ValueError('width must be a multiple of 9 for exact 9:16')
    height=width*16//9
    if cfg.get('mode') == 'universal':
        from topic_engine import validate_universal
        validate_universal(cfg)
    elif cfg.get('mode') == 'storyboard':
        from storyboard import validate_storyboard
        validate_storyboard(cfg)
    elif cfg.get('mode', 'paper') != 'paper':
        raise ValueError('Unknown video mode')
    elif float(cfg.get("paper_mm", PAPER_MM)) <= 0:
        raise ValueError("paper_mm must be positive")
    painter=Painter(width,height)
    output.parent.mkdir(parents=True,exist_ok=True)
    audio=output.with_suffix('.sound.wav')
    make_audio(audio,duration,cfg)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-i',str(audio)]
    if voice:
        if not voice.exists():raise FileNotFoundError(voice)
        cmd+=['-i',str(voice),'-filter_complex','[1:a]volume=0.35[bed];[bed][2:a]amix=inputs=2:duration=first:dropout_transition=0[a]','-map','0:v','-map','[a]']
    else:cmd+=['-map','0:v','-map','1:a']
    cmd+=['-c:v','libx264','-preset','medium' if not preview else 'veryfast',
          '-crf','18' if not preview else '21','-pix_fmt','yuv420p','-movflags','+faststart',
          '-c:a','aac','-b:a','192k','-t',str(duration),str(output)]
    frames=round(duration*fps)
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for index in range(frames):
            proc.stdin.write(painter.frame(index/fps,cfg).tobytes())
            if index%max(1,5*fps)==0:print(f'frame {index+1}/{frames}',flush=True)
        proc.stdin.close()
        error=proc.stderr.read().decode('utf-8','replace')
        if proc.wait()!=0:raise RuntimeError(f'FFmpeg render failed: {error}')
    except Exception:
        proc.kill();proc.wait()
        raise
    finally:
        audio.unlink(missing_ok=True)
    if not output.exists() or output.stat().st_size<1000:
        raise RuntimeError('Rendered video missing or empty')
    cover=output.with_name('cover.png')
    painter.frame(min(7.3,duration*.45),cfg).save(cover)
    info={'output':str(output),'cover':str(cover),'width':width,'height':height,'fps':fps,
          'duration':duration,'frames':frames,'mode':cfg.get('mode','paper')}
    if info['mode']=='universal':
        info.update(topic=cfg['topic'],evidence=cfg.get('evidence','unsourced'),
                    sources=cfg.get('sources',[]),scenes=cfg['scenes'])
    elif info['mode']=='storyboard':
        info['scenes']=[{'start':scene['start'],'end':scene['end'],'headline':scene['headline'],
                         'visual':scene['visual']} for scene in cfg['scenes']]
    else:
        info.update(target_folds=cfg.get('target_folds',42),moon_distance_km=MOON_KM,
                    fold42_distance_km=thickness_mm(42)/1e6)
    output.with_suffix('.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
    return info


def main():
    p=argparse.ArgumentParser(description='Offline 9:16 scientific motion-video studio')
    p.add_argument('--config',default='presets/paper-to-moon.json')
    p.add_argument('--output',default='output/science.mp4')
    p.add_argument('--width',type=int,default=1080)
    p.add_argument('--fps',type=int,default=30)
    p.add_argument('--duration',type=float)
    p.add_argument('--title',type=str,help='Replace first line of the title')
    p.add_argument('--voice',type=Path,help='Optional owned narration audio file')
    p.add_argument('--preview',action='store_true',help='Fast encoding (resolution still configurable)')
    a=p.parse_args()
    cfg=json.loads(Path(a.config).read_text(encoding='utf8'))
    if a.title:
        if cfg.get('mode') in ('storyboard','universal'):
            cfg['scenes'][0]['headline'] = a.title[:200]
        else:
            cfg['title_lines'] = [a.title, *cfg['title_lines'][1:]]
    print(json.dumps(render(cfg,Path(a.output),a.width,a.fps,a.duration,a.preview,a.voice),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
