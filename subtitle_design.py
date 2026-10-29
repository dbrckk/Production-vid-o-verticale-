"""English documentary captions: mobile-safe contrast and word-level timing.

Unlike slide captions, highlighted words are placed by neural speech timestamps.
The backdrop remains stable while individual word illumination is continuous.
"""
from __future__ import annotations

from PIL import ImageDraw

WHITE=(244,246,255)
MINT=(113,242,208)
GOLD=(255,201,114)


def _background(p, image):
    d=ImageDraw.Draw(image,"RGBA")
    a=p.p(35,801)
    b=p.p(541,917)
    d.rounded_rectangle((*a,*b), radius=max(10,round(21*p.s)),
                        fill=(11,14,30,229),outline=(121,178,176,110),
                        width=max(1,round(1.25*p.s)))
    p.line(d,[(55,815),(521,815)],(*MINT,70),1.1)
    return d


def render_captions(p,image,cues,t,scene_index):
    """Return true when speech cues exist for this scene.

    During pauses over 250ms the text is suppressed, preventing a narrator
    from appearing to speak when the actual waveform has no words.
    """
    matching=[cue for cue in cues if cue.get("scene")==scene_index
              and cue.get("word","").strip()]
    if not matching:
        return False
    selection=next((i for i,cue in enumerate(matching)
                    if cue["start"]<=t<cue["end"]),None)
    if selection is None:
        recent=[i for i,cue in enumerate(matching) if cue["end"]<=t
                and t-cue["end"]<=.25]
        if recent:
            selection=recent[-1]
        else:
            return True
    anchor=matching[selection]
    progress=min(1,max(0,(t-anchor["start"])/max(.01,anchor["end"]-anchor["start"])))
    # Three spoken / upcoming words show useful context without covering artwork.
    left=max(0,selection-2)
    right=min(len(matching),selection+3)
    words=matching[left:right]

    d=_background(p,image)
    base_font=p.font(19,True)
    sizes=[max(2,d.textbbox((0,0),cue["word"],font=base_font)[2]/p.s) for cue in words]
    total=sum(sizes)+13*max(0,len(words)-1)
    if total>461:
        words=[anchor]
        sizes=[max(2,d.textbbox((0,0),anchor["word"],font=base_font)[2]/p.s)]
        total=sum(sizes)
    x=288-total/2
    for cue,width in zip(words,sizes):
        active=cue is anchor
        xpos=x+width/2
        y=857-3*(1-progress)*int(active)
        if active:
            p.text(d,cue["word"],xpos+1,y+2,19,(0,0,0,200),bold=True)
        color=(*GOLD,255) if active else (*WHITE,188 if cue["start"]>t else 240)
        p.text(d,cue["word"],xpos,y,19,color,bold=True)
        x+=width+13
    # Underline shows elapsed progress of the currently spoken word.
    x0=288-min(200,total/2)
    d.line([p.p(x0,889),p.p(x0+min(400,total)*progress,889)],
           fill=(*MINT,215),width=max(2,round(3*p.s)))
    return True


def caption_backdrop(p,image):
    """Contrast panel for unsynchronized/preview narration captions."""
    return _background(p,image)
