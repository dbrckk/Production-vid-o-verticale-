"""Offline original score regression: no hard clicks, natural topic variation."""
import numpy as np
import pytest
from soundscape import synthesize, write_soundscape, SAMPLE_RATE
import wave


@pytest.mark.parametrize("topic,category",[
    ("How do ocean currents work?","ocean"),
    ("Why do tectonic plates shake?","earthquake"),
    ("How do planets orbit?","space"),
    ("How do markets move?","economy"),
])
def test_score_is_well_bounded_topic_aware_and_not_a_metronome(topic,category):
    cfg={"mode":"universal","topic":topic,"motion_category":category,
         "scenes":[{"start":0,"end":3,"visual":"focus"},{"start":3,"end":6,"visual":"compare"}]}
    samples=synthesize(6,cfg)
    assert samples.dtype==np.float32
    assert len(samples)==SAMPLE_RATE*6
    assert np.max(np.abs(samples))<.86
    assert np.sqrt(np.mean(samples**2))>.008
    assert np.max(np.abs(samples[:round(.07*SAMPLE_RATE)])) < .015
    assert np.max(np.abs(samples[-round(.07*SAMPLE_RATE):])) < .015
    # A scored video should not change level abruptly at a cut.
    seam=round(3*SAMPLE_RATE)
    assert np.max(np.abs(np.diff(samples[seam-100:seam+100])))<.1


def test_score_different_topics_produce_different_acoustic_texture(tmp_path):
    ocean={"mode":"universal","motion_category":"ocean","scenes":[]}
    space={"mode":"universal","motion_category":"space","scenes":[]}
    x=synthesize(5,ocean)
    y=synthesize(5,space)
    assert np.mean(np.abs(x-y)) > 0.0005
    path=tmp_path/"original.wav"
    write_soundscape(path,5,ocean)
    with wave.open(str(path),"rb") as w:
        assert w.getnchannels()==1 and w.getframerate()==SAMPLE_RATE
        assert w.getnframes()==5*SAMPLE_RATE


@pytest.mark.parametrize("seconds",[0,-1,181])
def test_reject_invalid_duration(seconds):
    with pytest.raises(ValueError):
        synthesize(seconds,{})
