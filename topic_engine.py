"""Sourced, no-API-key universal story generation and important recent RSS selection."""
from __future__ import annotations
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
import json
import math
import random
import re
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

FEEDS = (
    ('BBC World','https://feeds.bbci.co.uk/news/world/rss.xml'),
    ('BBC Science','https://feeds.bbci.co.uk/news/science_and_environment/rss.xml'),
    ('The Guardian','https://www.theguardian.com/world/rss'),
    ('BBC Technology','https://feeds.bbci.co.uk/news/technology/rss.xml'),
    ('BBC Business','https://feeds.bbci.co.uk/news/business/rss.xml'),
)
IMPACT_WORDS = ('élection','guerre','climat','séisme','accord','santé','énergie','économie',
                'espace','science','crise','urgence','election','war','climate','earthquake',
                'deal','health','energy','economy','space','discovery','crisis','flood')
VISUALS = ('focus','globe','timeline','network','compare','question')
MAX_AGE_HOURS = 72

def clean(value: str, limit: int = 220) -> str:
    raw = re.sub(r'<[^>]*>',' ',unescape(str(value or '')))
    raw = re.sub(r'\s+',' ',raw).strip()
    return raw[:limit].rsplit(' ',1)[0].rstrip(' ,;:-') if len(raw)>limit else raw

def _date(value: str):
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        try: return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)
        except (TypeError, ValueError, AttributeError): return None

def parse_rss(xml_bytes: bytes, source: str, now: datetime | None=None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    if len(xml_bytes)>1_500_000: raise ValueError('RSS feed too large')
    root=ET.fromstring(xml_bytes)
    records=[]
    ns='{http://www.w3.org/2005/Atom}'
    for node in list(root.findall('.//item'))+list(root.findall(f'.//{ns}entry')):
        def txt(*tags):
            for tag in tags:
                elem=node.find(tag)
                if elem is not None and elem.text:return elem.text.strip()
            return ''
        title=clean(txt('title',ns+'title'),160)
        link=txt('link')
        if not link:
            for e in node.findall(ns+'link'):
                if e.get('rel','alternate')=='alternate':
                    link=e.get('href','')
                    break
        published=_date(txt('pubDate','published','updated',ns+'published',ns+'updated'))
        summary=clean(txt('description','summary',ns+'summary'),310)
        age=(now-published).total_seconds()/3600 if published else float('inf')
        if not(title and published and -1<=age<=MAX_AGE_HOURS):continue
        parsed=urlparse(link)
        if parsed.scheme!='https' or not parsed.hostname:continue
        importance=1+max(0,MAX_AGE_HOURS-age)/MAX_AGE_HOURS
        importance+=sum(.55 for term in IMPACT_WORDS if term in title.casefold())
        records.append(dict(title=title,summary=summary,source=source,published=published.isoformat(),
                            url=link,importance=round(importance,3)))
    return records

def current_headlines(fetcher=None,now:datetime|None=None) -> list[dict]:
    if fetcher is None:
        def fetcher(url):
            req=Request(url,headers={'User-Agent':'VerticalScienceStudio/1.0 (RSS reader)'})
            with urlopen(req,timeout=5) as response:
                return response.read(1_500_001)
    unique={}
    for source,url in FEEDS:
        try:
            for item in parse_rss(fetcher(url),source,now):
                normalized=re.sub(r'\W+','',item['title'].casefold())
                if normalized not in unique or item['importance']>unique[normalized]['importance']:
                    unique[normalized]=item
        except (OSError,TimeoutError,ValueError,ET.ParseError):
            continue
    return sorted(unique.values(),key=lambda x:x['importance'],reverse=True)

def random_important_news(fetcher=None,rng=None,now=None) -> dict:
    items=current_headlines(fetcher,now)
    if not items:raise RuntimeError('No recent verifiable news available: feeds are unavailable or stale')
    # English-language outlets only: narration and on-screen text stay in English.
    candidates=items[:20]
    rng=rng or random.SystemRandom()
    return rng.choices(candidates,weights=[max(.01,item['importance']-.75)**2 for item in candidates],k=1)[0]

def _phrases(text:str) -> list[str]:
    return [clean(t,145) for t in re.split(r'(?<=[.!?])\s+',clean(text,900)) if len(t.strip())>16]

def validate_universal(cfg:dict) -> None:
    if cfg.get('mode')!='universal':raise ValueError('Invalid universal mode')
    duration=float(cfg.get('duration',0))
    if not math.isfinite(duration) or duration<1 or duration>180:raise ValueError('Invalid duration')
    scenes=cfg.get('scenes')
    if not isinstance(scenes,list) or not scenes:raise ValueError('Missing scenes')
    last=0.
    for s in scenes:
        a,b=float(s['start']),float(s['end'])
        if not all(math.isfinite(t) for t in (a,b)) or abs(a-last)>.001 or not a<b<=duration+.001:
            raise ValueError('Scene timeline must have no gaps or overlaps')
        if s.get('visual') not in VISUALS:raise ValueError('Unknown universal visual')
        for field in ('headline','caption'):
            if not isinstance(s.get(field),str) or not 1<=len(s[field])<=200:
                raise ValueError('Invalid text length')
        last=b
    if abs(last-duration)>.001:raise ValueError('Scenes do not cover duration')


def require_english_topic(topic: str):
    """Fail closed on obviously French input instead of generating mixed-language videos.

    An arbitrary-language translation service is intentionally NOT simulated here.
    """
    if not isinstance(topic,str) or len(topic.strip())<3:
        raise ValueError("Enter a topic in English")
    value=topic.casefold()
    french_words=re.findall(r"\b(?:pourquoi|comment|fonctionne|fonctionnent|le|la|du|de|quelles|quels|est-ce|sont-ils|sommes|avez-vous|les|des|une|dans|nous|vous|notre|aujourd'hui|commentaire|expliquer|étude|découverte|réchauffement)\b",value)
    if len(french_words)>=2 or re.search(r"[éèêëàâîïôûùçœ]", value):
        raise ValueError("English only: please enter or select an English-language topic")

def create_story(topic:str, *,article:dict|None=None,duration:int=30) -> dict:
    title=clean(topic,145)
    if not title or len(title)<3 or len(topic)>500:raise ValueError('Enter a topic between 3 and 500 characters')
    if not isinstance(duration,int) or not 12<=duration<=90:raise ValueError('Duration must be between 12 and 90 seconds')
    if article is not None:
        from editorial import compose_news_story
        return compose_news_story(title, article, duration)
    if article:
        if not all(article.get(k) for k in ('url','source','published')):raise ValueError('News item needs a source and publication date')
        sentences=_phrases(article.get('summary',''))
        captions=[
            f"Today’s headline: {title}.",
            ("According to "+article['source']+", "+sentences[0]) if sentences else f"This development was reported by {article['source']}.",
            sentences[1] if len(sentences)>1 else "This is an emerging story. Details can change as reporting continues.",
            sentences[2] if len(sentences)>2 else "The source article provides the context for this development.",
            "This short video summarizes the available reporting, not unverified predictions.",
            f"Reported on {article['published'][:10]} by {article['source']}. Check the original article for updates.",
        ]
    else:
        captions=[
            f"Let's explore the question: {title}.",
            "We start by identifying the key ideas and the processes involved.",
            "Follow how these parts change over time and influence one another.",
            "Notice the patterns, the connections, and the causes behind the outcome.",
            "Reliable evidence matters. We should not invent facts or numbers.",
            "Use the original source to explore the topic in more depth.",
        ]
    heads=[title,'WHAT WE KNOW','HOW IT WORKS','THE CONNECTIONS',
           'WHY IT MATTERS','THE BIGGER PICTURE']
    lengths=[.16,.20,.19,.18,.16,.11]
    bounds=[0.]
    for v in lengths[:-1]:bounds.append(round(bounds[-1]+duration*v,3))
    bounds.append(float(duration))
    scenes=[dict(start=bounds[i],end=bounds[i+1],headline=heads[i],
                 caption=clean(captions[i],175),visual=VISUALS[i],
                 metric=article['source'] if article else 'ANIMATED EXPLAINER',
                 narration=captions[i]) for i in range(6)]
    cfg=dict(mode='universal',language='en',topic=title,duration=duration,scenes=scenes,
             evidence='rss' if article else 'unsourced',
             sources=[{k:article[k] for k in ('title','source','published','url')}] if article else [])
    validate_universal(cfg)
    return cfg

def wikipedia_context(topic:str,fetcher=None) -> dict|None:
    query=urlencode(dict(action='query',generator='search',gsrsearch=topic[:150],
                         gsrlimit=1,prop='extracts',exintro=1,explaintext=1,
                         exsectionformat='plain',format='json'))
    url='https://en.wikipedia.org/w/api.php?'+query
    if fetcher is None:
        def fetcher(address):
            with urlopen(Request(address,headers={'User-Agent':'VerticalScienceStudio/1.0 (educational video)'}),timeout=6) as r:
                return r.read(100_000)
    try:
        pages=json.loads(fetcher(url)).get('query',{}).get('pages',{})
        if not pages:return None
        page=next(iter(pages.values()))
        summary=clean(page.get('extract',''),700)
        if len(summary)<60 or not isinstance(page.get('pageid'),int):return None
        return dict(title=page['title'],summary=summary,source='Wikipedia',
                    url='https://en.wikipedia.org/?curid='+str(page['pageid']))
    except (OSError,TimeoutError,ValueError,KeyError,TypeError):return None

def research_story(topic:str,duration:int=30,*,fetcher=None) -> dict:
    require_english_topic(topic)
    cfg=create_story(topic,duration=duration)
    # A user's detailed briefing is an equally valid input for any subject.
    # Extract its own sentences rather than filling the video with generic slogans.
    brief=_phrases(topic)
    if len(topic)>145 and len(brief)>=2:
        cfg['topic']=clean(brief[0],145)
        cfg['scenes'][0]['headline']=cfg['topic']
        for i,phrase in enumerate(brief[:5],start=1):
            cfg['scenes'][i]['caption']=phrase[:175]
            cfg['scenes'][i]['metric']='USER-PROVIDED BRIEF'
            cfg['scenes'][i]['narration']=phrase[:175]
        cfg['evidence']='user_provided'
    if cfg['evidence'] != 'user_provided':
        from editorial import apply_explainer
        if apply_explainer(cfg, topic):
            return cfg
    source=wikipedia_context(topic,fetcher)
    if source and cfg['evidence']!='user_provided':
        phrases=_phrases(source['summary'])
        for i in range(1,min(6,len(phrases)+1)):
            cfg['scenes'][i]['caption']=phrases[i-1][:175]
            cfg['scenes'][i]['metric']='SOURCE: WIKIPEDIA'
            cfg['scenes'][i]['narration']=phrases[i-1][:175]
        cfg['sources']=[{k:source[k] for k in ('title','source','url')}]
        cfg['evidence']='wikipedia'
    return cfg
