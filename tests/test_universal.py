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
    with pytest.raises(RuntimeError,match='No recent verifiable news'):
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
      'extract':'Oceans are large bodies of saline water on our planet. Salinity varies due to currents, evaporation, and multiple natural processes.'}}}}
    fetch=lambda _:json.dumps(response).encode()
    assert wikipedia_context('océan',fetcher=fetch)['url'].endswith('123')
    cfg=research_story('ocean',fetcher=fetch)
    assert cfg['evidence']=='wikipedia'
    assert 'Oceans' in cfg['scenes'][1]['caption']
    assert cfg['sources'][0]['source']=='Wikipedia'

def test_news_video_has_source():
    item=parse_rss(RSS,'Test News',NOW)[0]
    cfg=create_story(item['title'],article=item)
    assert cfg['evidence']=='rss'
    assert cfg['sources'][0]['url']==item['url']
    assert cfg['scenes'][-1]['caption'].startswith('Reported')

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
    with pytest.raises(RuntimeError):state.start('Star formation',None,'preview')
    with pytest.raises(ValueError):state.start('Star formation',None,'ultra-8k')


@pytest.mark.parametrize(('topic','category'),[
    ('Comment se forment les volcans ?','volcano'),
    ('Pourquoi les océans sont-ils salés ?','ocean'),
    ('Comment fonctionne une IA ?','tech'),
    ('Comprendre la santé humaine','health'),
    ('Pourquoi les prix augmentent-ils ?','economy'),
    ('Les planètes de notre système solaire','space'),
    ('Histoire du papier','general'),
])
def test_semantic_topic_category_and_frame(topic,category):
    from universal import topic_category
    assert topic_category(topic)==category
    frame=Painter(288,512).frame(0.8,create_story(topic))
    assert frame.size==(288,512)

def test_mobile_web_app_serves_ui_and_authenticated_news(tmp_path,monkeypatch):
    from http.server import ThreadingHTTPServer
    from threading import Thread
    from urllib.request import Request,urlopen
    from urllib.error import HTTPError
    import webapp
    from webapp import Handler,State
    item=parse_rss(RSS,'Test News',NOW)[0]
    monkeypatch.setattr(webapp,'random_important_news',lambda:item)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    server.state=State(tmp_path)
    server.token='super-secret-access-token'
    server.news_provider=lambda:[item]
    worker=Thread(target=server.serve_forever,daemon=True)
    worker.start()
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        with urlopen(base+'/') as response:
            html=response.read().decode()
            assert 'Random important news' in html
            assert 'Create video' in html
        with pytest.raises(HTTPError) as exc:
            urlopen(base+'/api/random')
        assert exc.value.code==401
        req=Request(base+'/api/random',headers={'X-Studio-Token':server.token})
        with urlopen(req) as response:
            news=json.load(response)
            assert news['article']['title']==item['title']
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=4)

def test_user_brief_becomes_factual_content_without_fabrication():
    from topic_engine import research_story
    briefing=('Understanding our company. We built a tool to organize complex data. '
              'Our team has improved reliability over several years. '
              'This week, measurements show faster response times.')
    cfg=research_story(briefing,fetcher=lambda _:b'{"query":{"pages":{}}}')
    assert cfg['evidence']=='user_provided'
    assert 'organize complex data' in cfg['scenes'][2]['caption']
