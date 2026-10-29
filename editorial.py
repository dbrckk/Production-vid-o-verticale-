"""Editorially authored English scripts for well-defined science questions.

These are not synthetic current events: known science concepts are scripted once and
reused only when the question matches a narrow trigger. Unknown topics still require
external evidence instead of pretending that generic slides explain them.
"""
from __future__ import annotations

import re

# Each beat contains a visible headline and genuinely spoken English narration.
# Keep each section short enough for a natural ~3–6 second neural voice segment.
EXPLAINERS = {
    "ocean_currents": {
        "triggers": (r"\bocean currents?\b", r"\bsea currents?\b", r"\bthermohaline\b"),
        "category": "ocean",
        "beats": [
            ("THE OCEAN NEVER STOPS", "Even when the surface looks calm, vast streams of seawater are moving beneath it."),
            ("WIND STARTS THE FLOW", "Winds push water across the surface. Earth's rotation bends that motion into enormous circulating systems."),
            ("COLD WATER CAN SINK", "When seawater cools or grows saltier, it often becomes denser and sinks below warmer water."),
            ("A DEEP GLOBAL NETWORK", "These differences help connect surface and deep currents, carrying water between ocean basins."),
            ("HEAT TRAVELS WITH WATER", "Currents move heat, nutrients, and oxygen. That changes regional climates and supports marine life."),
            ("AN OCEAN IN MOTION", "What seems like still blue water is really a moving system connected to the whole planet."),
        ],
    },
    "volcano_eruption": {
        "triggers": (r"\bvolcano(?:es)?\b", r"\bvolcanic eruptions?\b", r"\bmagma\b"),
        "category": "volcano",
        "beats": [
            ("DEEP BENEATH THE SURFACE", "A volcanic eruption begins when molten rock, called magma, collects beneath the ground."),
            ("PRESSURE BUILDS", "Dissolved gases can expand as magma rises. That growing pressure helps drive material upward."),
            ("THE ROCK FINDS A PATH", "Magma travels through fractures until it may break through a vent at the surface."),
            ("LAVA AND ASH", "Once magma reaches the surface, it becomes lava. Some eruptions also send ash high into the air."),
            ("EVERY ERUPTION IS DIFFERENT", "Runny magma may flow in long streams, while gas-rich magma can erupt much more violently."),
            ("THE LANDSCAPE CHANGES", "Over time, repeated eruptions can build mountains, reshape coastlines, and create new land."),
        ],
    },
    "ocean_tides": {
        "triggers": (r"\bocean tides?\b", r"\bsea tides?\b", r"\bhigh tide\b", r"\blow tide\b", r"\btides?\b"),
        "category": "ocean",
        "beats": [
            ("WHY THE SEA RISES", "Across the planet, coastlines experience the rhythmic rise and fall we call tides."),
            ("THE MOON PULLS ON EARTH", "The Moon's gravity is the main influence, creating a repeating difference in ocean levels."),
            ("EARTH KEEPS ROTATING", "As our planet turns, many coastlines move through two tidal highs and two lows each lunar day."),
            ("THE SUN ADDS ITS PULL", "The Sun also matters. When its effect aligns with the Moon, tidal ranges can grow."),
            ("COASTLINES CHANGE THE PATTERN", "The shape of each bay and ocean basin changes when high tides arrive and how large they become."),
            ("A PLANETARY RHYTHM", "Every tide is a visible reminder that the Earth, Moon, and Sun are connected."),
        ],
    },
    "photosynthesis": {
        "triggers": (r"\bphotosynthesis\b", r"\bhow plants (?:make|produce) (?:food|energy)\b"),
        "category": "biology",
        "beats": [
            ("SUNLIGHT HITS A LEAF", "Inside leaves, green pigments capture some of the energy arriving from sunlight."),
            ("WATER ENTERS THE PLANT", "Roots absorb water and carry it into the cells where photosynthesis takes place."),
            ("CARBON DIOXIDE COMES IN", "Tiny openings in leaves allow carbon dioxide from the air to enter."),
            ("LIGHT ENERGY POWERS CHANGE", "The plant uses captured energy to turn water and carbon dioxide into sugars."),
            ("OXYGEN IS RELEASED", "During this process, oxygen is produced and much of it returns to the atmosphere."),
            ("THE FOUNDATION OF FOOD WEBS", "Those sugars fuel the plant and, indirectly, many of the living things that depend on it."),
        ],
    },
    "solar_system": {
        "triggers": (r"\bsolar system\b", r"\bplanets? orbit\b", r"\bwhy (?:do )?planets? (?:orbit|move)\b"),
        "category": "space",
        "beats": [
            ("ONE STAR HOLDS THE SYSTEM", "The Sun contains almost all the mass in our solar system."),
            ("GRAVITY SHAPES THE PATHS", "Its gravity continually bends the paths of planets as they move through space."),
            ("PLANETS KEEP MOVING", "They don't fall straight into the Sun because they already have sideways motion."),
            ("EACH ORBIT HAS A RHYTHM", "Planets closer to the Sun usually complete their orbits faster than distant planets."),
            ("MOONS HAVE THEIR OWN PATHS", "Many planets are orbited by natural satellites, adding another layer of motion."),
            ("A SYSTEM IN CONSTANT MOTION", "Our solar system is not a still picture. It's a moving family of worlds."),
        ],
    },
    "heartbeat": {
        "triggers": (r"\bheart(?:beat| beat| beats)\b", r"\bwhy (?:does|do) (?:our|the) heart\b"),
        "category": "health",
        "beats": [
            ("YOUR HEART IS A PUMP", "Your heart keeps blood moving, delivering oxygen and nutrients to tissues across your body."),
            ("AN ELECTRICAL SIGNAL BEGINS", "Specialized cells create an electrical rhythm that starts each heartbeat."),
            ("THE UPPER CHAMBERS CONTRACT", "The atria push blood into the lower chambers, called ventricles."),
            ("THE VENTRICLES PUMP", "Then the ventricles contract, sending blood toward the lungs and around the body."),
            ("THE CYCLE REPEATS", "Valves help keep blood moving in the right direction as the chambers relax and refill."),
            ("EVERY BEAT KEEPS YOU GOING", "The rhythm changes with activity, rest, and the body's need for oxygen."),
        ],
    },
    "earthquakes": {
        "triggers": (r"\bearthquakes?\b", r"\btectonic plates?\b", r"\bseismic waves?\b"),
        "category": "earthquake",
        "beats": [
            ("THE GROUND IS NOT STILL", "Earth's outer shell is broken into huge tectonic plates that move very slowly."),
            ("ROCKS CAN GET STUCK", "Near faults, friction can prevent rocks from sliding even while forces keep building."),
            ("THE FAULT SUDDENLY SLIPS", "When stress overcomes friction, part of the fault moves and releases stored energy."),
            ("SEISMIC WAVES SPREAD", "Vibrations travel outward through the Earth, shaking the ground as they pass."),
            ("THE EFFECTS VARY", "How strongly a place shakes depends on the earthquake, the distance, and the local ground."),
            ("SCIENCE MEASURES THE MOTION", "Seismometers record these waves, helping researchers understand what happened below."),
        ],
    },
    "weather": {
        "triggers": (r"\bweather\b", r"\brain forms?\b", r"\bhow clouds? form\b", r"\bcloud formation\b"),
        "category": "weather",
        "beats": [
            ("THE AIR IS ALWAYS MOVING", "Sunlight heats Earth's surface unevenly, creating differences in air temperature."),
            ("WARM AIR CAN RISE", "As warm air rises, surrounding pressure drops and that air expands and cools."),
            ("CLOUDS BEGIN TO FORM", "If enough water vapor condenses into tiny droplets, clouds can become visible."),
            ("WIND MOVES THE SYSTEM", "Pressure differences help move air from one region to another, shaping winds."),
            ("MOISTURE CAN FALL", "When droplets or ice crystals grow large enough, they can fall as rain or snow."),
            ("A CHANGING ATMOSPHERE", "Weather emerges from heat, moisture, pressure, and motion interacting over time."),
        ],
    },
}

def match_explainer(topic: str) -> tuple[str, dict] | None:
    text = str(topic).casefold()
    for name, item in EXPLAINERS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in item["triggers"]):
            return name, item
    return None


def apply_explainer(cfg: dict, topic: str) -> bool:
    """Replace generic narrated slides with meaningful, non-repetitive action beats."""
    matched = match_explainer(topic)
    if not matched:
        return False
    name, item = matched
    if len(cfg.get("scenes", [])) != len(item["beats"]):
        return False
    for scene, (headline, spoken) in zip(cfg["scenes"], item["beats"]):
        scene["headline"] = headline
        scene["caption"] = spoken
        scene["narration"] = spoken
        scene["metric"] = name.replace("_", " ").upper()
    cfg["evidence"] = "curated_science"
    cfg["editorial_template"] = name
    cfg["motion_category"] = item["category"]
    return True


def compose_news_story(title: str, article: dict, duration: int) -> dict:
    """A source-bound English news brief: fewer factual scenes beat six empty slides.

    Source date and attribution are mandatory, and the narration consists only
    of the title, the RSS description and editorial attribution. Never invent
    quotations, casualty figures, consequences, or future developments.
    """
    from datetime import datetime
    from topic_engine import VISUALS, clean, validate_universal
    source = clean(article.get("source", ""), 70)
    description = clean(article.get("summary", ""), 330)
    published = article.get("published", "")
    url = article.get("url", "")
    if not source or not published or not str(url).startswith("https://"):
        raise ValueError("A current news documentary requires an identified source")
    if len(description) < 24:
        raise ValueError("Not enough sourced information to narrate this news story")
    date = str(published)[:10]
    try:
        datetime.fromisoformat(date)
    except (ValueError, TypeError) as exc:
        raise ValueError("News publication date is invalid") from exc
    # Preserve full sentences when possible; split lengthy briefs at punctuation.
    phrases = [s.strip() for s in re.split(r"(?<=[.!?])\\s+", description) if len(s.strip()) > 10]
    if not phrases:
        phrases = [description]
    beats = [(title.upper()[:145], f"Here is the latest from {source}. {title}.", "NEWS UPDATE")]
    for ix, phrase in enumerate(phrases[:3]):
        headlines = ("THE VERIFIED REPORT", "WHAT ELSE WAS REPORTED", "MORE FROM THE SOURCE")
        beats.append((headlines[ix], phrase[:180], "SOURCE: " + source.upper()))
    beats.append(("SOURCE AND DATE",
                  f"Reported on {date} by {source}. Read the original report for continuing updates.",
                  "ORIGINAL REPORT LINKED"))
    count = len(beats)
    scenes = []
    for ix, (headline, spoken, stamp) in enumerate(beats):
        scenes.append({
            "start": round(duration * ix / count, 3),
            "end": round(duration * (ix+1) / count, 3) if ix+1 < count else float(duration),
            "headline": headline,
            "caption": spoken[:180],
            "narration": spoken[:180],
            "metric": stamp,
            "visual": VISUALS[ix % len(VISUALS)],
        })
    cfg = {
        "mode": "universal", "language": "en", "topic": title,
        "duration": duration, "scenes": scenes, "evidence": "rss",
        "editorial_policy": "source_only_no_fabricated_details",
        "sources": [{key: article[key] for key in ("title", "source", "published", "url")}],
    }
    validate_universal(cfg)
    return cfg
