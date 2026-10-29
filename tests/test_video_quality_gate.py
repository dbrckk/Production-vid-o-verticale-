"""Real FFmpeg QA tests: narration, clips, static-image detection, timing."""
import json
import subprocess

import pytest

from qa_video import inspect, QualityFailure


def _make_video(path,still=False):
    source="color=c=black:s=288x512:r=15:d=4" if still else "testsrc2=s=288x512:r=15:d=4"
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i",source,
        "-f","lavfi","-i","sine=frequency=660:sample_rate=48000:duration=4",
        "-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","128k","-t","4",str(path),
    ],check=True,capture_output=True)


def _manifest(path):
    data={
        "mode":"universal","duration":4.0,
        "voice":{"provider":"edge","language":"en","word_alignment":"provider_word_boundaries"},
        "word_cues":[
            {"scene":0,"word":w,"start":i*.45+.15,"end":i*.45+.4}
            for i,w in enumerate(("Today","we","explain","how","this","works"))
        ],
    }
    path.write_text(json.dumps(data))
    return data


@pytest.fixture
def playable(tmp_path):
    video=tmp_path/"animated.mp4"
    metadata=tmp_path/"animated.json"
    _make_video(video)
    _manifest(metadata)
    return video,metadata


def test_live_video_has_actual_motion_and_audible_english_metadata(playable):
    video,metadata=playable
    result=inspect(video,metadata)
    assert result["passed"]
    assert result["width"]==288 and result["height"]==512
    assert result["audio_language"]=="en"
    assert result["sampled_frames"]>=3
    assert result["active_intervals"]>=.65
    assert -22<=result["loudness_lufs"]<=-12


def test_static_slideshow_fails_even_when_audio_exists(playable,tmp_path):
    _,metadata=playable
    still=tmp_path/"still.mp4"
    _make_video(still,still=True)
    with pytest.raises(QualityFailure,match="slideshow"):
        inspect(still,metadata)



def test_adjacent_frame_motion_detects_real_30_fps_vs_fake_smoothness(tmp_path):
    from qa_video import _temporal_motion
    def movie(path,source):
        subprocess.run([
            "ffmpeg","-hide_banner","-loglevel","error","-y",
            "-f","lavfi","-i",source,
            "-c:v","libx264","-preset","ultrafast",
            "-pix_fmt","yuv420p","-t","3",str(path),
        ],check=True,capture_output=True)
    moving=tmp_path/"motion.mp4"
    still=tmp_path/"static.mp4"
    movie(moving,"testsrc2=s=90x160:r=30:d=3")
    movie(still,"color=c=black:s=90x160:r=30:d=3")
    good=_temporal_motion(moving,3,30)
    bad=_temporal_motion(still,3,30)
    assert good["sampled_adjacent_frames"]>35
    assert good["adjacent_frame_activity"]>.8
    assert bad["adjacent_frame_activity"]<.05
    assert _temporal_motion(moving,3,15) is None


def test_missing_narration_fails(playable,tmp_path):
    video,metadata=playable
    data=json.loads(metadata.read_text())
    data["voice"]=None
    altered=tmp_path/"missing.json"
    altered.write_text(json.dumps(data))
    with pytest.raises(QualityFailure,match="English narrated voice"):
        inspect(video,altered)


def test_bad_word_timings_rejected(playable,tmp_path):
    video,metadata=playable
    data=json.loads(metadata.read_text())
    data["word_cues"][2]["end"]=7
    altered=tmp_path/"bad-timing.json"
    altered.write_text(json.dumps(data))
    with pytest.raises(QualityFailure,match="out of sync"):
        inspect(video,altered)
