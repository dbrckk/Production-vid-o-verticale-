"""Objective output checks for narrated English 9:16 motion documentaries.

This gate catches missing narration, silent/overloud audio, invalid timing,
wrong video format and static-image slideshows. It does not pretend to judge
art direction, factual accuracy, or human-like voice quality automatically.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np

CHECK_WIDTH=180
CHECK_HEIGHT=320


class QualityFailure(ValueError):
    pass


def _execute(args):
    p=subprocess.run(args,capture_output=True,check=True)
    return p.stdout.decode("utf-8","replace"),p.stderr.decode("utf-8","replace")


def _probe(movie:Path):
    stdout,_=_execute([
        "ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,codec_name,profile,pix_fmt,avg_frame_rate,"
        "color_space,color_primaries,color_transfer,width,height,sample_rate",
        "-of","json",str(movie),
    ])
    return json.loads(stdout)


def _loudness(movie:Path):
    # The analyser reports input_i and input_tp of the *finished* compressed
    # MP4, not of the pre-mix WAV or compressor's internal signal.
    _,log=_execute([
        "ffmpeg","-nostdin","-hide_banner","-loglevel","info","-i",str(movie),
        "-vn","-af","loudnorm=I=-17:TP=-1.5:LRA=9:print_format=json",
        "-f","null","-",
    ])
    payload=re.findall(r'\{\s*"input_i".*?\}',log,re.S)
    if not payload:
        raise QualityFailure("Unable to measure finished audio loudness")
    metrics=json.loads(payload[-1])
    integrated=float(metrics["input_i"])
    true_peak=float(metrics["input_tp"])
    if not (math.isfinite(integrated) and math.isfinite(true_peak)):
        raise QualityFailure("Silent or invalid audio detected")
    return integrated,true_peak


def _motion(movie:Path, duration:float):
    # Compare the area of the *illustration*, excluding header, progress bar,
    # large chapter title and the bottom subtitles.
    _,_=None,None
    frame_bytes=CHECK_WIDTH*CHECK_HEIGHT*3
    cmd=[
        "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",str(movie),
        "-t",str(min(duration,60)),"-an","-vf",
        f"fps=1,scale={CHECK_WIDTH}:{CHECK_HEIGHT}:flags=fast_bilinear",
        "-pix_fmt","rgb24","-f","rawvideo","pipe:1",
    ]
    output=subprocess.run(cmd,capture_output=True,check=True).stdout
    count=len(output)//frame_bytes
    if count<3:
        raise QualityFailure("Insufficient frames for animation verification")
    frames=np.frombuffer(output[:count*frame_bytes],dtype=np.uint8)
    frames=frames.reshape(count,CHECK_HEIGHT,CHECK_WIDTH,3)
    region=frames[:,102:240,19:161].astype(np.int16)
    changes=np.abs(np.diff(region,axis=0))
    moving=(changes>8).any(axis=3).mean(axis=(1,2))
    return {
        "sampled_frames":int(count),
        "active_intervals":round(float(np.mean(moving>.015)),3),
        "mean_motion_ratio":round(float(np.mean(moving)),4),
    }



def _temporal_motion(movie:Path, duration:float, frame_rate:float):
    """Inspect actual adjacent 30/60 FPS frames, not only 1 FPS snapshots.

    A small image sampling window keeps runtime and memory bounded even on
    constrained free Render instances. Distinguishes true new frames from
    repeated/frozen frames that were merely tagged as 60 FPS.
    """
    if frame_rate<29.5 or duration<1.8:
        return None
    w,h=90,160
    frame_size=w*h*3
    fps=min(60,round(frame_rate))
    begin=.45
    seconds=min(1.5,max(.1,duration-begin-.15))
    cmd=[
        "ffmpeg","-nostdin","-hide_banner","-loglevel","error",
        "-ss",str(begin),"-i",str(movie),"-t",str(seconds),
        "-an","-vf",f"fps={fps},scale={w}:{h}:flags=fast_bilinear",
        "-pix_fmt","rgb24","-f","rawvideo","pipe:1",
    ]
    output=subprocess.run(cmd,capture_output=True,check=True).stdout
    count=len(output)//frame_size
    if count<max(12,round(fps*.6)):
        raise QualityFailure("Not enough adjacent publication frames")
    frames=np.frombuffer(output[:count*frame_size],dtype=np.uint8).reshape(count,h,w,3)
    # Crop the actual scientific animation, not captions or station labels.
    crop=frames[:,50:132,10:80].astype(np.int16)
    changed=(np.abs(np.diff(crop,axis=0))>7).any(axis=3)
    pixel_fraction=changed.mean(axis=(1,2))
    active=float(np.mean(pixel_fraction>.002))
    return {
        "sampled_adjacent_frames":int(count),
        "adjacent_frame_activity":round(active,3),
        "mean_adjacent_motion_ratio":round(float(pixel_fraction.mean()),4),
    }


def inspect(movie:Path, manifest_path:Path):
    movie=Path(movie)
    manifest=json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not movie.is_file() or movie.stat().st_size<2500:
        raise QualityFailure("MP4 is missing or empty")
    probe=_probe(movie)
    streams=probe.get("streams",[])
    video=next((s for s in streams if s.get("codec_type")=="video"),None)
    audio=next((s for s in streams if s.get("codec_type")=="audio"),None)
    if not video or video.get("codec_name")!="h264":
        raise QualityFailure("H.264 video track is required")
    width,height=int(video["width"]),int(video["height"])
    if width*16!=height*9 or width<288:
        raise QualityFailure("Exact vertical 9:16 video is required")
    if not audio or audio.get("codec_name")!="aac" or audio.get("sample_rate")!="48000":
        raise QualityFailure("48 kHz AAC narration audio track is required")
    profile_name=manifest.get("export_profile","")
    publication=profile_name in ("publication_1080p","publication_1080p60")
    if publication:
        rate=video.get("avg_frame_rate","0/1")
        try:
            numerator,denominator=map(int,rate.split("/"))
            real_fps=numerator/denominator
        except (ValueError,ZeroDivisionError):
            real_fps=0.
        minimum_fps=59.5 if profile_name=="publication_1080p60" else 29.5
        if width < 1080 or real_fps < minimum_fps:
            raise QualityFailure("Publication requires full-HD 9:16 at the declared frame rate")
        if video.get("profile")!="High" or video.get("pix_fmt")!="yuv420p":
            raise QualityFailure("Publication requires H.264 High, yuv420p compatibility")
        for key in ("color_space","color_primaries","color_transfer"):
            if video.get(key)!="bt709":
                raise QualityFailure("Publication color metadata must be BT.709")
        encoding=manifest.get("encoding") or {}
        if encoding.get("chapter_numbers") is not False or encoding.get("watermark") is not False:
            raise QualityFailure("Publication must not include scene numbers or watermarks")

    duration=float(probe["format"]["duration"])
    if not math.isfinite(duration) or duration<=2:
        raise QualityFailure("Invalid video duration")
    expected=float(manifest.get("duration",0))
    if abs(duration-expected)>.55:
        raise QualityFailure("Truncated or lengthened final video")
    voice=manifest.get("voice")
    if not isinstance(voice,dict) or voice.get("language")!="en":
        raise QualityFailure("English narrated voice metadata is required")
    cues=manifest.get("word_cues")
    if not isinstance(cues,list) or len(cues)<5:
        raise QualityFailure("Timed English subtitles are missing")

    previous=-1.
    for cue in cues:
        start,end=float(cue["start"]),float(cue["end"])
        if (not math.isfinite(start) or not math.isfinite(end) or start<previous-.001
                or start<0 or end<=start or end>duration+.4):
            raise QualityFailure("Narrated words are out of sync with final duration")
        previous=start

    integrated,peak=_loudness(movie)
    if not -22<=integrated<=-12:
        raise QualityFailure(f"Dialogue audio loudness out of range: {integrated:.1f} LUFS")
    if peak>0.3:
        raise QualityFailure(f"Audio true peak above safety threshold: {peak:.1f} dBTP")

    movement=_motion(movie,duration)
    if movement["active_intervals"]<.65 or movement["mean_motion_ratio"]<.025:
        raise QualityFailure("The picture behaves like a slideshow, not live motion")
    temporal=_temporal_motion(movie,duration,real_fps if publication else
        float(manifest.get("fps",15)))
    if publication and temporal is not None and temporal["adjacent_frame_activity"]<.55:
        raise QualityFailure("High-FPS output contains too many repeated or frozen frames")
    return {
        "passed":True,"width":width,"height":height,
        "publication_spec":publication,"export_profile":manifest.get("export_profile","review"),
        "duration_seconds":round(duration,3),"audio_language":"en",
        "narrated_words":len(cues),"loudness_lufs":round(integrated,2),
        "true_peak_dbtp":round(peak,2),"word_alignment":voice.get("word_alignment"),
        **movement,**(temporal or {}),
    }


def main():
    parser=argparse.ArgumentParser(description="Check narrated 9:16 MP4 production quality")
    parser.add_argument("--video",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    report=inspect(args.video,args.manifest)
    print(json.dumps(report,indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
