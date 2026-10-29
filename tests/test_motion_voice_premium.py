"""Premium motion and voice regression contracts."""
import math
from PIL import Image
from cinematic import camera_parameters, move_camera, render_cinematic_art
from studio import Painter
from audio_mastering import narration_mix, quality_targets


def test_bicubic_camera_is_temporally_continuous():
    for ix in range(6):
        last=None
        for frame in range(121):
            zoom,x,y=camera_parameters(ix,frame/120)
            assert 1.0<zoom<1.1
            assert abs(x)<=4.1 and abs(y)<=4.7
            if last:
                assert max(abs(a-b) for a,b in zip((zoom,x,y),last))<.16
            last=zoom,x,y
    p=Painter(288,512)
    moved=move_camera(p,p.base.copy(),0,.5,'earthquake')
    assert moved.size==(288,512)


def test_outgoing_scene_keeps_animating_through_dissolve():
    p=Painter(288,512)
    cfg={'scenes':[{'start':0,'end':2},{'start':2,'end':4}]}
    observed=[]
    def draw(painter,canvas,kind,t,chapter,progress):
        observed.append((chapter,t,progress))
    render_cinematic_art(p,cfg,2.08,1,.04,draw,'earthquake')
    render_cinematic_art(p,cfg,2.24,1,.12,draw,'earthquake')
    outgoing=[t for chapter,t,_ in observed if chapter==0]
    assert len(outgoing)==2
    assert outgoing[1]>outgoing[0]
    assert outgoing[0]>1.99


def test_voice_is_english_first_with_soft_presence_mastering():
    chain=narration_mix()
    assert 'sidechaincompress' in chain
    assert 'equalizer=f=3250' in chain
    assert 'acompressor=threshold=0.11:ratio=1.8' in chain
    assert 'loudnorm' in chain
    assert quality_targets()['voice_language']=='en'
