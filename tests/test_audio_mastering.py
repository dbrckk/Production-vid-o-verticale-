"""Audio mastering tests use real FFmpeg PCM, not just a string inspection."""
from __future__ import annotations

import json
import subprocess
import wave

import numpy as np

from audio_mastering import narration_mix, quality_targets


SR = 24000


def _write_mono(path, samples):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def _read_mono(path):
    with wave.open(str(path), "rb") as w:
        assert w.getnchannels() == 1 and w.getframerate() == SR
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768


def _energy_at(samples, hz):
    # Correlation isolates the actual music frequency from narrator speech.
    # Use windows containing integral multiples of the test waveform period.
    tt = np.arange(len(samples)) / SR
    cos = np.cos(2*np.pi*hz*tt)
    sin = np.sin(2*np.pi*hz*tt)
    return 2*np.hypot(np.dot(samples, cos), np.dot(samples, sin))/len(samples)


def test_voice_over_music_is_ducked_not_clipped(tmp_path):
    n = 3 * SR
    t = np.arange(n, dtype=np.float64) / SR
    music = .22 * np.sin(2 * np.pi * 220 * t)
    speech = np.zeros(n)
    active = (t >= .65) & (t < 1.65)
    speech[active] = .20 * np.sin(2*np.pi * 880 * t[active])

    bed = tmp_path / "bed.wav"
    voice = tmp_path / "voice.wav"
    mixed = tmp_path / "mix.wav"
    _write_mono(bed, music)
    _write_mono(voice, speech)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=32x32:r=1:d=3",
        "-i", str(bed), "-i", str(voice),
        "-filter_complex", narration_mix(), "-map", "[a]",
        "-ac", "1", "-ar", str(SR), "-t", "3", "-c:a", "pcm_s16le", str(mixed)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    audio = _read_mono(mixed)

    assert abs(len(audio)-n) < 256
    before = _energy_at(audio[int(.10*SR):int(.40*SR)], 220)
    during = _energy_at(audio[int(1.0*SR):int(1.3*SR)], 220)
    recovered = _energy_at(audio[int(2.35*SR):int(2.65*SR)], 220)
    voice_level = _energy_at(audio[int(1.0*SR):int(1.3*SR)], 880)
    assert before > .020
    assert during < before * .72, (before,during)
    assert recovered > during * 1.3, (recovered,during)
    assert voice_level > during * 1.5, (voice_level,during)
    assert np.max(np.abs(audio)) < .97


def test_mastering_metadata_and_filter_pads():
    graph = narration_mix()
    assert "[speech]asplit=2[key][narrator]" in graph
    assert "sidechaincompress" in graph
    assert "alimiter" in graph
    assert graph.endswith("[a]")
    targets = quality_targets()
    assert targets["voice_language"] == "en"
    assert targets["dialogue_primary"] is True
