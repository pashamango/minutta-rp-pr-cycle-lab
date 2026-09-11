#!/usr/bin/env python3
import json,re,sys,urllib.parse,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).parent; MANIFEST=ROOT/'corpus.json'
FAMILIES={'idempotency':'duplicate execution idempotency bug','null-lookup':'unchecked null lookup bug','authorization':'authorization guard missing bug','stale-state':'stale cache state mismatch bug','serialization':'serialization schema mismatch bug','concurrency':'race condition ordering bug','path-config':'path configuration mismatch bug'}
STOP=set('the and for with from that this issue when into have has was are not but can will to of in on a an is it be as by or'.split())
HIGH=re.compile(r'(?:/[A-Za-z0-9_.-]+)+|\b[A-Z][A-Za-z0-9_]{2,}\b|\b\d+(?:\.\d+)?\b|`[^`]+`|https?://\S+')
def get(u):
 out=subprocess.check_output(['curl','--fail','--silent','--show-error','--location','-H','Accept: application/vnd.github+json','-A','public-study',u],timeout=30)
 return json.loads(out)
def tok(s): return [x for x in re.findall(r'[a-z]{3,}',s.lower()) if x not in STOP]
def sig(s):
 keep={'error','exception','fail','failed','failure','missing','duplicate','race','stale','schema','null','permission','cache','path','config','ordering','state','retry','serialize','authorization','lookup'}
 return ' '.join(x for x in tok(HIGH.sub('<RESIDUAL>',s)) if x in keep)
def vec(s):
 d={}
 for x in tok(s): d[x]=d.get(x,0)+1
 return d
def sim(a,b):
 a,b=vec(a),vec(b); return sum(x*b.get(k,0) for k,x in a.items())/(sum(x*x for x in a.values())**.5*sum(x*x for x in b.values())**.5 or 1)
def score(xs,f):
 a1=a3=0; bad=[]
 for i,x in enumerate(xs):
  rr=sorted(((sim(x[f],y[f]),j) for j,y in enumerate(xs) if i!=j),reverse=True); fam=x['family']
  a1+=xs[rr[0][1]]['family']==fam; a3+=any(xs[j]['family']==fam for _,j in rr[:3])
  if xs[rr[0][1]]['family']!=fam and len(bad)<8: bad.append([x['id'],fam,xs[rr[0][1]]['id'],xs[rr[0][1]]['family']])
 return a1/len(xs),a3/len(xs),bad
def main():
 if '--collect' in sys.argv:
  rows=[]
  for fam,q in FAMILIES.items():
   u='https://api.github.com/search/issues?'+urllib.parse.urlencode({'q':q+' is:issue is:public','sort':'relevance','per_page':5})
   for x in get(u)['items'][:5]:
    text=x['title']+'\n'+(x.get('body') or ''); rows.append({'id':x['html_url'],'repo':x['repository_url'].rsplit('/',1)[-1],'family':fam,'title':x['title'],'text':text,'signature':sig(text)})
  MANIFEST.write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
 xs=json.loads(MANIFEST.read_text())
 for x in xs: x['sr']=x['signature']+' '+HIGH.sub('',x['text'])
 out={f:score(xs,f) for f in ('text','signature','sr')}
 print(json.dumps({'n':len(xs),'metrics':{f:{'top1':v[0],'top3':v[1]} for f,v in out.items()},'confusions':{f:v[2] for f,v in out.items()}},indent=2))
if __name__=='__main__': main()
