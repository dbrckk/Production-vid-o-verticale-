"""English-only neural narration, scene timing, and synchronized subtitle cues.

Edge neural voices run on small Render instances. Optional Kokoro ONNX runs offline
on a machine with enough RAM. Never silently replace missing speech with music.
"""
from __future__ import annotations

import asyncio
import math
from pathlib import Path
import subprocess
import tempfile
import wave
import numpy as np

SAMPLE_RATE = 24000
DEFAULT_EDGE_VOICE = "en-US-AndrewNeural"
DEFAULT_KOKORO_VOICE = "af_heart"


def script_for_scene(scene: dict, cfg: dict) -> str:
    text = (scene.get("narration") or scene.get("caption") or "").strip()
    if not text:
        raise ValueError("Every scene needs English narration")
    return text


def _pcm_from_file(path: Path) -> np.ndarray:
    command = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(path), "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-c:a", "pcm_s16le", "-f", "s16le", "pipe:1",
    ]
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if not p.stdout:
        raise RuntimeError("Neural voice provider produced empty audio")
    return np.frombuffer(p.stdout, dtype="<i2").copy()


async def _edge(text: str, output: Path, voice: str):
    """Write neural MP3 and collect provider-authored word boundaries."""
    import edge_tts
    marks=[]
    communication=edge_tts.Communicate(
        text, voice=voice, rate="-4%", volume="+0%", boundary="WordBoundary",
    )
    with output.open("wb") as stream:
        async for chunk in communication.stream():
            if chunk["type"] == "audio":
                stream.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                marks.append({
                    "text":chunk["text"],
                    "offset":chunk["offset"] / 10_000_000,
                    "duration":chunk["duration"] / 10_000_000,
                })
    if not output.exists() or output.stat().st_size < 1000:
        raise RuntimeError("English neural narrator returned no audio")
    return marks


def _kokoro(text: str, engine, voice: str) -> np.ndarray:
    audio, sr = engine.create(text, voice=voice, speed=1.03, lang="en-us")
    if sr != SAMPLE_RATE:
        raise RuntimeError("Unexpected Kokoro sample rate")
    return np.clip(np.asarray(audio, dtype=np.float32), -1, 1).astype(np.float32)


def make_narration(
    cfg: dict, dest: Path, provider: str = "edge",
    voice: str | None = None,
    synthesizer=None,
) -> dict:
    """Create a real spoken WAV and retime the scenes around the voice.

    A custom synthesizer(text, scene_index) -> 1D array of float32 at 24kHz is
    available solely for isolated regression tests and local adapter integrations.
    """
    if cfg.get("mode") not in ("universal", "storyboard"):
        raise ValueError("Neural narration requires a scene-based video")
    if cfg.get("language", "en") != "en":
        raise ValueError("Only English narration is supported")
    scenes = cfg["scenes"]
    if not scenes:
        raise ValueError("No scenes to narrate")
    if provider not in ("edge", "kokoro") and synthesizer is None:
        raise ValueError("Supported voice providers: edge or kokoro")
    dest.parent.mkdir(parents=True, exist_ok=True)
    pieces = []
    cues = []
    clock = 0.0
    engine = None
    if provider == "kokoro" and synthesizer is None:
        from kokoro_onnx import Kokoro
        models = Path(__file__).resolve().parent / "models"
        model = models / "kokoro-v1.0.onnx"
        voices = models / "voices-v1.0.bin"
        if not model.is_file() or not voices.is_file():
            raise RuntimeError(
                "Kokoro model missing: download kokoro-v1.0.onnx and "
                "voices-v1.0.bin into models/"
            )
        engine = Kokoro(str(model), str(voices))
    try:
        with tempfile.TemporaryDirectory(prefix="vss-narration-") as temp:
            timing_mode="estimated"
            for index, scene in enumerate(scenes):
                text = script_for_scene(scene, cfg)
                boundaries=[]
                if synthesizer is not None:
                    samples = np.asarray(synthesizer(text, index), dtype=np.float32)
                    samples = (np.clip(samples, -1, 1) * 32767).astype("<i2")
                elif provider == "kokoro":
                    samples = (_kokoro(text, engine, voice or DEFAULT_KOKORO_VOICE) * 32767).astype("<i2")
                else:
                    temp_mp3 = Path(temp) / f"{index:02d}.mp3"
                    boundaries=asyncio.run(_edge(text, temp_mp3, voice or DEFAULT_EDGE_VOICE))
                    samples = _pcm_from_file(temp_mp3)
                if len(samples) < SAMPLE_RATE // 10:
                    raise RuntimeError(f"Speech was empty or too short for scene {index + 1}")
                # Maintain subtitles in sync with each spoken word (approximate
                # alignment; unlike phoneme alignment, no false per-word precision).
                words = text.split()
                length = len(samples) / SAMPLE_RATE
                boundaries_est = [sum(max(1, len(word.strip('.,!?'))) for word in words[:i]) for i in range(len(words)+1)]
                total = boundaries_est[-1] or 1
                scene["start"] = round(clock, 4)
                scene["end"] = round(clock + length + 0.28, 4)
                scene["narration"] = text
                if boundaries:
                    # Provider timestamps are in 100-ns ticks, aligned with
                    # spoken audio. Clamp to the decoded clip duration.
                    timing_mode="provider_word_boundaries"
                    for marker in boundaries:
                        begin=max(0,min(length,float(marker["offset"])))
                        finish=min(length,begin+max(.07,float(marker["duration"])))
                        if finish>begin:
                            cues.append({
                                "start":round(clock+begin,3),
                                "end":round(clock+finish,3),
                                "word":marker["text"].strip(),
                                "scene":index,
                            })
                else:
                    # Kokoro currently has no phoneme alignment provider;
                    # keep an explicit proportional fallback for those renders.
                    for word_index, word in enumerate(words):
                        cues.append({
                            "start":round(clock + .08*length + .84*length*boundaries_est[word_index]/total,3),
                            "end":round(clock + .08*length + .84*length*boundaries_est[word_index+1]/total,3),
                            "word":word,
                            "scene":index,
                        })
                pieces.append(samples)
                gap = np.zeros(round(.28 * SAMPLE_RATE), dtype="<i2")
                pieces.append(gap)
                clock = scene["end"]
        if not pieces:
            raise RuntimeError("No narration audio")
        pieces.append(np.zeros(round(.5*SAMPLE_RATE), dtype="<i2"))
        all_audio = np.concatenate(pieces)
        if len(all_audio) / SAMPLE_RATE > 180:
            raise ValueError("Narration exceeds 180-second video limit")
        cfg["duration"] = round(len(all_audio) / SAMPLE_RATE, 4)
        cfg["scenes"][-1]["end"] = cfg["duration"]
        cfg["word_cues"] = cues
        cfg["voice"] = {"provider":provider, "voice":voice or (DEFAULT_KOKORO_VOICE if provider=="kokoro" else DEFAULT_EDGE_VOICE), "language":"en","word_alignment":timing_mode}
        with wave.open(str(dest),"wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(SAMPLE_RATE)
            out.writeframes(all_audio.tobytes())
        return {"file":str(dest),"duration":cfg["duration"],"words":len(cues),"provider":provider}
    finally:
        if engine is not None and hasattr(engine, "voices") and hasattr(engine.voices, "close"):
            engine.voices.close()
