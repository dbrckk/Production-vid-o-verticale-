#!/usr/bin/env python3
"""Export a fresh, source-attributed shortlist for the static Hugging Face UI.

No browser-side RSS proxy, private token, or speculative news item is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from topic_engine import current_headlines, MAX_AGE_HOURS


def export_news(path: Path, items: list[dict] | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    candidates = current_headlines(now=now) if items is None else items
    selected = []
    for item in candidates:
        try:
            stamp = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
            age = (now - stamp).total_seconds() / 3600
            if stamp.tzinfo is None or age < -1 or age > MAX_AGE_HOURS:
                continue
            if not item["url"].startswith("https://"):
                continue
            selected.append({key: item[key] for key in ("title","summary","source","published","url","importance")})
        except (KeyError, TypeError, ValueError):
            continue
    selected.sort(key=lambda item: item["importance"], reverse=True)
    payload = {
        "schema": 1,
        "generated_at": now.isoformat(),
        "max_age_hours": MAX_AGE_HOURS,
        "items": selected[:50],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("hf_space/news.json"))
    a = p.parse_args()
    result = export_news(a.output)
    print(f"Exported {len(result['items'])} recent sourced stories to {a.output}")
