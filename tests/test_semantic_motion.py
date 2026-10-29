"""Story-level animation QA for arbitrary topics (not only curated science)."""
import numpy as np
import pytest
from studio import Painter
from topic_engine import research_story
from semantic_motion import VISUAL_TAGS
import motion_layers


def _generic_story():
    return research_story("Who was Ada Lovelace?", fetcher=lambda _: b"{}")


def test_every_generic_chapter_uses_a_distinct_purpose_built_animation(monkeypatch):
    cfg=_generic_story()
    assert cfg["evidence"]=="unsourced"
    assert set(scene["visual"] for scene in cfg["scenes"])==VISUAL_TAGS

    def forbidden(*a,**kw):
        raise AssertionError("Generic overlaid effects should never obscure authored diagrams")
    monkeypatch.setattr(motion_layers,"animate",forbidden)
    p=Painter(288,512)
    images=[]
    for ix,scene in enumerate(cfg["scenes"]):
        t=(scene["start"]+scene["end"])/2
        image=np.asarray(p.frame(t,cfg))
        images.append(image[195:409,25:263].copy())
        nearby=np.asarray(p.frame(t+.22,cfg))[195:409,25:263]
        movement=(images[-1]!=nearby).any(axis=2).sum()
        assert movement>200, (ix,movement)
    for i in range(len(images)-1):
        differences=(images[i]!=images[i+1]).any(axis=2).sum()
        assert differences>1200,(i,differences)


def test_visual_renderer_rejects_unknown_visual():
    from semantic_motion import draw
    p=Painter(288,512)
    with pytest.raises(ValueError,match="Unknown generic"):
        draw(p,p.base.copy(),"not_authorized",.4,.2,0)


def test_generic_topic_never_adds_invented_data_figures():
    cfg=_generic_story()
    # Without a source, avoid fake dates, invented labels, numbers, or events.
    assert not cfg.get("sources")
    assert "curated_science" != cfg.get("evidence")
    assert all(scene["headline"] and scene["caption"] for scene in cfg["scenes"])
