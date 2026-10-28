import json
import math
import subprocess
import sys
from pathlib import Path

import pytest
from studio import Painter, fold_at, format_distance, make_audio, render, thickness_mm


CFG = json.loads((Path(__file__).parent.parent/'presets'/'paper-to-moon.json').read_text())


def test_exponential_math():
    assert thickness_mm(0) == .1
    assert thickness_mm(10) == 102.4
    assert 439_000 < thickness_mm(42)/1e6 < 440_000
    with pytest.raises(ValueError):thickness_mm(-1)


def test_fold_timeline():
    assert fold_at(0,CFG)==0
    assert fold_at(22.0,CFG)==42
    assert fold_at(23.0,CFG)==42
    assert fold_at(29,CFG)==103
    assert all(fold_at(i/10,CFG) <= fold_at((i+1)/10,CFG) for i in range(310))


def test_values_and_frame():
    assert 'km' in format_distance(thickness_mm(42))
    assert 'mm' in format_distance(.1)
    frame=Painter(288,512).frame(8,CFG)
    assert frame.size==(288,512)
    assert len(frame.getcolors(288*512))>150
    with pytest.raises(ValueError):Painter(300,512)


def test_audio(tmp_path):
    f=tmp_path/'s.wav';make_audio(f,1.2,CFG)
    assert f.stat().st_size>20_000


def test_render_mp4(tmp_path):
    out=tmp_path/'sample.mp4'
    info=render(CFG,out,width=288,fps=6,duration=1.5,preview=True)
    assert info['frames']==9
    assert out.stat().st_size>2000
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
          '-of','default=noprint_wrappers=1:nokey=1',str(out)],capture_output=True,text=True,check=True)
    assert math.isclose(float(r.stdout),1.5,abs_tol=.2)
