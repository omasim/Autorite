from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.lang=None;self.ids=set();self.rings=[];self.arcs=[];self.track_geometry=[];self.progress_geometry=[];self.graphic=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if 'cycle-ring' in a.get('class','').split():self.rings.append(a.get('aria-label'))
  if tag=='svg':self.graphic=a.get('class')
  if tag=='circle':
   geometry=(self.graphic,tuple(a.get(k) for k in ('cx','cy','r','stroke-width')))
   if 'cycle-track' in a.get('class','').split():self.track_geometry.append(geometry)
   if 'cycle-progress' in a.get('class','').split():self.progress_geometry.append(geometry)
  if tag=='circle' and a.get('pathlength')=='100':self.arcs.append(a.get('stroke-dasharray'))
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
manifest=json.loads((ROOT/'cycles/cycle-01/manifest.json').read_text())
expected=sum(o['weight'] for o in manifest['obligations'] if o['resolved'])/sum(o['weight'] for o in manifest['obligations'])
assert state[0]['completion']==expected and state[0]['cycle']['status']==manifest['status']
# Check the published visual/accessible ring, not only its JSON source.
count=sum(o['resolved'] for o in manifest['obligations']);total=len(manifest['obligations'])
label=f"Cycle {manifest['cycle_number']:02d}: {manifest['status']}, {count} / {total} obligations resolved ({expected*100:.1f}%)."
for site,path in [('org','index.html'),('net','index.html'),('net','cycle/01/index.html')]:
 parser=Links();parser.feed((ROOT/'apps'/site/'dist'/path).read_text())
 assert parser.rings==[label],(site,path,'Accessible ring disagrees with manifest')
 assert parser.arcs==[f'{expected*100} 100'],(site,path,'Rendered ring disagrees with manifest')
 assert len(parser.track_geometry)==len(parser.progress_geometry)==1,(site,path,'Ring layers missing')
 assert parser.track_geometry==parser.progress_geometry,(site,path,'Track and progress geometry differ')
 assert parser.track_geometry[0][0]=='cycle-graphic',(site,path,'Ring layers must share an SVG')
cycle_html=(ROOT/'apps/net/dist/cycle/01/index.html').read_text()
assert f'{count} resolved · {total-count} open obligations' in cycle_html
assert cycle_html.count('Open · no resolution on record')==total-count,'Obligation list has stale open labels'
for obligation in manifest['obligations']:
 if obligation['resolved']:
  for ref in obligation['evidence_refs']:
   assert 'https://github.com/omasim/Autorite/blob/main/'+ref in cycle_html,'Resolved obligation evidence is missing'
print(f'PASS: {pages} English pages; {checks} asset, source and page links; identical canonical Cycle state.')
