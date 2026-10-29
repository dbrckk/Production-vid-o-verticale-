"""Publication contracts: no slide numbers, safe captions, 1080p mastering.

Uses generated frames and an actual FFmpeg High-profile H.264 video rather than
assuming that a change to the script also changes delivered MP4 pixels.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import ImageDraw
import pytest

from studio import Painter, export_preset, render
from topic_engine import create_story
from subtitle_design import (CAPTION_PANEL, CAPTION_SAFE_BOTTOM,
                             render_captions, caption_backdrop)

ROOT=Path(__file__).resolve().parents[1]
PAPER=json.loads((ROOT/"presets/paper-to-moon.json").read_text())
SUN=json.loads((ROOT/"presets/sun-vanished.json").read_text())


@pytest.mark.parametrize(("cfg","samples"),[
    (create_story("What causes earthquakes?"),(0.2,4.2,14.6,27.0)),
    (SUN,(0.2,6.0,14.0,26.0)),
    (PAPER,(0.2,10.0,22.4,29.8)),
])
def test_no_video_mode_exposes_scene_counters_or_studio_label(cfg,samples):
    p=Painter(288,512)
    collected=[]
    original=p.text
    def capture(d,text,x,y,size,fill,anchor="mm",bold=False):
        collected.append((str(text),x,y))
        return original(d,text,x,y,size,fill,anchor=anchor,bold=bold)
    p.text=capture
    for when in samples:
        frame=p.frame(when,cfg)
        assert frame.size==(288,512)
    displayed=" | ".join(label for label,*_ in collected)
    assert not re.search(r"(?<!\d)\d{1,2}\s*/\s*\d{1,2}(?!\d)",displayed)
    assert "MOTION DOCUMENTARY" not in displayed
    assert "EXPLAINED IN" not in displayed
    if cfg.get("mode") in ("universal","storyboard"):
        assert all(y<925 for _,_,y in collected)


def test_caption_safe_zone_is_clear_of_social_platform_controls():
    assert CAPTION_SAFE_BOTTOM>=160
    assert CAPTION_PANEL[3]<1024-160
    p=Painter(288,512)
    cues=[
        {"scene":0,"word":"Natural","start":0.01,"end":.4},
        {"scene":0,"word":"English","start":.42,"end":.78},
        {"scene":0,"word":"narration","start":.8,"end":1.2},
    ]
    base=np.asarray(p.base)
    frame=p.base.copy()
    assert render_captions(p,frame,cues,.6,0)
    actual=np.asarray(frame)
    assert np.array_equal(actual[int(CAPTION_PANEL[3]*p.s)+2:,:,:],base[int(CAPTION_PANEL[3]*p.s)+2:,:,:])
    fallback=p.base.copy()
    caption_backdrop(p,fallback)
    assert np.array_equal(np.asarray(fallback)[int(CAPTION_PANEL[3]*p.s)+2:],
                          base[int(CAPTION_PANEL[3]*p.s)+2:])


def test_publish_encoding_is_high_quality_not_preview():
    pub=export_preset(1080,30,False)
    assert pub["name"]=="publication_1080p"
    assert pub["crf"]<=17
    assert pub["preset"] in ("medium","slow","slower","veryslow")
    assert pub["frame_rate"]==30
    assert pub["codec_profile"]=="high"
    assert pub["color_space"]=="bt709"
    assert pub["pixel_format"]=="yuv420p"
    assert pub["chapter_numbers"] is False and pub["watermark"] is False
    assert pub["audio_bitrate_kbps"]>=192
    assert export_preset(540,15,True)["name"]=="review"
    assert export_preset(720,24,False)["name"]=="review"


def test_real_1080p_30fps_social_encoder(tmp_path):
    # A short High-profile 1080p sample proves that FFmpeg supports our actual
    # publishing flags (BT709 color tags, faststart and constant frame rate).
    cfg={**PAPER}
    output=tmp_path/"publication.mp4"
    info=render(cfg,output,width=1080,fps=30,duration=.4,preview=False)
    assert info["export_profile"]=="publication_1080p"
    assert info["height"]==1920
    assert output.stat().st_size>2500
    p=subprocess.run([
        "ffprobe","-v","error","-show_entries",
        "stream=codec_name,codec_type,profile,pix_fmt,r_frame_rate,"
        "color_space,color_primaries,color_transfer,width,height,sample_rate",
        "-of","json",str(output),
    ],check=True,capture_output=True,text=True)
    streams=json.loads(p.stdout)["streams"]
    video=next(s for s in streams if s["codec_type"]=="video")
    audio=next(s for s in streams if s["codec_type"]=="audio")
    assert video["width"]==1080 and video["height"]==1920
    assert video["codec_name"]=="h264" and video["profile"]=="High"
    assert video["pix_fmt"]=="yuv420p"
    assert video["r_frame_rate"]=="30/1"
    assert all(video[k]=="bt709" for k in ("color_space","color_primaries","color_transfer"))
    assert audio["codec_name"]=="aac" and audio["sample_rate"]=="48000"
