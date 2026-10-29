"""Cinematic 2D art and mobile captions regression tests.

No static slide can satisfy these: art varies *within* a chapter, camera
motion is controlled, caption groups are fixed and genuinely silent gaps
remain blank.
"""
from __future__ import annotations

import numpy as np
import pytest

from cinematic import camera_parameters, ease, move_camera
from studio import Painter
from topic_engine import research_story
from subtitle_design import _chunks, render_captions
import kinetic


def _story(topic):
    return research_story(topic, fetcher=lambda _: b"{}")


@pytest.mark.parametrize("index", range(8))
def test_camera_paths_are_eased_and_remain_inside_bleed(index):
    scale, pan_x, pan_y = camera_parameters(index, .5)
    assert 1.04 <= scale <= 1.08
    assert -5 <= pan_x <= 5
    assert -5 <= pan_y <= 5
    assert ease(0)==0 and ease(1)==1
    assert ease(.2)<.2 and ease(.8)>.8


def test_camera_transforms_only_art_and_keeps_full_canvas():
    p=Painter(288,512)
    first=move_camera(p,p.base.copy(),0,.05)
    last=move_camera(p,p.base.copy(),0,.95)
    a=np.asarray(first)
    b=np.asarray(last)
    assert a.shape == (512,288,4)
    assert (a!=b).any(axis=2).sum()>1000
    # There can be no fully transparent border pixels after the camera crop.
    for im in (a,b):
        assert np.min(im[:,:,-1])==255


@pytest.mark.parametrize("topic",[
    "What causes earthquakes?",
    "Why do ocean currents move?",
    "How do volcanoes erupt?",
    "Why do planets orbit in our solar system?",
])
def test_each_chapter_has_true_continuous_visual_motion(topic):
    cfg=_story(topic)
    p=Painter(288,512)
    for scene in cfg["scenes"]:
        mid=(float(scene["start"])+float(scene["end"]))/2
        x=np.asarray(p.frame(mid,cfg))
        y=np.asarray(p.frame(mid+.23,cfg))
        change=(x!=y).any(axis=2).sum()
        assert change>250, (topic,scene["headline"],change)


def test_specific_editorial_animations_never_get_unrelated_generic_overlays(monkeypatch):
    import motion_layers
    from kinetic import ANIMATORS
    assert "earthquake" in ANIMATORS and "ocean" in ANIMATORS
    called=[]
    def record(*args,**kwargs):
        called.append(True)
    monkeypatch.setattr(motion_layers,"animate",record)
    p=Painter(288,512)
    kinetic.draw(p,p.base.copy(),"earthquake",2.4,1,.3)
    kinetic.draw(p,p.base.copy(),"ocean",2.4,1,.3)
    assert called == []
    kinetic.draw(p,p.base.copy(),"general",2.4,1,.3)
    assert called == [True]


def test_stable_three_word_subtitles_and_no_ghosting():
    cues=[
        {"scene":0,"word":"Seismic","start":.1,"end":.42},
        {"scene":0,"word":"waves","start":.44,"end":.75},
        {"scene":0,"word":"travel.","start":.78,"end":1.09},
        {"scene":0,"word":"Energy","start":1.2,"end":1.5},
        {"scene":0,"word":"spreads","start":1.55,"end":1.95},
    ]
    assert len(_chunks(cues)) == 2
    assert _chunks(cues)[0] == [0,1,2]
    p=Painter(288,512)
    clean=np.asarray(p.base.copy())
    samples=[]
    for t in (.21,.57,.89):
        im=p.base.copy()
        assert render_captions(p,im,cues,t,0)
        result=np.asarray(im)
        assert (result!=clean).any(axis=2).sum()>1000
        samples.append(result)
    assert (samples[0]!=samples[1]).any(axis=2).sum()>75
    blank=p.base.copy()
    assert render_captions(p,blank,cues,5,0)
    assert np.array_equal(np.asarray(blank),clean)


def test_long_mobile_word_is_renderable_without_text_overflow():
    p=Painter(288,512)
    frame=p.base.copy()
    cues=[{"scene":0,"word":"Electroencephalographically", "start":0, "end":1}]
    assert render_captions(p,frame,cues,.2,0)
    assert np.asarray(frame).std()>8
