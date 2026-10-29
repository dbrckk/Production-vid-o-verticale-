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


def test_news_brief_uses_only_verifiable_source_text():
    from topic_engine import create_story
    story = {
        "title": "Major research mission launches into orbit",
        "summary": "A new research spacecraft launched from the coastal spaceport. Its mission will study Earth's upper atmosphere.",
        "source": "Verified Science News",
        "published": "2026-10-29T10:00:00+00:00",
        "url": "https://news.example.org/research-mission",
    }
    cfg = create_story(story["title"], article=story, duration=30)
    assert cfg["evidence"] == "rss"
    assert cfg["editorial_policy"] == "source_only_no_fabricated_details"
    assert len(cfg["scenes"]) == 4  # lead, two substantive facts, attribution
    assert cfg["scenes"][-1]["narration"].startswith("Reported on")
    assert all("We should not invent" not in sc["narration"] for sc in cfg["scenes"])
    assert any("upper atmosphere" in sc["narration"] for sc in cfg["scenes"])
    assert cfg["sources"][0]["url"] == story["url"]
    assert cfg["scenes"][-1]["end"] == 30
    validate_universal(cfg)


def test_news_rejects_thin_reporting_not_fake_padding():
    from topic_engine import create_story
    article = {
        "title":"Minor event", "summary":"Soon.",
        "source":"A source", "url":"https://news.example.org/event",
        "published":"2026-10-29T10:00:00+00:00",
    }
    with pytest.raises(ValueError,match="Not enough sourced information"):
        create_story(article["title"], article=article)


def test_encyclopedia_video_uses_only_retrieved_facts_not_generic_slides():
    import json
    from topic_engine import research_story
    source = {
        "query": {"pages": {"1": {
            "pageid": 12, "title": "The Atlantic Ocean",
            "extract": "The Atlantic Ocean is one of Earth's five oceans. It separates the Americas from Europe and Africa. Ocean currents transport heat across its basin."
        }}}
    }
    cfg = research_story("Tell me about the Atlantic Ocean",fetcher=lambda _:json.dumps(source).encode())
    assert cfg["evidence"] == "wikipedia"
    assert cfg["editorial_policy"] == "reference_sentences_only"
    assert len(cfg["scenes"]) == 5
    assert "transport heat" in cfg["scenes"][3]["narration"]
    assert all("We start by identifying" not in sc["narration"] for sc in cfg["scenes"])
    assert cfg["sources"][0]["source"] == "Wikipedia"
    validate_universal(cfg)
