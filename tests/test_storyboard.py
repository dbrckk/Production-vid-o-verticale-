"""Storyboard scene contracts and playable vertical-render regression checks."""
import json
import math
import subprocess
from pathlib import Path

import pytest

from studio import Painter, render
from storyboard import ALLOWED_VISUALS, scene_at, validate_storyboard

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'presets' / 'sun-vanished.json').read_text(encoding='utf8'))


def test_six_scenes_cover_exactly_thirty_seconds():
    validate_storyboard(CONFIG)
    assert len(CONFIG['scenes']) == 6
    assert scene_at(CONFIG, 0)[0] == 0
    assert scene_at(CONFIG, 5)[0] == 1
    assert scene_at(CONFIG, 29.99)[0] == 5
    assert set(s['visual'] for s in CONFIG['scenes']) == ALLOWED_VISUALS


@pytest.mark.parametrize('change', [
    lambda c: c['scenes'][0].update(end=5),
    lambda c: c['scenes'][1].update(visual='unknown'),
    lambda c: c['scenes'][3].update(caption=''),
    lambda c: c.update(duration=28),
])
def test_invalid_storyboards_are_rejected(change):
    cfg = json.loads(json.dumps(CONFIG))
    change(cfg)
    with pytest.raises(ValueError):
        validate_storyboard(cfg)


def test_all_scenes_and_crossfades_produce_full_frames():
    p = Painter(288, 512)
    for scene in CONFIG['scenes']:
        for t in (scene['start'], (scene['start']+scene['end'])/2):
            im = p.frame(t, CONFIG)
            assert im.mode == 'RGB' and im.size == (288, 512)
            assert len(im.getcolors(288*512) or []) > 150


def test_render_sun_mp4_with_audio_and_manifest(tmp_path):
    mp4 = tmp_path / 'sun.mp4'
    info = render(CONFIG, mp4, width=288, fps=6, duration=2.0, preview=True)
    assert info['mode'] == 'storyboard' and len(info['scenes']) == 6
    assert mp4.stat().st_size > 2000
    assert (tmp_path / 'cover.png').stat().st_size > 1000
    streams = json.loads(subprocess.run([
        'ffprobe','-v','error','-show_streams','-of','json',str(mp4)],
        check=True,capture_output=True,text=True).stdout)['streams']
    assert any(s['codec_type']=='video' and s['width']==288 and s['height']==512 for s in streams)
    assert any(s['codec_type']=='audio' and s['codec_name']=='aac' for s in streams)
    assert math.isclose(info['duration'],2.0)
