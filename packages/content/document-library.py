"""Static document library, generated from unchanged source Markdown."""
import html, re, hashlib, math
from pathlib import Path
from markdown_it import MarkdownIt

md=MarkdownIt('commonmark', {'html':False}).enable('table')

def render_document(source):
 tokens=md.parse(source);toc=[];seen={}
 for i,t in enumerate(tokens):
  if t.type=='heading_open':
   label=tokens[i+1].content
   key=re.sub(r'[^a-z0-9]+','-',label.lower()).strip('-') or 'section'
   seen[key]=seen.get(key,0)+1
   anchor=key if seen[key]==1 else f'{key}-{seen[key]}'
   t.attrSet('id',anchor)
   if t.tag in ('h2','h3'):toc.append((anchor,label,t.tag))
 rendered=md.renderer.render(tokens,md.options,{})
 # Tables stay readable on phones without making the document itself scroll sideways.
 rendered=rendered.replace('<table>','<div class="document-table"><table>').replace('</table>','</table></div>')
 return rendered,toc

def build_library(root,site,catalog,page,href):
 esc=html.escape
 records=[d for d in catalog if site in d['sites']]
 categories=list(dict.fromkeys(d['category'] for d in records))
 groups=[]
 for category in categories:
  items=[]
  for d in records:
   if d['category']!=category:continue
   source=(root/d['path']).read_text();filename=Path(d['path']).name
   target=('/sources/'+d['key']+'/') if d['primary_site']==site else href(d['primary_site'],'/sources/'+d['key']+'/')
   download='/documents/'+d['key']+'.md'
   download_path=root/'apps'/site/'dist/documents'/(d['key']+'.md')
   download_path.parent.mkdir(parents=True,exist_ok=True)
   download_path.write_bytes((root/d['path']).read_bytes())
   attrs=f'data-category="{esc(category)}" data-search="{esc((d["title"]+" "+d["summary"]+" "+source).lower(),quote=True)}"'
   items.append(f'<article class="document-card" {attrs}><div class="document-meta">{esc(d["label"])} · {max(1,math.ceil(len(source.split())/220))} min read</div><h3><a href="{target}">{esc(d["title"])}</a></h3><p>{esc(d["summary"])}</p><div class="document-actions"><a href="{target}">Read document</a><a href="{download}" download="{filename}">Download .md</a></div></article>')
  groups.append(f'<section class="document-group" data-group="{esc(category)}"><h2>{esc(category)}</h2><div class="document-cards">'+''.join(items)+'</div></section>')
 options='<option value="">All categories</option>'+''.join(f'<option>{esc(c)}</option>' for c in categories)
 suggested=[d for d in records if d['recommended']]
 starts=''.join(f'<a href="{("/sources/"+d["key"]+"/" if d["primary_site"]==site else href(d["primary_site"],"/sources/"+d["key"]+"/"))}">{esc(d["title"])}</a>' for d in suggested)
 body=f'<div class="library-header"><div class="eyebrow">Document library</div><h1>{"Research foundations" if site=="org" else "Research working documents"}</h1><p class="lead">{"Read the questions, principles and source framework behind Autorite." if site=="org" else "Find protocols, Cycle commitments and the rules for recording research."}</p><p class="library-note">The frozen baseline is preserved. Protocols and reports state their own dates, execution status and evidence limits.</p></div><div class="library-start"><strong>Start here</strong>{starts}</div><form class="library-toolbar" role="search" onsubmit="return false"><div><label for="document-search">Search documents</label><input id="document-search" type="search" placeholder="Search titles, summaries and document text" autocomplete="off"></div><div><label for="document-category">Category</label><select id="document-category">{options}</select></div><button type="reset">Clear filters</button></form><p class="document-count" role="status" aria-live="polite">{len(records)} documents</p><div class="document-empty" hidden>No matching documents. Try another term or clear the filters.</div>'+''.join(groups)+'<script src="/document-library.js" defer></script>'
 page(site,'/sources/','Document library',body)
 for d in catalog:
  if d['primary_site']!=site:continue
  source_path=root/d['path'];source=source_path.read_text();filename=source_path.name
  dest=root/'apps'/site/'dist/documents'/filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source_path.read_bytes())
  content,toc=render_document(source)
  toc_html=''.join(f'<li class="{tag}"><a href="#{anchor}">{esc(label)}</a></li>' for anchor,label,tag in toc)
  sidebar=f'<aside class="document-toc" aria-label="Contents"><h2>On this page</h2><ul>{toc_html}</ul></aside>' if toc else ''
  digest=hashlib.sha256(source_path.read_bytes()).hexdigest()
  body=f'<div class="document-breadcrumb"><a href="/sources/">Document library</a> / {esc(d["category"])}</div><div class="document-reader-meta"><span>{esc(d["label"])}</span><span>{max(1,math.ceil(len(source.split())/220))} min read</span><a href="/documents/{filename}" download="{filename}">Download original .md</a><button type="button" onclick="window.print()">Print / Save PDF</button></div><p class="document-summary">{esc(d["summary"])}</p><div class="document-reader">{sidebar}<article class="document-content">{content}<details class="document-provenance"><summary>Source record</summary><p>Repository path: <code>{esc(d["path"])}</code></p><p>SHA-256: <code>{digest}</code></p><p>This reading view is generated from the source. The downloaded Markdown preserves the original bytes.</p></details></article></div>'
  page(site,'/sources/'+d['key']+'/',d['title'],body)
