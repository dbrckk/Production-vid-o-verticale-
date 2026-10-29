"""Narrated publishing guarantees must hold for classic presets too."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
from studio import Painter,render
from narration import make_narration

ROOT=Path(__file__).resolve().parents[1]
SUN=json.loads((ROOT/'presets/sun-vanished.json').read_text())
PAPER=json.loads((ROOT/'presets/paper-to-moon.json').read_text())


def test_english_sun_template_keeps_word_cues_in_render_manifest(tmp_path):
    cfg=copy.deepcopy(SUN)
    assert cfg['language']=='en'
    # A deterministic local test synthesizer replaces the network service only
    # inside this test. Production always requires the actual English narrator.
    def voice_samples(text,scene):
        sr=24000
        t=np.arange(round(.32*sr),dtype=np.float32)/sr
        return (.17*np.sin(2*np.pi*(270+scene*20)*t)).astype(np.float32)
    audio=tmp_path/'sun-narration.wav'
    make_narration(cfg,audio,synthesizer=voice_samples)
    assert cfg['voice']['language']=='en'
    assert len(cfg['word_cues'])>=30
    assert cfg['duration']>3
    out=tmp_path/'sun.mp4'
    info=render(cfg,out,width=288,fps=6,preview=True,voice=audio)
    assert info['voice']['language']=='en'
    assert len(info['word_cues'])==len(cfg['word_cues'])
    assert info['encoding']['chapter_numbers'] is False
    assert out.stat().st_size>5000
    frame=Painter(288,512).frame(cfg['scenes'][0]['start']+.12,cfg)
    assert frame.size==(288,512)


def test_paper_scene_uses_real_narration_cues_without_counter_overlay():
    paper=copy.deepcopy(PAPER)
    paper['word_cues']=[
        {'scene':0,'word':'Forty','start':.10,'end':.45},
        {'scene':0,'word':'two','start':.46,'end':.85},
        {'scene':0,'word':'folds','start':.87,'end':1.20},
    ]
    paper['voice_scene_bounds']=[(0,2),(2,3)]
    painter=Painter(288,512)
    with_cues=np.asarray(painter.frame(.61,paper),dtype=np.int16)
    without=copy.deepcopy(paper)
    without.pop('word_cues')
    no_cues=np.asarray(painter.frame(.61,without),dtype=np.int16)
    # The subtitle occupies only the publishing-safe band, no slide index.
    y0=round(726*painter.s)
    y1=round(854*painter.s)
    difference=np.abs(with_cues-no_cues).sum(axis=2)
    assert difference[y0:y1].sum()>25000
    assert difference[y1+2:].sum()==0
