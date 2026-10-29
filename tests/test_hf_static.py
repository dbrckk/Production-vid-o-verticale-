"""Hugging Face static site publication and freshness/selection contracts."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import sys

import pytest

from topic_engine import parse_rss
from scripts.export_news import export_news
from generate_topic import build

NOW = datetime(2026,10,29,8,tzinfo=timezone.utc)
RSS = b"""<rss><channel><item><title>Important accord climatique international</title>
<link>https://news.example.net/article/1</link><pubDate>Thu, 29 Oct 2026 07:30:00 GMT</pubDate>
<description>Un accord a ete annonce entre plusieurs pays.</description></item></channel></rss>"""
ROOT = Path(__file__).resolve().parents[1]


def test_static_hf_space_manifest_and_no_private_token_leaks():
    readme = (ROOT / 'hf_space/README.md').read_text(encoding='utf8')
    assert 'sdk: static' in readme and 'app_file: index.html' in readme
    html = (ROOT / 'hf_space/index.html').read_text(encoding='utf8')
    script = (ROOT / 'hf_space/app.js').read_text(encoding='utf8')
    assert 'id="random"' in html
    assert 'id="create"' in html
    assert 'article_url' in script
    assert 'localStorage' not in script and 'sessionStorage' not in script
    assert 'https://api.github.com/repos/' in script


def test_export_news_timestamps_sources_and_invalid_items(tmp_path):
    valid = parse_rss(RSS, 'Actualites verifiees', now=NOW)[0]
    old = dict(valid, published=(NOW-timedelta(hours=100)).isoformat())
    invalid = dict(valid, url='http://invalid.example')
    target = tmp_path / 'news.json'
    data = export_news(target, items=[valid, old, invalid], now=NOW)
    assert data['schema'] == 1 and len(data['items']) == 1
    assert data['items'][0]['url'] == valid['url']
    assert json.loads(target.read_text())['items'][0]['source'] == 'Actualites verifiees'


def test_exact_rss_article_url_selection(monkeypatch):
    import generate_topic
    valid = parse_rss(RSS, 'Verified', now=NOW)[0]
    monkeypatch.setattr(generate_topic, 'current_headlines', lambda: [valid])
    cfg = build(None, False, 30, article_url=valid['url'])
    assert cfg['evidence'] == 'rss'
    assert cfg['sources'][0]['url'] == valid['url']
    with pytest.raises(ValueError,match='not present'):
        build(None, False, 30, article_url='https://news.example.net/old')
    with pytest.raises(ValueError,match='Invalid'):
        build(None, False, 30, article_url='http://insecure.example')


@pytest.mark.parametrize('path', ['hf_space/README.md','hf_space/app.js',
                                  'hf_space/style.css','hf_space/index.html'])
def test_static_space_assets_present(path):
    assert (ROOT / path).stat().st_size > 60


def test_news_export_cli_offline(tmp_path):
    # Uses a local module execution to ensure importing scripts works as checked in.
    command = [sys.executable, '-c',
               "from pathlib import Path; from scripts.export_news import export_news; "
               "export_news(Path(r'" + str(tmp_path / 'empty.json') +
               "'),items=[])"]
    subprocess.run(command,check=True,cwd=ROOT)
    assert json.loads((tmp_path / 'empty.json').read_text())['items'] == []
