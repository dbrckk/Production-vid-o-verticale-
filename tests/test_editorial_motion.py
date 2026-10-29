"""Regression tests for source-limited English editorial motion documentaries."""
import numpy as np
import pytest

from editorial import EXPLAINERS, match_explainer
from kinetic import ANIMATORS
from studio import Painter
from topic_engine import research_story, validate_universal


@pytest.mark.parametrize(("question", "template", "motion"), [
    ("Why do ocean currents move?", "ocean_currents", "ocean"),
    ("How do volcanoes erupt?", "volcano_eruption", "volcano"),
    ("Why does the ocean have tides?", "ocean_tides", "ocean"),
    ("What is photosynthesis?", "photosynthesis", "biology"),
    ("Why do planets orbit in our solar system?", "solar_system", "space"),
    ("Why does our heart beat?", "heartbeat", "health"),
    ("What causes earthquakes?", "earthquakes", "earthquake"),
    ("How does weather develop?", "weather", "weather"),
])
def test_curated_scenes_have_distinct_meaning_and_physical_motion(question, template, motion):
    cfg = research_story(question, fetcher=lambda _: b"{}")
    assert cfg["evidence"] == "curated_science"
    assert cfg["editorial_template"] == template
    assert cfg["motion_category"] == motion
    assert cfg["language"] == "en"
    assert len(cfg["scenes"]) == 6
    assert motion in ANIMATORS
    validate_universal(cfg)
    captions = [s["narration"] for s in cfg["scenes"]]
    assert len(set(captions)) == 6
    assert all(len(caption.split()) >= 9 for caption in captions)
    assert all(s["narration"] == s["caption"] for s in cfg["scenes"])
    assert all("We start by identifying" not in sentence for sentence in captions)
    painter = Painter(288, 512)
    for t in (1.2, 12.7, 26.2):
        a = np.asarray(painter.frame(t, cfg))
        b = np.asarray(painter.frame(t + .17, cfg))
        pixels_changed = np.any(a != b, axis=2).sum()
        assert pixels_changed > 90, (template, t, pixels_changed)


def test_unknown_topic_not_misclassified_as_curated_science():
    assert match_explainer("A biography of Ada Lovelace") is None
    cfg = research_story("A biography of Ada Lovelace", fetcher=lambda _: b"{}")
    assert cfg["evidence"] == "unsourced"
    assert "editorial_template" not in cfg


def test_english_editorial_scripts_do_not_contain_placeholder_text():
    banned = ("we should not invent", "the original source", "reliable evidence matters",
              "notice the patterns", "we start by")
    assert len(EXPLAINERS) >= 8
    for name, item in EXPLAINERS.items():
        assert item["category"] in ANIMATORS, name
        assert len(item["beats"]) == 6
        for headline, narration in item["beats"]:
            assert headline and narration
            assert all(word not in narration.casefold() for word in banned)


def test_active_spoken_word_caption_render_has_high_contrast_background():
    from topic_engine import create_story
    cfg = create_story("What causes ocean currents?", duration=12)
    cfg["word_cues"] = [
        {"scene":0, "start":0.0, "end":0.30, "word":"OCEAN"},
        {"scene":0, "start":0.30, "end":0.65, "word":"CURRENTS"},
        {"scene":0, "start":0.65, "end":1.2, "word":"MOVE"},
    ]
    img = Painter(288,512).frame(.38,cfg)
    assert img.size == (288,512)
    assert np.asarray(img).std() > 8
