"""Volcanic physical-sequence QA: staged visuals and non-repeated scenes."""
from __future__ import annotations
import numpy as np
from studio import Painter
from volcano_story import draw
from subject_illustrations import volcanic_structure


def test_six_volcanic_chapters_are_visually_distinct():
    p=Painter(288,512)
    views=[]
    for index in range(6):
        frame=p.base.copy()
        draw(p,frame,2.25+index*.7,index,.55)
        views.append(np.asarray(frame)[175:422,22:260,:3].copy())
    for index in range(5):
        # Compare only the scientific artwork, ignoring titles and subtitles.
        pixels=(np.abs(views[index].astype(np.int16)-views[index+1].astype(np.int16))>18)
        ratio=pixels.any(axis=2).mean()
        assert ratio>.022,(index,ratio)


def test_volcano_physics_updates_at_60_fps_within_all_six_chapters():
    p=Painter(288,512)
    for index in range(6):
        a=p.base.copy()
        b=p.base.copy()
        draw(p,a,2.5,index,.45)
        draw(p,b,2.5+1/60,index,.45+1/240)
        first=np.asarray(a).astype(np.int16)
        second=np.asarray(b).astype(np.int16)
        assert np.any(first!=second),(index,"frozen scene")


def test_before_eruption_crater_is_not_a_live_lava_flow():
    p=Painter(288,512)
    sealed=p.base.copy()
    erupting=p.base.copy()
    volcanic_structure(p,sealed,2.2,0)
    volcanic_structure(p,erupting,2.2,4)
    # During storage the geology cannot already have visible external lava
    # following both slopes, as it does in the eruption segment.
    a=np.asarray(sealed)[320:430,65:250,:3].astype(np.int16)
    b=np.asarray(erupting)[320:430,65:250,:3].astype(np.int16)
    assert (np.abs(a-b)>20).any(axis=2).mean()>.012
