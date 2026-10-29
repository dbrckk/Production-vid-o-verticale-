"""Genuine 60 FPS publishing and improved dynamic geology checks."""
import json
import subprocess
import numpy as np

from studio import Painter, export_preset, render
from topic_engine import research_story


def test_premium_60fps_profile_is_not_a_relabelled_30fps_master():
    profile=export_preset(1080,60,False)
    assert profile["name"]=="publication_1080p60"
    assert profile["frame_rate"]==60
    assert profile["gop_frames"]==120
    assert profile["crf"]<=17
    assert export_preset(1080,30,False)["name"]=="publication_1080p"


def test_actual_h264_file_encodes_60_distinct_times(tmp_path):
    cfg=research_story("What causes earthquakes?", fetcher=lambda _:b"{}")
    movie=tmp_path/"smooth.mp4"
    info=render(cfg,movie,width=1080,fps=60,duration=.35,preview=False)
    assert info["frames"]==21 and info["fps"]==60
    probe=json.loads(subprocess.run([
        "ffprobe","-v","error",
        "-show_entries","stream=codec_name,avg_frame_rate,profile,width,height",
        "-of","json",str(movie)
    ],check=True,capture_output=True,text=True).stdout)
    track=next(s for s in probe["streams"] if s.get("codec_name")=="h264")
    assert track["avg_frame_rate"]=="60/1"
    assert track["width"]==1080 and track["height"]==1920
    assert track["profile"]=="High"


def test_earthquake_geology_has_layered_painted_detail_and_nonstatic_shocks():
    cfg=research_story("What causes earthquakes?", fetcher=lambda _:b"{}")
    p=Painter(288,512)
    frame1=np.asarray(p.frame(2.0,cfg))
    frame2=np.asarray(p.frame(2.4,cfg))
    # The mineral structure contains many fine color variations, not one flat block.
    rock=frame1[299:380,28:255,:]
    assert np.unique(rock.reshape(-1,3),axis=0).shape[0]>180
    assert np.any(frame1!=frame2)
