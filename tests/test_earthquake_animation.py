"""Earthquake visual quality regression: flexible buildings and seismic waves."""
from PIL import Image,ImageDraw
import numpy as np
from studio import Painter
from geology_premium import building_response,seismic_wavefield


def test_structural_sway_has_continuous_distinct_floor_motion():
    p=Painter(288,512)
    shifts=[]
    for frame in range(121):
        im=p.base.copy()
        d=ImageDraw.Draw(im,'RGBA')
        shifts.append(building_response(p,d,169,699,214,frame/60,12.5,1))
        assert im.size==(288,512)
    assert max(shifts)-min(shifts)>12
    assert max(abs(a-b) for a,b in zip(shifts,shifts[1:]))<2.5


def test_seismic_wavefronts_advance_and_have_non_static_frames():
    p=Painter(288,512)
    outputs=[]
    for t in (0.0,.15,.3,.45):
        im=p.base.copy()
        seismic_wavefield(p,im,t,.5)
        outputs.append(np.asarray(im).astype(np.int16))
    for a,b in zip(outputs,outputs[1:]):
        assert np.mean(np.abs(a-b))>.01
    assert all(im.shape[:2]==(512,288) for im in outputs)
