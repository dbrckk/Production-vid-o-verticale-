"""Cinematic camera and transitions for actual animated 2D scenes.

The artwork moves below stable titles and subtitles. Camera scale/translation
are continuous within a shot. Near scene boundaries the previous animated
diagram dissolves into the next, instead of switching like a presentation.
"""
from __future__ import annotations

import math

from PIL import Image


def ease(value: float) -> float:
    v = max(0.0, min(1.0, float(value)))
    return v * v * (3.0 - 2.0 * v)


def camera_parameters(scene_index: int, phase: float) -> tuple[float, float, float]:
    """Zoom and pan in reference (576 x 1024) pixels.

    Positive zoom prevents empty edges; offsets are intentionally small enough
    to preserve the scientific diagram and 9:16 safe area.
    """
    # Cosine trajectory has continuous acceleration and no perceptible
    # abrupt camera velocity change at shot boundaries.
    v = (1.0 - math.cos(math.pi * max(0.0, min(1.0, phase)))) * .5
    odd = scene_index % 2
    zoom = (1.045 + 0.026 * v) if not odd else (1.071 - 0.026 * v)
    pan_x = (4.0 * (2 * v - 1)) * (-1 if odd else 1)
    pan_y = (4.6 * (2 * v - 1)) * (-1 if scene_index % 3 == 0 else 1)
    return zoom, pan_x, pan_y


def move_camera(painter, image: Image.Image, scene_index: int, phase: float,
                category: str | None = None) -> Image.Image:
    """Subject-adaptive art framing; subtitles and editorial titles stay still.

    The original diagram occupies the bottom half of the canvas. Physical
    science drawings benefit from an art-only push-in and upward offset.
    """
    zoom, pan_x, pan_y = camera_parameters(scene_index, phase)
    if category == "earthquake":
        zoom += .095
        pan_y += 60.
    elif category in ("ocean","volcano","weather"):
        zoom += .048
        pan_y += 24.
    elif category in ("biology","health","space"):
        zoom += .028
        pan_y += 10.
    a = 1.0 / zoom
    center_x = 288.0 * painter.s
    center_y = 570.0 * painter.s
    matrix = (
        a, 0, center_x * (1.0 - a) + pan_x * painter.s,
        0, a, center_y * (1.0 - a) + pan_y * painter.s,
    )
    return image.transform(
        image.size, Image.Transform.AFFINE, matrix,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(14, 9, 31, 255),
    )


def render_cinematic_art(painter, cfg: dict, t: float, scene_index: int, phase: float,
                         draw_scene, category: str):
    """Render foreground animation and a timed dissolve between adjacent scenes.

    The previous scene is rendered at its final pose and blended for a short
    380-ms boundary; title and subtitles are composited after this operation.
    """
    from scene_backdrops import environment, add_parallax
    current = environment(painter,category)
    add_parallax(painter,current,category,t,scene_index)
    draw_scene(painter, current, category, t, scene_index, phase)
    current = move_camera(painter, current, scene_index, phase, category)

    if scene_index <= 0:
        return current
    start = float(cfg["scenes"][scene_index]["start"])
    elapsed = max(0, t - start)
    fade_length = 0.38
    if elapsed >= fade_length:
        return current

    previous = environment(painter,category)
    old_scene = cfg["scenes"][scene_index - 1]
    # Never freeze the outgoing animation during a dissolve. Keep its
    # particles and seismic waves moving until the final blend frame.
    old_t = float(old_scene["end"]) - .001 + elapsed
    old_duration=max(.001,float(old_scene['end'])-float(old_scene['start']))
    old_phase=min(1.0,max(0.0,(old_t-float(old_scene['start']))/old_duration))
    add_parallax(painter,previous,category,old_t,scene_index-1)
    draw_scene(painter, previous, category, old_t, scene_index - 1, old_phase)
    previous = move_camera(painter, previous, scene_index - 1, old_phase, category)
    return Image.blend(previous, current, ease(elapsed / fade_length))


def title_motion(elapsed: float) -> tuple[float, float]:
    """Return per-frame title opacity and vertical offset in reference pixels."""
    v = ease(elapsed / .48)
    return v, (1.0 - v) * 11.0
