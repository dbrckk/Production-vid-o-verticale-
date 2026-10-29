"""Render-focused safe-area captions regressions."""
import numpy as np
from studio import Painter
from subtitle_design import render_captions


CUES=[
    {"scene":0,"word":"Ocean","start":0.1,"end":0.5},
    {"scene":0,"word":"currents","start":0.51,"end":0.95},
    {"scene":0,"word":"move","start":1.4,"end":1.9},
]


def test_captions_appear_only_when_narrator_speaks():
    p=Painter(288,512)
    blank=np.asarray(p.base.copy())
    frame=p.base.copy()
    assert render_captions(p,frame,CUES,.72,0)
    live=np.asarray(frame)
    assert (live!=blank).any(axis=2).sum() > 700

    quiet=p.base.copy()
    assert render_captions(p,quiet,CUES,1.25,0)
    assert np.array_equal(np.asarray(quiet),blank), "No silent karaoke ghosting"

    last=p.base.copy()
    assert render_captions(p,last,CUES,1.6,0)
    assert (np.asarray(last)!=live).any(axis=2).sum()>100


def test_captions_respect_other_scene_and_missing_data():
    p=Painter(288,512)
    frame=p.base.copy()
    assert render_captions(p,frame,CUES,.72,1) is False
    assert np.array_equal(np.asarray(frame),np.asarray(p.base))
