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
    ('France 24','https://www.france24.com/fr/rss'),
    ('franceinfo','https://www.francetvinfo.fr/titres.rss'),
    ('Le Monde','https://www.lemonde.fr/rss/une.xml'),
    ('The Guardian','https://www.theguardian.com/world/rss'),
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
    if not items:raise RuntimeError('Aucune actualité récente vérifiable : flux indisponibles ou obsolètes')
    french=[item for item in items if item['source'] in ('France 24','franceinfo','Le Monde')]
    candidates=(french if french else items)[:15]
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

def create_story(topic:str, *,article:dict|None=None,duration:int=30) -> dict:
    title=clean(topic,145)
    if not title or len(title)<3 or len(topic)>500:raise ValueError('Le sujet doit contenir entre 3 et 500 caractères')
    if not isinstance(duration,int) or not 12<=duration<=90:raise ValueError('Durée autorisée : 12 à 90 secondes')
    if article:
        if not all(article.get(k) for k in ('url','source','published')):raise ValueError('Actualité sans source ou date')
        sentences=_phrases(article.get('summary',''))
        captions=[
            f'À la une : {title}',
            sentences[0] if sentences else f"Actualité publiée par {article['source']}.",
            sentences[1] if len(sentences)>1 else f"Source : {article['source']}.",
            sentences[2] if len(sentences)>2 else 'Retrouvez les informations détaillées dans la source.',
            'Cette synthèse présente les éléments publiés, sans prédire leurs conséquences.',
            f"Publication : {article['published'][:10]}. Source : {article['source']}.",
        ]
    else:
        captions=[
            f'Explorons cette question : {title}',
            'D’abord, identifions les éléments essentiels du sujet.',
            'Observons la chronologie et les liens entre les événements.',
            'Comparons les différents facteurs et leurs interactions.',
            'Les réponses précises nécessitent des sources fiables.',
            'Un point de départ pour approfondir le sujet.',
        ]
    heads=[title,'LES FAITS ESSENTIELS','LE CONTEXTE','LES LIENS',
           'CE QU’IL FAUT RETENIR','POUR ALLER PLUS LOIN']
    lengths=[.16,.20,.19,.18,.16,.11]
    bounds=[0.]
    for v in lengths[:-1]:bounds.append(round(bounds[-1]+duration*v,3))
    bounds.append(float(duration))
    scenes=[dict(start=bounds[i],end=bounds[i+1],headline=heads[i],
                 caption=clean(captions[i],175),visual=VISUALS[i],
                 metric=article['source'] if article else 'EXPLICATION VISUELLE') for i in range(6)]
    cfg=dict(mode='universal',topic=title,duration=duration,scenes=scenes,
             evidence='rss' if article else 'unsourced',
             sources=[{k:article[k] for k in ('title','source','published','url')}] if article else [])
    validate_universal(cfg)
    return cfg

def wikipedia_context(topic:str,fetcher=None) -> dict|None:
    query=urlencode(dict(action='query',generator='search',gsrsearch=topic[:150],
                         gsrlimit=1,prop='extracts',exintro=1,explaintext=1,
                         exsectionformat='plain',format='json'))
    url='https://fr.wikipedia.org/w/api.php?'+query
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
        return dict(title=page['title'],summary=summary,source='Wikipédia',
                    url='https://fr.wikipedia.org/?curid='+str(page['pageid']))
    except (OSError,TimeoutError,ValueError,KeyError,TypeError):return None

def research_story(topic:str,duration:int=30,*,fetcher=None) -> dict:
    cfg=create_story(topic,duration=duration)
    # A user's detailed briefing is an equally valid input for any subject.
    # Extract its own sentences rather than filling the video with generic slogans.
    brief=_phrases(topic)
    if len(topic)>145 and len(brief)>=2:
        cfg['topic']=clean(brief[0],145)
        cfg['scenes'][0]['headline']=cfg['topic']
        for i,phrase in enumerate(brief[:5],start=1):
            cfg['scenes'][i]['caption']=phrase[:175]
            cfg['scenes'][i]['metric']='BRIEF FOURNI PAR L’UTILISATEUR'
        cfg['evidence']='user_provided'
    source=wikipedia_context(topic,fetcher)
    if source and cfg['evidence']!='user_provided':
        phrases=_phrases(source['summary'])
        for i in range(1,min(6,len(phrases)+1)):
            cfg['scenes'][i]['caption']=phrases[i-1][:175]
            cfg['scenes'][i]['metric']='SOURCE : WIKIPÉDIA'
        cfg['sources']=[{k:source[k] for k in ('title','source','url')}]
        cfg['evidence']='wikipedia'
    return cfg
