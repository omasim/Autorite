"""Validate stored research structure, never scientific truth or approval."""
from pathlib import Path
from datetime import date
import hashlib, json, re, subprocess
import yaml

COMMON = {'schema_version','id','type','title','created_at','updated_at','source_refs','relations'}
FIELDS = {
 'Question': ('Q', {'question','scope'}, {'OPEN','ACTIVE','PARTIALLY_RESOLVED','RESOLVED','REFORMULATED'}),
 'Claim': ('C', {'claim_kind','statement','scope','assumption_refs','does_not_imply','limitations','change_conditions'}, set()),
 'Assumption': ('A', {'statement','scope'}, None),
 'ResearchPackage': ('RP', {'question_refs','scope','protocol_ref','cycle_ref'}, {'PLANNED','ACTIVE','BLOCKED','CLOSED'}),
 'Test': ('TST', {'package_ref','protocol_ref','target_refs'}, None),
 'Result': ('R', {'test_ref','package_ref','run_ref','artifact_refs','observations'}, {'VALID','INVALIDATED'}),
 'Decision': ('D', {'decision','rationale','affected_refs'}, {'ACTIVE','SUPERSEDED','REOPENED'}),
 'Source': ('SRC', {'citation'}, None),
}
OPTIONAL = {'Claim': {'proof_artifact_refs'}, 'Result': {'invalidation_reason','invalidation_decision_ref'}, 'Source': {'url','repository_path'}}
ARRAYS = {'aliases','source_refs','relations','question_refs','assumption_refs','target_refs','artifact_refs','affected_refs','proof_artifact_refs'}
CYCLE_FIELDS = {'schema_version','cycle_number','title','status','package_refs','obligations','close_decision_ref','snapshot_ref','publication_refs'}

class Invalid(ValueError): pass

def require(ok, message):
 if not ok: raise Invalid(message)

def read_record(path):
 text = path.read_text()
 parts = text.split('---', 2)
 require(len(parts)==3 and not parts[0].strip(), f'{path}: missing frontmatter')
 # Reject duplicate YAML keys rather than silently retaining the last value.
 class Unique(yaml.SafeLoader): pass
 def mapping(loader,node):
  result={}
  for key,value in node.value:
   k=loader.construct_object(key)
   require(k not in result, f'{path}: duplicate key {k}')
   result[k]=loader.construct_object(value)
  return result
 Unique.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
 data=yaml.load(parts[1], Loader=Unique)
 require(isinstance(data,dict) and parts[2].strip(), f'{path}: empty record')
 return data,parts[2].strip()

def validate(root):
 root=Path(root).resolve();records={};bodies={};aliases=set();cycles={}
 def file_ref(ref, directory=False):
  require(isinstance(ref,str) and ref.strip(), 'Empty file reference')
  raw=ref.split('#',1)[0];p=(root/raw).resolve()
  require(not Path(raw).is_absolute() and p.is_relative_to(root), f'Unsafe path: {ref}')
  require(p.is_dir() if directory else p.is_file(), f'Missing path: {ref}')
  return p
 paths=list((root/'graph').rglob('*.md'))+list((root/'research').rglob('RECORD.md'))
 for p in paths:
  d,body=read_record(p);t=d.get('type');require(t in FIELDS,f'{p}: unknown type')
  prefix,extra,statuses=FIELDS[t];allowed=COMMON|extra|{'aliases'}|OPTIONAL.get(t,set())
  if statuses is not None:allowed.add('status')
  require(COMMON|extra <= d.keys() and d.keys() <= allowed,f'{p}: missing/unknown fields')
  require(d['schema_version']=='0.1', f'{p}: schema version')
  require(isinstance(d['id'],str) and re.fullmatch(prefix+r'-[A-Z0-9]+',d['id']),f'{p}: ID')
  require(d['id'] not in records,f'Duplicate ID: {d["id"]}')
  for key,value in d.items():
   if key in ARRAYS:require(isinstance(value,list),f'{p}: {key} must be an array')
   elif key not in ('created_at','updated_at'):require(isinstance(value,str) and value.strip(),f'{p}: {key} must be a nonempty string')
  try:created=date.fromisoformat(str(d['created_at']));updated=date.fromisoformat(str(d['updated_at']))
  except ValueError:raise Invalid(f'{p}: invalid dates')
  require(updated>=created,f'{p}: reversed dates')
  if t=='Claim':
   statuses={'empirical':{'PROPOSED','SUPPORTED','FALSIFIED','INDETERMINATE'},'formal':{'CONJECTURED','PROVED','DISPROVED'}}.get(d['claim_kind'],set())
  if statuses is not None:require(d.get('status') in statuses,f'{p}: incompatible status')
  for alias in d.get('aliases',[]):
   require(isinstance(alias,str) and alias and alias not in aliases,f'{p}: duplicate/empty alias');aliases.add(alias)
  for ref in d['source_refs']:file_ref(ref)
  records[d['id']]=d;bodies[d['id']]=body
 require(not (aliases & records.keys()),'Alias shadows ID')
 def object_ref(ref,types=None):
  require(isinstance(ref,str) and ref in records,f'Unknown ID: {ref}')
  require(types is None or records[ref]['type'] in types,f'Wrong reference type: {ref}')
  return records[ref]
 supersedes={};supported={}
 for id,d in records.items():
  t=d['type'];edges=set()
  for edge in d['relations']:
   require(isinstance(edge,dict) and edge.keys()=={'relation','target'},f'{id}: invalid edge')
   r,target=edge['relation'],edge['target'];dest=object_ref(target)
   require(r in {'tests','supports','challenges','depends_on','derived_from','supersedes','informs','inspired_by'},f'{id}: unknown relation')
   require(target!=id and (r,target) not in edges,f'{id}: duplicate/self edge');edges.add((r,target))
   require(target in bodies[id],f'{id}: explain edge to {target} in body')
   if r=='tests':require(t=='Test' and dest['type'] in {'Question','Claim'},f'{id}: tests endpoints')
   if r in {'supports','challenges'}:require(t in {'Result','Claim'} and dest['type']=='Claim',f'{id}: evidence endpoints')
   if r=='supports' and d.get('status') in {'VALID','SUPPORTED','PROVED'}:supported.setdefault(target,[]).append(id)
   if r=='supersedes':require(t==dest['type'],f'{id}: supersedes type');supersedes.setdefault(id,[]).append(target)
  for key,types in [('question_refs',{'Question'}),('assumption_refs',{'Assumption'}),('target_refs',{'Claim','Question'}),('affected_refs',None)]:
   for ref in d.get(key,[]):object_ref(ref,types)
  for key,types in [('package_ref',{'ResearchPackage'}),('test_ref',{'Test'}),('invalidation_decision_ref',{'Decision'})]:
   if key in d:object_ref(d[key],types)
  for key in ['protocol_ref','repository_path']:
   if key in d:file_ref(d[key])
  for ref in d.get('artifact_refs',[])+d.get('proof_artifact_refs',[]):file_ref(ref)
  if t=='Source':require('url' in d or 'repository_path' in d,f'{id}: source location missing')
  if t=='Source' and 'url' in d:require(d['url'].startswith(('https://','http://')),f'{id}: invalid URL')
  if t=='Result':
   require(records[d['test_ref']]['package_ref']==d['package_ref'],f'{id}: Test/package mismatch')
   run=file_ref(d['run_ref'],directory=True);manifest=json.loads((run/'manifest.json').read_text())
   history=subprocess.run(['git','log','--diff-filter=A','--format=%H','--',d['run_ref']+'/manifest.json'],cwd=root,capture_output=True,text=True)
   if history.returncode==0 and history.stdout.strip():
    first=history.stdout.strip().splitlines()[-1]
    tree=subprocess.check_output(['git','ls-tree','-r','--name-only',first,'--',d['run_ref']],cwd=root,text=True).splitlines()
    current={p.relative_to(root).as_posix() for p in run.rglob('*') if p.is_file()}
    require(current==set(tree),f'{id}: immutable run file set changed')
    for path in tree:require((root/path).read_bytes()==subprocess.check_output(['git','show',first+':'+path],cwd=root),f'{id}: immutable run changed')
   legacy=isinstance(manifest,dict) and set(manifest)=={'configuration','seeds','environment','outputs'}
   pipeline_fields={'stage','run_id','source_commit','approval_path','approval_sha256','plan_path','plan_sha256','plan','base','seeds','environment','elapsed_wall_seconds','peak_process_resident_memory','outputs'}
   confirm=isinstance(manifest,dict) and set(manifest)==pipeline_fields and manifest.get('stage')=='confirmation'
   require((legacy or confirm) and all(manifest.values()),f'{id}: incomplete run manifest')
   if confirm:
    plan=manifest['plan']
    require(isinstance(plan,dict) and plan.get('frozen') is True and plan.get('execution_authorized') is True and plan.get('run_id')==manifest['run_id']==run.name,f'{id}: unfrozen confirmation manifest')
    require(not (run/'failure.txt').exists() and isinstance(manifest['outputs'],dict) and {'summary.json','replicates.json'}<=manifest['outputs'].keys(),f'{id}: incomplete confirmation evidence')
    require(all(isinstance(manifest[k],str) for k in ['source_commit','plan_sha256','approval_sha256']) and re.fullmatch(r'[0-9a-f]{40}',manifest['source_commit']) is not None and re.fullmatch(r'[0-9a-f]{64}',manifest['plan_sha256']) is not None and re.fullmatch(r'[0-9a-f]{64}',manifest['approval_sha256']) is not None,f'{id}: confirmation provenance hashes')
   require(isinstance(manifest['outputs'],dict),f'{id}: output manifest')
   for name,digest in manifest['outputs'].items():
    output=(run/name).resolve();require(output.is_relative_to(run) and output.is_file(),f'{id}: invalid run output')
    require(hashlib.sha256(output.read_bytes()).hexdigest()==digest,f'{id}: output checksum mismatch')
   for ref in d['artifact_refs']:require(file_ref(ref).is_relative_to(run),f'{id}: artifact outside its run')
   if d['status']=='INVALIDATED':
    require(d.get('invalidation_reason') and d.get('invalidation_decision_ref'),f'{id}: invalidation metadata')
    require(records[d['invalidation_decision_ref']]['status']=='ACTIVE',f'{id}: invalidation decision must be active')
 for id,d in records.items():
  if d.get('status') in {'SUPPORTED','PROVED'}:
   require('## Justification' in bodies[id] and bodies[id].split('## Justification',1)[1].strip(),f'{id}: justification missing')
   require(supported.get(id) or d.get('proof_artifact_refs'),f'{id}: valid supporting evidence missing')
 def walk(id,stack):
  require(id not in stack,'Supersession cycle')
  for target in supersedes.get(id,[]):walk(target,stack|{id})
 for id in supersedes:walk(id,set())
 for p in (root/'cycles').glob('cycle-*/manifest.json'):
  c=json.loads(p.read_text());require(set(c)==CYCLE_FIELDS,f'{p}: cycle fields')
  require(c['schema_version']=='0.1' and type(c['cycle_number']) is int and c['cycle_number']>0 and c['title'],f'{p}: cycle identity')
  require(p.parent.name==f'cycle-{c["cycle_number"]:02d}',f'{p}: cycle folder')
  require(c['status'] in {'PLANNED','OPEN','ACTIVE','REVIEW','CLOSED','PUBLISHED'},f'{p}: cycle status')
  require(isinstance(c['package_refs'],list) and c['package_refs'] and len(set(c['package_refs']))==len(c['package_refs']),f'{p}: packages')
  for ref in c['package_refs']:object_ref(ref,{'ResearchPackage'})
  require(isinstance(c['publication_refs'],list),f'{p}: publications array')
  for ref in c['publication_refs']:file_ref(ref)
  obligations=c['obligations'];require(isinstance(obligations,list) and obligations,f'{p}: no obligations');keys=set();total=done=0
  if c['cycle_number']==1:
   require([o.get('key') for o in obligations]==['rp002a','rp003','rp004','rp005a','damx','checkpoint-a','graph-review','synthesis','foundation','what-changed','what-open','transition','close-bundle'],f'{p}: Cycle 1 obligation contract')
  for i,o in enumerate(obligations):
   require(set(o)=={'key','description','weight','resolved','resolution','evidence_refs','decision_ref'},f'{p}: obligation fields')
   require(isinstance(o['key'],str) and o['key'] and o['key'] not in keys and o['description'],f'{p}: obligation key');keys.add(o['key'])
   require(type(o['weight']) is int and o['weight']>0 and type(o['resolved']) is bool and isinstance(o['evidence_refs'],list),f'{p}: obligation types')
   if c['cycle_number']==1:require(o['weight']==1,f'{p}: Cycle 1 equal weights')
   total+=o['weight']
   for ref in o['evidence_refs']:file_ref(ref)
   if o['decision_ref'] is not None:require(object_ref(o['decision_ref'],{'Decision'})['status']=='ACTIVE',f'{p}: inactive obligation decision')
   if o['resolved']:
    done+=o['weight'];require(o['evidence_refs'] and o['resolution'] in {'completed','validly_blocked','falsified','indeterminate','explicitly_transferred'},f'{p}: resolution without evidence')
    if o['resolution'] in {'validly_blocked','indeterminate','explicitly_transferred'}:require(o['decision_ref'],f'{p}: resolution decision missing')
    if o['resolution']=='explicitly_transferred':require('Transfer acceptance' in bodies[o['decision_ref']],f'{p}: transfer acceptance missing')
   else:require(o['resolution'] is None and o['decision_ref'] is None and not o['evidence_refs'],f'{p}: unresolved metadata')
  closed=c['status'] in {'CLOSED','PUBLISHED'};require((done==total)==closed,f'{p}: progress/lifecycle mismatch')
  if closed:
   require(obligations[-1]['key']=='close-bundle' and obligations[-1]['decision_ref']==c['close_decision_ref'],f'{p}: close bundle decision')
   require(object_ref(c['close_decision_ref'],{'Decision'})['status']=='ACTIVE',f'{p}: close decision')
   require(isinstance(c['snapshot_ref'],str) and re.fullmatch('[0-9a-f]{40}',c['snapshot_ref']),f'{p}: snapshot SHA')
   require(subprocess.run(['git','cat-file','-e',c['snapshot_ref']+'^{commit}'],cwd=root,capture_output=True).returncode==0,f'{p}: missing snapshot commit')
  else:require(c['close_decision_ref'] is None and c['snapshot_ref'] is None,f'{p}: premature close metadata')
  if c['status']=='PUBLISHED':require(c['publication_refs'],f'{p}: publication evidence missing')
  cycles[p.relative_to(root).as_posix()]=c
 for id,d in records.items():
  if d['type']=='ResearchPackage':
   require(d['cycle_ref'] in cycles and id in cycles[d['cycle_ref']]['package_refs'],f'{id}: cycle/package mismatch')
 return records,cycles

if __name__=='__main__':
 root=Path(__file__).resolve().parents[2]
 records,cycles=validate(root)
 print(f'PASS: {len(records)} research objects; {len(cycles)} Cycle manifests. No scientific status promoted.')
