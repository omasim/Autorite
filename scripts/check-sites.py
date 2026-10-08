from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.lang=None;self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if 'id' in a:self.ids.add(a['id'])
  for key in ('href','src'):
   if key in a:self.links.append(a[key])
origins=json.loads((ROOT/'canonical/site-origins.json').read_text())
checks=0
pages=0
for site in ('org','net'):
 dist=ROOT/'apps'/site/'dist'
 for p in dist.rglob('*.html'):
  pages+=1
  text=p.read_text();parser=Links();parser.feed(text)
  assert parser.lang=='en',p
  assert not any(c in text for c in 'çğıöşüÇĞİÖŞÜ'),p
  assert '<title>' in text and 'name="description"' in text,p
  for link in parser.links:
   u=urlsplit(link)
   if u.scheme=='data':continue
   target_site=site
   if u.netloc:
    matches=[k for k,v in origins.items() if urlsplit(v).netloc==u.netloc]
    if not matches:continue
    target_site=matches[0]
   target_root=ROOT/'apps'/target_site/'dist'
   path=unquote(u.path)
   q=target_root/path.lstrip('/') if path.startswith('/') or u.netloc else p.parent/path
   if not path:q=p
   if q.is_dir():q=q/'index.html'
   assert q.exists(),(p,link,q)
   if u.fragment and q.suffix=='.html':
    dest=Links();dest.feed(q.read_text());assert u.fragment in dest.ids,(p,link)
   checks+=1
state=[json.loads((ROOT/'apps'/s/'dist/research-state.json').read_text()) for s in ('org','net')]
assert state[0]==state[1],'Site state diverged'
assert state[0]['completion']==0 and state[0]['cycle']['status']=='PLANNED'
print(f'PASS: {pages} English pages; {checks} asset, source and page links; identical canonical Cycle state.')
