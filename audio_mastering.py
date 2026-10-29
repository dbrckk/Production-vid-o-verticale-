"""Broadcast-style voice-first soundtrack mastering for FFmpeg.

The narrator is the primary signal. The music bed is automatically ducked
under active speech and recovers naturally during the editorial pauses.
The music input is padded to prevent FFmpeg sidechain tail truncation.\nAll final audio is peak limited; no separate paid mixing service is required.
"""
from __future__ import annotations

def narration_mix() -> str:
    """A deterministic filter chain with voice-dependent sidechain ducking.

    Inputs: 1:a original music, 2:a mono neural narration.
    Output: [a] a mastered mix suitable for mobile speaker playback.

    asplit is essential: one copy drives the music compressor, the other is
    retained for the final mix (FFmpeg pads cannot be consumed twice).
    """
    return (
        "[1:a]volume=0.42,highpass=f=36,apad=pad_dur=1.5[bed];"
        # Light proximity EQ and softer compression retain a natural
        # presenter timbre rather than a harsh, synthetic broadcast voice.
        "[2:a]highpass=f=72,lowpass=f=14500,"
        "equalizer=f=185:t=q:w=0.9:g=1.2,"
        "equalizer=f=3250:t=q:w=1.3:g=-1.8,"
        "equalizer=f=6100:t=q:w=1.4:g=-1.4,"
        "acompressor=threshold=0.11:ratio=1.8:attack=18:release=235,"
        "volume=1.18[speech];"
        "[speech]asplit=2[key][narrator];"
        "[bed][key]sidechaincompress="
        "threshold=0.018:ratio=7:attack=24:release=420[ducked];"
        "[ducked][narrator]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.92:attack=6:release=90,"
        "loudnorm=I=-17:TP=-1.5:LRA=9,alimiter=limit=0.95[a]"
    )

def quality_targets() -> dict:
    return {
        "dialogue_primary": True,
        "music_ducking": "voice_sidechain",
        "speech_highpass_hz": 72,
        "speech_lowpass_hz": 14500,
        "mix_peak_limit": 0.95,
        "integrated_target_lufs": -17,
        "true_peak_target_dbtp": -1.5,
        "voice_language": "en",
    }
