from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib
import json
import zipfile
ROOT=Path(__file__).resolve().parents[1]
class Links(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.lang=None;self.ids=set();self.rings=[];self.arcs=[];self.track_geometry=[];self.progress_geometry=[];self.graphic=None;self.svg_index=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if 'cycle-ring' in a.get('class','').split():self.rings.append(a.get('aria-label'))
  if tag=='svg':
   self.svg_index+=1;self.graphic=(self.svg_index,a.get('class'))
  if tag=='circle':
   geometry=(self.graphic,tuple(a.get(k) for k in ('cx','cy','r','stroke-width')))
   if 'cycle-track' in a.get('class','').split():self.track_geometry.append(geometry)
   if 'cycle-progress' in a.get('class','').split():self.progress_geometry.append(geometry)
  if tag=='circle' and a.get('pathlength')=='100':self.arcs.append(a.get('stroke-dasharray'))
  if 'id' in a:self.ids.add(a['id'])
  for key in ('href','src'):
   if key in a:self.links.append(a[key])
 def handle_endtag(self,tag):
  if tag=='svg':self.graphic=None
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
# Both library and reader downloads must preserve each catalog source exactly.
for document in json.loads((ROOT/'canonical/documents.json').read_text()):
 source=(ROOT/document['path']).read_bytes()
 for site in document['sites']:
  assert (ROOT/'apps'/site/'dist/documents'/(document['key']+'.md')).read_bytes()==source,document['path']
 reader=ROOT/'apps'/document['primary_site']/'dist/documents'/Path(document['path']).name
 assert reader.read_bytes()==source,(document['path'],'Reader download differs from source; check filename collisions')
# Published downloadable review archives must match their source bytes and SHA-256 sidecars.
for filename in (
 'FINITE_LINEAGE_CYCLE03_REVIEW_BUNDLE_2026-10-16.zip',
 'FINITE_LINEAGE_CYCLE03_REVIEW_RESPONSE_2026-10-18.zip',
 'FINITE_LINEAGE_SUPPLEMENTAL_REVIEW_BUNDLE_2026-10-21.zip',
):
 source=ROOT/'research/preparation'/filename
 digest=hashlib.sha256(source.read_bytes()).hexdigest()
 sidecar=source.with_suffix(source.suffix+'.sha256').read_text().split()[0]
 assert digest==sidecar,(filename,'Source sidecar mismatch')
 with zipfile.ZipFile(source) as archive: assert archive.testzip() is None,(filename,'Corrupt ZIP')
 for site in ('org','net'):
  public=ROOT/'apps'/site/'dist/downloads'/filename
  public_sidecar=public.with_suffix(public.suffix+'.sha256')
  assert public.read_bytes()==source.read_bytes(),(site,filename,'Published archive differs from source')
  assert public_sidecar.read_text().split()[0]==digest,(site,filename,'Published sidecar differs')
state=[json.loads((ROOT/'apps'/s/'dist/research-state.json').read_text()) for s in ('org','net')]
assert state[0]==state[1],'Site state diverged'
publication=json.loads((ROOT/'canonical/site-state.json').read_text())
manifest=json.loads((ROOT/publication['active_cycle_ref']).read_text())
expected=sum(o['weight'] for o in manifest['obligations'] if o['resolved'])/sum(o['weight'] for o in manifest['obligations'])
assert state[0]['completion']==expected and state[0]['cycle']['status']==manifest['status']
assert state[0]['cycle']['number']==f"{manifest['cycle_number']:02d}",'Current Cycle selector diverged'
# Check each archive and the current home rings from their own manifest.
for manifest_path in sorted((ROOT/'cycles').glob('cycle-*/manifest.json')):
 m=json.loads(manifest_path.read_text());number=f"{m['cycle_number']:02d}"
 fraction=sum(o['weight'] for o in m['obligations'] if o['resolved'])/sum(o['weight'] for o in m['obligations'])
 count=sum(o['resolved'] for o in m['obligations']);total=len(m['obligations'])
 archived=state[0]['cycles'][number]
 assert archived['completion']==fraction and archived['cycle']['status']==m['status']
 assert archived['cycle']['number']==number and archived['resolved_obligations']==count
 label=f"Cycle {number}: {m['status']}, {count} / {total} obligations resolved ({fraction*100:.1f}%)."
 targets=[('net',f'cycle/{number}/index.html')]
 if m['cycle_number']==manifest['cycle_number']:targets.extend([('org','index.html'),('net','index.html')])
 for site,path in targets:
  parser=Links();parser.feed((ROOT/'apps'/site/'dist'/path).read_text())
  assert parser.rings==[label],(site,path,'Accessible ring disagrees with selected manifest')
  assert parser.arcs==[f'{fraction*100} 100'],(site,path,'Rendered ring disagrees with selected manifest')
  assert len(parser.track_geometry)==len(parser.progress_geometry)==1,(site,path,'Ring layers missing')
  assert parser.track_geometry==parser.progress_geometry,(site,path,'Track and progress geometry differ')
  assert parser.track_geometry[0][0][1]=='cycle-graphic',(site,path,'Ring layers must share an SVG')
 cycle_html=(ROOT/f'apps/net/dist/cycle/{number}/index.html').read_text()
 assert f'{count} resolved · {total-count} open obligations' in cycle_html
 assert cycle_html.count('Open · no resolution on record')==total-count,'Obligation list has stale open labels'
 for obligation in m['obligations']:
  if obligation['resolved']:
   for ref in obligation['evidence_refs']:
    assert 'https://github.com/omasim/Autorite/blob/main/'+ref in cycle_html,'Resolved obligation evidence missing'
# A newly opened Cycle must not erase the published predecessor's full ring.
assert state[0]['cycles']['01']['completion']==1 and state[0]['cycles']['01']['cycle']['status']=='PUBLISHED'
print(f'PASS: {pages} English pages; {checks} asset, source and page links; shared current Cycle and separate archived rings.')
