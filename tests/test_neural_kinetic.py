"""Physical animation movement, real English narration assembly and MP4 checks."""
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np
import pytest

from narration import make_narration, script_for_scene
from studio import Painter, render
from topic_engine import create_story, research_story, require_english_topic
from universal import topic_category


@pytest.mark.parametrize("topic", [
    "How do the oceans move?",
    "Why do volcanoes erupt?",
    "How does the solar system work?",
    "How does a computer process information?",
    "Why does our heart beat?",
    "What makes the stock market fluctuate?",
    "How do weather patterns develop?",
])
def test_physical_motion_changes_visible_pixels(topic):
    cfg = create_story(topic, duration=12)
    p = Painter(288, 512)
    a = np.asarray(p.frame(.5, cfg), dtype=np.uint8)
    b = np.asarray(p.frame(1.2, cfg), dtype=np.uint8)
    # Separate frames are physically different without relying on scene cuts.
    changed = (a != b).any(axis=2).sum()
    assert changed > 120
    assert topic_category(topic) in (
        "ocean", "volcano", "space", "tech", "health", "economy", "general"
    )


def sample_voice(text: str, scene: int):
    sr = 24000
    t = np.arange(int(sr * (.78+scene*.04)), dtype=np.float32) / sr
    return .14 * np.sin(2*math.pi*(182+scene*14)*t)


def test_voice_retimes_scenes_and_creates_english_word_cues(tmp_path):
    cfg = create_story("How do oceans shape the planet?", duration=12)
    voice = tmp_path / "voice.wav"
    info = make_narration(cfg, voice, provider="edge", synthesizer=sample_voice)
    assert info["words"] >= 35
    assert cfg["voice"]["language"] == "en"
    assert cfg["duration"] > 5.5
    assert cfg["scenes"][0]["start"] == 0
    assert cfg["scenes"][-1]["end"] == cfg["duration"]
    assert all(s["end"]>s["start"] for s in cfg["scenes"])
    assert cfg["word_cues"][-1]["start"] <= cfg["duration"]
    assert all(cfg["word_cues"][i]["start"]<=cfg["word_cues"][i+1]["start"]
               for i in range(len(cfg["word_cues"])-1))
    with wave.open(str(voice), "rb") as f:
        assert f.getframerate() == 24000 and f.getnchannels() == 1
        assert f.getnframes() / 24000 == pytest.approx(cfg["duration"], abs=.01)


def test_narrated_movie_has_audio_and_source_metadata(tmp_path):
    cfg = create_story("What causes ocean currents?", duration=12)
    voice = tmp_path / "voice.wav"
    make_narration(cfg, voice, synthesizer=sample_voice)
    movie = tmp_path / "narrated.mp4"
    manifest = render(cfg, movie, 288, 2, preview=True, voice=voice)
    assert manifest["voice"]["language"] == "en"
    assert manifest["frames"] > 10
    assert len(manifest["word_cues"]) > 25
    streams = json.loads(subprocess.run(
        ["ffprobe","-v","error","-show_streams","-of","json",str(movie)],
        capture_output=True,text=True,check=True
    ).stdout)["streams"]
    assert any(s["codec_type"]=="audio" and s["codec_name"]=="aac" for s in streams)
    assert any(s["codec_type"]=="video" and s["width"]==288 for s in streams)


def test_reject_non_english_custom_topic():
    with pytest.raises(ValueError,match="English only"):
        research_story("Pourquoi les océans sont-ils salés?",fetcher=lambda _:b"{}")
    require_english_topic("Why are oceans salty?")
    with pytest.raises(ValueError,match="English only"):
        require_english_topic("Comment fonctionne le volcan?")


def test_empty_voice_rejected(tmp_path):
    cfg=create_story("How does a turbine work?",duration=12)
    with pytest.raises(RuntimeError,match="empty or too short"):
        make_narration(cfg,tmp_path/"bad.wav",synthesizer=lambda t,i:np.zeros(12,np.float32))
    assert not (tmp_path/"bad.wav").exists()


def test_real_edge_word_boundaries_are_used_for_subtitles(tmp_path, monkeypatch):
    import narration
    cfg=create_story("Why do planets orbit?",duration=12)
    async def edge_stub(text, target, voice):
        target.write_bytes(b"stub")
        return [
            {"text":"Planets","offset":.15,"duration":.21},
            {"text":"orbit","offset":.40,"duration":.19},
        ]
    monkeypatch.setattr(narration,"_edge",edge_stub)
    monkeypatch.setattr(narration,"_pcm_from_file",lambda _:np.ones(24000,np.int16)*1600)
    voice=tmp_path/"speech.wav"
    info=make_narration(cfg,voice,provider="edge")
    assert cfg["voice"]["word_alignment"] == "provider_word_boundaries"
    assert info["words"] == len(cfg["scenes"])*2
    assert cfg["word_cues"][0]["word"] == "Planets"
    assert cfg["word_cues"][0]["start"] == pytest.approx(.15,abs=.01)
    assert cfg["word_cues"][1]["start"] == pytest.approx(.40,abs=.01)
    assert cfg["word_cues"][2]["start"] > cfg["word_cues"][1]["end"]
