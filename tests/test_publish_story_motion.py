"""Publishing checks for staged volcanic visuals and genuine speech alignment.

These checks inspect actual drawn pixels and the provider's spoken words.
They do not synthesize or fake a natural voice in a delivery video.
"""
import numpy as np

from narration import continuous_scene_bounds
from studio import Painter
from subject_illustrations import volcanic_structure, _revealed_path


def test_volcanic_lava_front_advances_without_looping_back():
    path=[(285,525),(300,567),(337,634),(383,703),(440,800)]
    previous_y=0
    for step in range(101):
        visible=_revealed_path(path,step/100)
        end=visible[-1]
        assert end[1]>=previous_y-1e-8
        previous_y=end[1]
    assert visible[-1]==path[-1]


def test_volcano_publish_frames_reveal_more_lava_during_flow_stage():
    p=Painter(288,512)
    def make(phase):
        image=p.base.copy()
        volcanic_structure(p,image,12,4,phase)
        return np.asarray(image.convert("RGB"))
    early=make(.04)
    late=make(.96)
    # The late lava front reaches the southeastern slope, which is cold rock
    # at the beginning of the scene. Count warm-lit pixels in that region.
    y0,y1=round(580*p.s),round(820*p.s)
    x0,x1=round(326*p.s),round(508*p.s)
    def molten_pixels(image):
        region=image[y0:y1,x0:x1].astype(np.int16)
        red,green,blue=region[:,:,0],region[:,:,1],region[:,:,2]
        return int(((red>115)&(red>green+35)&(green>65)&(red>blue+30)).sum())
    assert molten_pixels(late)>molten_pixels(early)+35


def test_english_narrative_uses_actual_scene_boundary_words():
    speeches=[
        "Warm water moves across the ocean.",
        "Cold water sinks into the deep.",
        "Climate depends on the transport."
    ]
    scenes=[{"narration":s} for s in speeches]
    words=[x.strip(".") for sentence in speeches for x in sentence.split()]
    cues=[{"text":word,"offset":i*.27+0.04,"duration":.19} for i,word in enumerate(words)]
    bounds=continuous_scene_bounds(cues,scenes,5.5)
    assert bounds is not None
    indices,ends=bounds
    assert indices==[0,6,12,17]
    assert ends[0]==cues[6]["offset"]
    assert ends[1]==cues[12]["offset"]


def test_speech_alignment_handles_provider_tokenization_variations():
    scenes=[
        {"narration":"Earth's crust stores energy."},
        {"narration":"Some faults release it suddenly."},
        {"narration":"Seismic waves carry that energy."},
    ]
    words=[
        "Earth","s","crust","stores","energy",
        "Some","faults","release","it","suddenly",
        "Seismic","waves","carry","that","energy",
    ]
    cues=[{"text":word,"offset":.2*i+.04,"duration":.14} for i,word in enumerate(words)]
    aligned=continuous_scene_bounds(cues,scenes,3.8)
    assert aligned is not None
    assert aligned[0]==[0,5,10,15]


def test_badly_mismatched_voice_boundaries_are_rejected():
    scenes=[
        {"narration":"Science reveals how the ocean circulates."},
        {"narration":"Currents transport heat and nutrients."},
    ]
    cues=[{"text":word,"offset":i*.22,"duration":.13}
          for i,word in enumerate(["Nothing","in","this","audio","matches",
                                   "any","of","the","original","story","at","all"])]
    assert continuous_scene_bounds(cues,scenes,3.1) is None

def test_volcano_magma_chamber_visible_above_social_subtitles():
    from topic_engine import research_story
    cfg=research_story("Why do volcanoes erupt?",fetcher=lambda _: b"{}")
    assert cfg["evidence"]=="curated_science"
    p=Painter(288,512)
    # Stage zero shows underground magma, which must not be hidden
    # behind the bottom platform-safe subtitle area (starts at y=726).
    first=cfg["scenes"][0]
    frame=np.asarray(p.frame((first["start"]+first["end"])/2,cfg))
    chamber=frame[280:355,85:205,:].astype(np.int16)
    hot=(chamber[:,:,0]>120)&(chamber[:,:,0]>chamber[:,:,1]+30)&(
        chamber[:,:,1]>60)&(chamber[:,:,2]<145)
    assert hot.sum()>100


def test_repeated_topic_label_not_burned_into_video():
    from topic_engine import research_story
    cfg=research_story("Why do volcanoes erupt?",fetcher=lambda _: b"{}")
    p=Painter(288,512)
    written=[]
    original=p.text
    def record(d,text,x,y,size,fill,anchor="mm",bold=False):
        written.append(str(text))
        return original(d,text,x,y,size,fill,anchor=anchor,bold=bold)
    p.text=record
    p.frame(1.4,cfg)
    assert "VOLCANO ERUPTION" not in written
    # Sourced explanatory labels are still retained when meaningful.
    from topic_engine import create_story
    good=create_story("Why do ocean currents move?")
    good["evidence"]="noaa-sourced"
    good["scenes"][0]["metric"]="NOAA National Ocean Service"
    written.clear()
    p.frame(.5,good)
    assert "NOAA National Ocean Service" in written
