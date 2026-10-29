"""Original adaptive ambient score for vertical documentaries.

No audio samples, music library, network endpoint, or paid licence required.
A restrained tonal score and source-specific texture follow the actual scene
boundaries, with clean starts and ends and no constant mechanical ticking.
"""
from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 24000

CHORDS = (
    (146.83, 174.61, 220.00),  # Dm
    (130.81, 164.81, 196.00),  # C
    (110.00, 146.83, 174.61),  # Am
    (130.81, 164.81, 220.00),  # F
)


def _taper(n: int, sr: int) -> np.ndarray:
    envelope = np.ones(n, dtype=np.float32)
    edge = min(n // 2, round(.6 * sr))
    if edge:
        ramp = np.sin(np.linspace(0, np.pi / 2, edge, endpoint=True, dtype=np.float32)) ** 2
        envelope[:edge] *= ramp
        envelope[-edge:] *= ramp[::-1]
    return envelope


def _scene_cues(cfg: dict, duration: float):
    if cfg.get("mode") in ("universal", "storyboard"):
        return [(float(s["start"]), s.get("visual", "")) for s in cfg.get("scenes", [])[1:]]
    return [(t, "scale") for t in (7.5, 14.5, 21.8, 24.0, 28.5) if t < duration]


def synthesize(duration: float, cfg: dict, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Generate a mono broadcast-friendly bed (float32 in [-1,1])."""
    if not 0 < duration <= 180 or sr < 8000:
        raise ValueError("Invalid soundscape duration or sample rate")
    n = round(duration * sr)
    arr = np.zeros(n, np.float32)
    # Smooth voice-supporting pads: slow variation, no sharp note attacks.
    for chord_id, start in enumerate(np.arange(0, duration, 4)):
        a = round(float(start) * sr)
        b = min(n, a + round(sr * 4.25))
        t = np.arange(b-a, dtype=np.float32) / sr
        length = (b-a)/sr
        fade_in = np.minimum(1, t / .9)
        fade_out = np.minimum(1, np.maximum(0, length-t) / .85)
        envelope = fade_in * fade_out
        for j, freq in enumerate(CHORDS[chord_id % len(CHORDS)]):
            vibrato = .085 * np.sin(t * 1.1 + j)
            arr[a:b] += (.026/(1+.32*j)) * np.sin(2*np.pi*freq*t + vibrato) * envelope

    # Musical arpeggios in a higher register, round attacks and decay.
    notes = (293.66, 349.23, 440.00, 523.25, 392.00, 349.23, 329.63, 261.63)
    for j, when in enumerate(np.arange(.95, duration-.28, 1.3)):
        a = round(float(when)*sr)
        b = min(n, a+round(1.12*sr))
        t = np.arange(b-a,dtype=np.float32)/sr
        note = notes[j%len(notes)]
        env = (1-np.exp(-t*10)) * np.exp(-t*3.0)
        arr[a:b] += .018*np.sin(2*np.pi*note*t)*env

    # Topic-relevant nonverbal sound cues. All periodic textures are band-limited
    # by envelopes and rounded attacks rather than harsh square or noise clicks.
    category = cfg.get("motion_category", "")
    if not category:
        topic = str(cfg.get("topic", "")).lower()
        category = "ocean" if any(x in topic for x in ("ocean","sea","water")) else (
            "space" if any(x in topic for x in ("space","planet","solar","star")) else "general")
    if category == "ocean":
        for when in np.arange(0, duration, 3.4):
            a=round(float(when)*sr); b=min(n,a+round(2.9*sr))
            t=np.arange(b-a,dtype=np.float32)/sr
            swell=np.sin(np.pi*t/3.0)**2
            arr[a:b]+=.025*swell*np.sin(2*np.pi*(67*t+2.7*t*t))
    elif category in ("earthquake","volcano"):
        for when in np.arange(1.0, duration, 5.0):
            a=round(float(when)*sr);b=min(n,a+round(1.5*sr))
            t=np.arange(b-a,dtype=np.float32)/sr
            arr[a:b]+=.02*np.sin(2*np.pi*52*t)*np.exp(-t*2.0)
    elif category == "space":
        for when in np.arange(1.7, duration, 5.5):
            a=round(float(when)*sr);b=min(n,a+round(2.0*sr))
            t=np.arange(b-a,dtype=np.float32)/sr
            arr[a:b]+=.02*np.sin(2*np.pi*(205*t+45*t*t))*np.sin(np.pi*t/2)**2

    # Transitions have a short warm swell, rather than repetitive metronome ticks.
    for when, _ in _scene_cues(cfg,duration):
        a=max(0,round((when-.21)*sr))
        b=min(n,round((when+.46)*sr))
        if b<=a:continue
        t=np.arange(b-a,dtype=np.float32)/sr
        env=np.sin(np.pi*np.arange(b-a,dtype=np.float32)/(b-a))**2
        arr[a:b]+=.025*env*np.sin(2*np.pi*(210*t+160*t*t))

    arr*= _taper(n,sr)
    arr=np.tanh(arr*1.9)*.8
    return np.clip(arr,-.85,.85).astype(np.float32)


def write_soundscape(path: Path, duration: float, cfg: dict):
    values=synthesize(duration,cfg)
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SAMPLE_RATE)
        w.writeframes((values*32767).astype("<i2").tobytes())
