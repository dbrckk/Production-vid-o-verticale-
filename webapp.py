#!/usr/bin/env python3
"""Simple self-hosted mobile generator. Require STUDIO_TOKEN when exposed remotely."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Lock,Thread
from urllib.parse import urlsplit
import hmac,json,os,secrets
from generate_topic import build
from studio import render
from narration import make_narration
from qa_video import inspect as inspect_video_quality
from topic_engine import random_important_news,create_story,current_headlines

ROOT=Path(__file__).resolve().parent
HTML=ROOT/'web'/'index.html'

class State:
    def __init__(self,directory:Path):
        self.directory=Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True)
        self.jobs={}
        self.lock=Lock()
        self.busy=False
    def prune(self,max_outputs:int=5):
        with self.lock:
            finished=[key for key,value in self.jobs.items() if value['status'] in ('ready','error')]
            expired=finished[:-max_outputs]
            for key in expired:self.jobs.pop(key,None)
        for key in expired:
            for suffix in ('.mp4','.json','.sound.wav','.voice.wav'):
                (self.directory/f'{key}{suffix}').unlink(missing_ok=True)
        # cover.png is shared with the legacy renderer and may be in use.

    def start(self,topic:str,article:dict|None,quality:str,voice:str='en-US-BrianMultilingualNeural'):
        if voice not in ('en-US-AndrewNeural','en-US-BrianMultilingualNeural','en-US-EmmaMultilingualNeural','en-US-AriaNeural','en-GB-RyanNeural'):
            raise ValueError('Unsupported English narrator')
        if quality not in ('preview','720p','1080p','1080p60'):raise ValueError('Unknown video quality')
        cfg=create_story(topic,article=article) if article else build(topic,False,30)
        with self.lock:
            if self.busy:raise RuntimeError('Another video is rendering')
            self.busy=True
            job=secrets.token_hex(12)
            self.jobs[job]={'id':job,'status':'queued','topic':cfg['topic'],'sources':cfg['sources']}
        def worker():
            with self.lock:self.jobs[job]['status']='rendering'
            try:
                width,fps={'preview':(540,15),'720p':(720,24),'1080p':(1080,30),'1080p60':(1080,60)}[quality]
                with self.lock:self.jobs[job]['status']='narrating'
                voice_file=self.directory/f'{job}.voice.wav'
                voice_info=make_narration(cfg,voice_file,provider='edge',voice=voice)
                with self.lock:self.jobs[job]['status']='rendering'
                result=render(cfg,self.directory/f'{job}.mp4',width,fps,preview=quality=='preview',voice=voice_file)
                with self.lock:self.jobs[job]['status']='quality_check'
                qa=inspect_video_quality(Path(result['output']),Path(result['output']).with_suffix('.json'))
                with self.lock:self.jobs[job].update(status='ready',info=result,voice=voice_info,quality=qa)
            except Exception as error:
                with self.lock:self.jobs[job].update(status='error',error=str(error)[:200])
            finally:
                with self.lock:self.busy=False
                self.prune()
        Thread(target=worker,daemon=True).start()
        return self.jobs[job].copy()

class Handler(BaseHTTPRequestHandler):
    server_version='VerticalScienceStudio/1.0'
    def _auth(self):
        token=self.server.token
        return not token or hmac.compare_digest(self.headers.get('X-Studio-Token',''),token)
    def send_json(self,status:int,payload:dict):
        data=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        route=urlsplit(self.path).path
        if route=='/':
            data=HTML.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(data);return
        if not self._auth():return self.send_json(401,{'error':'Access key required'})
        if route=='/api/random':
            try:return self.send_json(200,{'article':random_important_news()})
            except RuntimeError as e:return self.send_json(503,{'error':str(e)})
        parts=route.split('/')
        if len(parts)==4 and parts[:2]==['','api'] and parts[2] in ('status','video'):
            job=parts[3]
            if len(job)!=24 or not all(c in '0123456789abcdef' for c in job):
                return self.send_json(404,{'error':'Identifiant inconnu'})
            with self.server.state.lock:state=self.server.state.jobs.get(job)
            if not state:return self.send_json(404,{'error':'Video not found'})
            if parts[2]=='status':return self.send_json(200,state)
            if state['status']!='ready':return self.send_json(409,{'error':'Video is still rendering'})
            video=self.server.state.directory/f'{job}.mp4'
            if not video.is_file():return self.send_json(404,{'error':'MP4 not found'})
            self.send_response(200)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Content-Disposition',f'attachment; filename="vertical-{job}.mp4"')
            self.send_header('Content-Length',str(video.stat().st_size))
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            with video.open('rb') as stream:
                while chunk:=stream.read(1<<18):self.wfile.write(chunk)
            return
        self.send_json(404,{'error':'Unknown route'})
    def do_POST(self):
        if not self._auth():return self.send_json(401,{'error':'Access key required'})
        if urlsplit(self.path).path!='/api/render':return self.send_json(404,{'error':'Unknown route'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4096:raise ValueError('Invalid request')
            body=json.loads(self.rfile.read(length))
            topic=body.get('topic','')
            if not isinstance(topic,str) or not 3<=len(topic)<=500:raise ValueError('Invalid topic')
            article=body.get('article')
            if article is not None:
                if not isinstance(article,dict) or not isinstance(article.get('url'),str):
                    raise ValueError('Invalid article')
                matches=[x for x in self.server.news_provider() if x['url']==article['url']]
                if not matches:raise ValueError('Article is unverified or too old')
                article=matches[0]
                if topic!=article['title']:raise ValueError('Topic does not match the source article')
            result=self.server.state.start(topic,article,body.get('quality','preview'),body.get('voice','en-US-BrianMultilingualNeural'))
            self.send_json(202,result)
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:self.send_json(400,{'error':str(e)})
        except RuntimeError as e:self.send_json(409,{'error':str(e)})

def serve(host='127.0.0.1',port=8765,output_dir=None):
    token=os.environ.get('STUDIO_TOKEN','')
    if host not in ('127.0.0.1','localhost','::1') and len(token)<16:
        raise RuntimeError('STUDIO_TOKEN (16 caractères minimum) obligatoire hors localhost')
    server=ThreadingHTTPServer((host,port),Handler)
    server.state=State(Path(output_dir or ROOT/'output'))
    server.token=token
    server.news_provider=current_headlines
    print(f'Studio prêt : http://{host}:{port}',flush=True)
    server.serve_forever()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=int(os.environ.get('PORT','8765')))
    args=p.parse_args()
    serve(args.host,args.port)
