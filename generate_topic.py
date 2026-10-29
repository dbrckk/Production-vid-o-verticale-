#!/usr/bin/env python3
"""Generate universal short-video configs from user topics or fresh verified RSS."""
import argparse
import json
from pathlib import Path
from topic_engine import create_story,random_important_news,research_story,current_headlines

def build(topic: str | None,random_news:bool,duration:int,article_url:str|None=None) -> dict:
    if random_news:
        item=random_important_news()
        return create_story(item['title'],article=item,duration=duration)
    if article_url:
        if not article_url.startswith('https://') or len(article_url)>2000:
            raise ValueError('Invalid article URL')
        candidates=current_headlines()
        item=next((a for a in candidates if a['url']==article_url),None)
        if item is None:
            raise ValueError('Article not present in fresh, verified RSS results (up to 72 hours)')
        return create_story(item['title'],article=item,duration=duration)
    if not topic:raise ValueError('Specify --topic or --random-news')
    return research_story(topic,duration=duration)

def main():
    p=argparse.ArgumentParser(description='Prepare a source-backed short-video storyboard')
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--topic',type=str)
    group.add_argument('--random-news',action='store_true')
    group.add_argument('--article-url',type=str,help='Select an exact currently sourced RSS news article')
    p.add_argument('--duration',type=int,default=30)
    p.add_argument('--output',type=Path,default=Path('output/topic.json'))
    a=p.parse_args()
    cfg=build(a.topic,a.random_news,a.duration,article_url=a.article_url)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(topic=cfg['topic'],evidence=cfg['evidence'],sources=cfg['sources'],
                          scenes=len(cfg['scenes']),path=str(a.output)),ensure_ascii=False))

if __name__=='__main__':main()
