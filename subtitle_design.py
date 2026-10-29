"""Narration-synchronised large-format captions for mobile documentary video.

Words stay in fixed chunks, instead of the entire sentence shifting on every
word. A current word is highlighted using provider timestamps. Deliberate
silences hide the panel and do not suggest speech that isn't being spoken.
"""
from __future__ import annotations

from PIL import ImageDraw

WHITE=(244,246,255)
MINT=(113,242,208)
GOLD=(255,201,114)

# Reference layout is 576 x 1024. Keep the bottom ~16% clear for the
# TikTok / Reels / Shorts description and playback controls.
CAPTION_PANEL=(43,726,503,854)
CAPTION_BASELINE=788
CAPTION_UNDERLINE=829
CAPTION_SAFE_BOTTOM=1024-CAPTION_PANEL[3]


def _background(p,image):
    d=ImageDraw.Draw(image,"RGBA")
    a=p.p(CAPTION_PANEL[0],CAPTION_PANEL[1])
    b=p.p(CAPTION_PANEL[2],CAPTION_PANEL[3])
    d.rounded_rectangle(
        (*a,*b),radius=max(10,round(23*p.s)),
        fill=(9,12,28,225),outline=(102,164,165,115),
        width=max(1,round(1.5*p.s)),
    )
    p.line(d,[(64,CAPTION_PANEL[1]+14),(482,CAPTION_PANEL[1]+14)],(*MINT,70),1.5)
    return d


def _chunks(cues):
    """Keep 2–3 spoken words still on screen for each short phrase."""
    groups=[]
    active=[]
    for i,cue in enumerate(cues):
        if active:
            preceding=cues[active[-1]]
            gap=float(cue["start"])-float(preceding["end"])
            punctuation=str(preceding["word"]).rstrip().endswith((".","!","?",":",";"))
            if len(active)>=3 or gap>.42 or punctuation:
                groups.append(active)
                active=[]
        active.append(i)
    if active:
        groups.append(active)
    return groups


def _font_and_widths(p,d,words):
    for size in range(27,14,-1):
        font=p.font(size,True)
        widths=[max(2,d.textbbox((0,0),str(c["word"]),font=font)[2]/p.s) for c in words]
        if sum(widths)+13*max(0,len(widths)-1)<=424:
            return size,widths
    # A single unusually long name must fit the mobile safe area.
    size=14
    font=p.font(size,True)
    widths=[max(2,d.textbbox((0,0),str(c["word"]),font=font)[2]/p.s) for c in words]
    return size,widths


def render_captions(p,image,cues,t,scene_index):
    """Render a stable multiword subtitle group; return whether cues exist."""
    matching=[
        c for c in cues if c.get("scene")==scene_index and str(c.get("word","")).strip()
    ]
    if not matching:
        return False
    selected=next(
        (i for i,c in enumerate(matching) if float(c["start"])<=t<float(c["end"])),
        None,
    )
    if selected is None:
        recent=[
            i for i,c in enumerate(matching)
            if 0<=t-float(c["end"])<=.18
        ]
        if not recent:
            return True
        selected=recent[-1]

    group=next(g for g in _chunks(matching) if selected in g)
    words=[matching[i] for i in group]

    d=_background(p,image)
    size,widths=_font_and_widths(p,d,words)
    total=sum(widths)+13*max(0,len(words)-1)
    left=288-total/2
    if total>430:
        words=[matching[selected]]
        size,widths=_font_and_widths(p,d,words)
        total=sum(widths)
        left=288-total/2

    for cue,width in zip(words,widths):
        is_active=cue is matching[selected]
        xpos=left+width/2
        y=CAPTION_BASELINE
        shadow_alpha=190 if is_active else 145
        p.text(d,cue["word"],xpos+1.2,y+2.2,size,(0,0,0,shadow_alpha),bold=True)
        fill=(*GOLD,255) if is_active else (*WHITE,228)
        p.text(d,cue["word"],xpos,y,size,fill,bold=True)
        if is_active:
            start=float(cue["start"])
            end=float(cue["end"])
            phase=min(1,max(0,(t-start)/max(.025,end-start)))
            x0=left+2
            x1=x0+max(3,width-4)*phase
            p.line(d,[(x0,CAPTION_UNDERLINE),(x1,CAPTION_UNDERLINE)],(*MINT,235),3)
        left+=width+13
    return True


def caption_backdrop(p,image):
    """High contrast when synchronized cues are not yet available."""
    return _background(p,image)
