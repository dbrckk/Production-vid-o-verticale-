"""Publishable photosynthesis movie: six genuinely different moving scenes."""
import numpy as np
from studio import Painter
from biology_story import SCENES, draw
from topic_engine import research_story


def test_science_script_is_subject_specific_english_and_not_generic():
    story=research_story("How does photosynthesis turn sunlight into food?")
    assert story["motion_category"]=="biology"
    assert story["editorial_template"]=="photosynthesis"
    assert len(story["scenes"])==6
    narration=" ".join(s["narration"].lower() for s in story["scenes"])
    for term in ("sunlight","roots","carbon dioxide","sugars","oxygen"):
        assert term in narration


def test_each_photosynthesis_scene_has_distinct_bespoke_illustration():
    assert len(SCENES)==6
    p=Painter(288,512)
    frames=[]
    for index in range(6):
        im=p.base.copy()
        draw(p,im,t=index+1.25,scene_index=index,phase=.5)
        assert im.size==(288,512)
        frames.append(np.asarray(im.convert("RGB"))[175:365,22:264].astype(np.int16))
    for left,right in zip(frames,frames[1:]):
        assert np.abs(left-right).mean()>2.0


def test_photon_molecules_and_leaves_animate_between_adjacent_frames():
    p=Painter(288,512)
    for index in range(6):
        a=p.base.copy()
        b=p.base.copy()
        draw(p,a,3.0,index,.4)
        draw(p,b,3.0+1/60,index,.4+1/360)
        first=np.asarray(a.convert("RGB"))[175:365,22:264].astype(np.int16)
        second=np.asarray(b.convert("RGB"))[175:365,22:264].astype(np.int16)
        assert np.abs(first-second).sum()>0,(index,"static scene")
