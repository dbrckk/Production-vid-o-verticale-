"""Regression tests for newly authored ocean and volcano animation detail.

Prove light is cached, subjects retain different cinematic palettes, and
60-FPS time steps change the actual illustrated geometry rather than slides.
"""
from __future__ import annotations
import numpy as np
from PIL import ImageDraw
import pytest

from studio import Painter
from scene_backdrops import environment
from subject_illustrations import fish, volcanic_structure
from topic_engine import research_story


@pytest.mark.parametrize("category",["ocean","earthquake","volcano","space","weather","biology"])
def test_atmosphere_is_opaque_cached_and_category_specific(category):
    painter=Painter(288,512)
    first=environment(painter,category)
    second=environment(painter,category)
    assert first.size==(288,512) and second.size==first.size
    assert painter._cinematic_backdrops[category] is not first
    assert len(painter._cinematic_backdrops)==1
    assert np.asarray(first)[:,:,-1].min()==255
    assert np.array_equal(np.asarray(first),np.asarray(second))
    first.putpixel((0,0),(255,0,0,255))
    assert np.asarray(environment(painter,category))[0,0,0]!=255


@pytest.mark.parametrize(("topic","category"),[
    ("Why do ocean currents move?","ocean"),
    ("Why do volcanoes erupt?","volcano"),
    ("What causes earthquakes?","earthquake"),
])
def test_curated_scene_has_rich_layered_continuous_motion(topic,category):
    cfg=research_story(topic,fetcher=lambda _:b"{}")
    p=Painter(288,512)
    frames=[]
    for time in (1.00,1.0167,1.0333):
        frame=np.asarray(p.frame(time,cfg))
        frames.append(frame)
    region=frames[0][193:417,22:265]
    assert np.unique(region.reshape(-1,3),axis=0).shape[0]>350
    for a,b in zip(frames,frames[1:]):
        different=(np.abs(a.astype(np.int16)-b.astype(np.int16))>2).any(axis=2).sum()
        assert different>80,(category,different)


def test_fish_silhouette_has_time_dependent_fins():
    p=Painter(288,512)
    a=p.base.copy()
    b=p.base.copy()
    fish(p,ImageDraw.Draw(a,"RGBA"),280,565,21,1,.24,3)
    fish(p,ImageDraw.Draw(b,"RGBA"),280,565,21,1,.42,3)
    x=np.asarray(a)
    y=np.asarray(b)
    assert not np.array_equal(x,y)
    fish(p,ImageDraw.Draw(a,"RGBA"),280,565,21,-1,.24,3)
    with pytest.raises(ValueError):
        fish(p,ImageDraw.Draw(a,"RGBA"),280,565,21,0,.24,3)


def test_volcano_eruption_has_real_lava_motion_and_crust_texture():
    p=Painter(288,512)
    a=p.base.copy()
    b=p.base.copy()
    volcanic_structure(p,a,1.2)
    volcanic_structure(p,b,1.48)
    rock=np.asarray(a)[265:450,20:270,:3]
    assert np.unique(rock.reshape(-1,3),axis=0).shape[0]>12
    pixels=(np.asarray(a)!=np.asarray(b)).any(axis=2).sum()
    assert pixels>15


def test_generic_story_uses_no_fake_science_backdrop():
    p=Painter(288,512)
    generic=environment(p,"general")
    assert np.array_equal(np.asarray(generic),np.asarray(p.base))
    assert not hasattr(p,"_cinematic_backdrops")
