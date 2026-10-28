"""Universal topics, live-news provenance and playable render integration tests."""
from datetime import datetime,timezone
import json,random,subprocess
import pytest
from pathlib import Path
from studio import Painter,render
from topic_engine import (parse_rss,create_story,validate_universal,
                          random_important_news,research_story,wikipedia_context)
from webapp import State

NOW=datetime(2026,10,28,12,tzinfo=timezone.utc)
RSS=b'''<rss><channel><item><title>Accord international sur le climat et l'energie</title>
<link>https://example.org/climat</link><pubDate>Wed, 28 Oct 2026 11:30:00 GMT</pubDate>
<description>Les representants ont annonce un nouvel accord. Des discussions doivent se poursuivre.</description></item>
<item><title>Le secret des biscuits</title><link>https://example.org/cuisine</link>
<pubDate>Thu, 01 Oct 2026 11:00:00 GMT</pubDate></item></channel></rss>'''

def test_news_source_freshness_random():
    news=parse_rss(RSS,'Test News',NOW)
    assert len(news)==1 and news[0]['source']=='Test News'
    assert news[0]['importance']>1.5
    selected=random_important_news(fetcher=lambda _:RSS,rng=random.Random(7),now=NOW)
    assert selected['url']=='https://example.org/climat'

def test_no_unverified_random_news():
    with pytest.raises(RuntimeError,match='Aucune actualité'):
        random_important_news(fetcher=lambda _:b'<rss/>',now=NOW)

@pytest.mark.parametrize('topic',[
    'Pourquoi les océans sont salés ?',
    'La révolution industrielle',
    'Développer une application mobile',
    'La pollution plastique des océans'])
def test_any_topic_renders_all_scenes(topic):
    cfg=create_story(topic)
    validate_universal(cfg)
    assert cfg['topic']==topic and cfg['evidence']=='unsourced'
    assert len(cfg['scenes'])==6 and cfg['scenes'][-1]['end']==30
    assert Painter(288,512).frame(19,cfg).size==(288,512)

def test_wikipedia_factual_context():
    response={'query':{'pages':{'1':{'pageid':123,'title':'Océan',
      'extract':'Les océans sont de vastes étendues d’eau salée. Leur salinité varie en fonction de plusieurs facteurs et conditions naturelles.'}}}}
    fetch=lambda _:json.dumps(response).encode()
    assert wikipedia_context('océan',fetcher=fetch)['url'].endswith('123')
    cfg=research_story('océan',fetcher=fetch)
    assert cfg['evidence']=='wikipedia'
    assert 'océans' in cfg['scenes'][1]['caption']
    assert cfg['sources'][0]['source']=='Wikipédia'

def test_news_video_has_source():
    item=parse_rss(RSS,'Test News',NOW)[0]
    cfg=create_story(item['title'],article=item)
    assert cfg['evidence']=='rss'
    assert cfg['sources'][0]['url']==item['url']
    assert cfg['scenes'][-1]['caption'].startswith('Publication')

def test_reject_invalid_timeline():
    cfg=create_story('Histoire du papier')
    cfg['scenes'][2]['start']+=1
    with pytest.raises(ValueError):validate_universal(cfg)

def test_mp4_audio_manifest(tmp_path):
    cfg=create_story('Pourquoi les vagues existent-elles ?',duration=12)
    out=tmp_path/'test.mp4'
    result=render(cfg,out,width=288,fps=2,preview=True)
    assert result['mode']=='universal' and result['frames']==24
    assert (tmp_path/'test.json').exists() and (tmp_path/'cover.png').exists()
    streams=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(out)],
                   check=True,capture_output=True,text=True).stdout)['streams']
    assert any(s['codec_type']=='video' for s in streams)
    assert any(s['codec_type']=='audio' for s in streams)

def test_server_refuses_parallel_and_unknown_quality(tmp_path):
    state=State(tmp_path)
    state.busy=True
    with pytest.raises(RuntimeError):state.start('Formation des étoiles',None,'preview')
    with pytest.raises(ValueError):state.start('Formation des étoiles',None,'ultra-8k')
