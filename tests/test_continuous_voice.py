"""One-take neural narration, accurate word cues and prosody contracts."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

import narration
from narration import make_narration, continuous_scene_bounds
from topic_engine import create_story


def test_uses_one_whole_story_voice_request_instead_of_chopped_clips(tmp_path,monkeypatch):
    cfg=create_story("Why do ocean currents move?")
    seen=[]
    async def one_take(text,out,voice):
        seen.append((text,voice))
        words=text.split()
        out.write_bytes(b"fake-mp3")
        return [
            {"text":word,"offset":.10+i*.20,"duration":.165}
            for i,word in enumerate(words)
        ]
    monkeypatch.setattr(narration,"_edge",one_take)
    def decode(_):
        return np.ones(24000*30,dtype="<i2")*2700
    monkeypatch.setattr(narration,"_pcm_from_file",decode)
    wav=tmp_path/"speech.wav"
    result=make_narration(cfg,wav,provider="edge",voice="en-US-AndrewNeural")
    assert len(seen)==1
    assert result["delivery_style"]=="continuous_documentary"
    assert cfg["voice"]["delivery_style"]=="continuous_documentary"
    assert cfg["voice"]["word_alignment"]=="provider_word_boundaries"
    assert len(cfg["word_cues"])==len(seen[0][0].split())
    assert all(scene["start"] < scene["end"] for scene in cfg["scenes"])
    assert all(cfg["scenes"][i]["end"]==cfg["scenes"][i+1]["start"]
               for i in range(len(cfg["scenes"])-1))
    assert wav.stat().st_size>100_000


def test_voice_scene_bounds_reject_inadequate_alignment():
    scenes=[
        {"narration":"A moving rock creates tremendous pressure."},
        {"narration":"Energy travels in every direction."},
    ]
    assert continuous_scene_bounds([{"offset":0,"text":"A"}],scenes,8.) is None
    words=" ".join(s["narration"] for s in scenes).split()
    cues=[{"offset":i*.5+.1,"duration":.4,"text":word}
          for i,word in enumerate(words)]
    bounds=continuous_scene_bounds(cues,scenes,10.)
    assert bounds is not None
    positions,ends=bounds
    assert positions[0]==0 and positions[-1]==len(words)
    assert 0<ends[0]<ends[1]


def test_documentary_voice_uses_natural_rate_instead_of_slow_robotic_rate(monkeypatch,tmp_path):
    import asyncio
    import sys
    import types
    observed=[]
    class FakeCommunicate:
        def __init__(self,text,voice,**options):
            observed.append(options)
        async def stream(self):
            yield {"type":"audio","data":b"A"*2000}
            yield {"type":"WordBoundary","text":"Earth","offset":10_000_000,
                   "duration":2_000_000}
    monkeypatch.setitem(sys.modules,"edge_tts",types.SimpleNamespace(Communicate=FakeCommunicate))
    marks=asyncio.run(narration._edge("Earth moves.",tmp_path/"voice.mp3","en-US-AndrewNeural"))
    assert marks
    assert observed[0]["rate"]==narration.DOCUMENTARY_RATE
    assert observed[0]["pitch"]==narration.DOCUMENTARY_PITCH
    assert observed[0]["boundary"]=="WordBoundary"
