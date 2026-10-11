"""Verify a source-bound close snapshot, never scientific truth or approval."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CLOSE = 'cycles/cycle-01/close'
CUTOFF = '4b9916491491d3c94e251b64589c79a40b99ece4'
PREFIXES = ('baseline', 'research', 'graph', 'legacy', 'docs/decisions', 'cycles/cycle-01/reviews')
CATEGORIES = {'initial_manifest_questions', 'packages', 'protocols', 'results', 'deviations_invalidations',
              'synthesis', 'foundation', 'what_changed', 'what_open', 'knowledge_snapshot', 'transition'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def historical_hashes(commit):
    paths = git('ls-tree', '-r', '--name-only', commit, '--', *PREFIXES).decode().splitlines()
    hashes = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for path in paths:
            process.stdin.write((commit + ':' + path + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            require(len(header) == 3 and header[1] == b'blob', 'Missing historical blob')
            remaining = int(header[2])
            digest = hashlib.sha256()
            while remaining:
                block = process.stdout.read(min(remaining, 1024 * 1024))
                require(block, 'Truncated historical blob')
                digest.update(block)
                remaining -= len(block)
            require(process.stdout.read(1) == b'\n', 'Blob framing')
            hashes[path] = digest.hexdigest()
        process.stdin.close()
        require(process.wait() == 0, 'Historical hash reconstruction failed')
    return hashes


def validate(saved=None, manifest=None):
    saved = saved if saved is not None else json.loads((ROOT / CLOSE / 'KNOWLEDGE_SNAPSHOT.json').read_text())
    manifest = manifest if manifest is not None else json.loads((ROOT / 'cycles/cycle-01/manifest.json').read_text())
    require(saved['evidence_cutoff'] == CUTOFF and saved['no_automatic_scientific_inference'] is True, 'Evidence cutoff/role')
    require(saved['evidence_files'] == historical_hashes(CUTOFF), 'Historical evidence inventory differs')
    spec = importlib.util.spec_from_file_location('historical_graph', ROOT / 'scripts/check-cycle01-graph-review.py')
    graph = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(graph)
    graph.verify_snapshot(saved['graph'], graph.reconstruct(CUTOFF))
    require(len(saved['graph']['record_inputs']) == 38, 'Pre-close inventory scope')
    require(set(saved['mandatory_outputs']) == CATEGORIES, 'Mandatory output categories')
    for paths in saved['mandatory_outputs'].values():
        require(paths and all((ROOT / path).is_file() for path in paths), 'Missing mandatory output')
    require(manifest['status'] in {'CLOSED', 'PUBLISHED'} and manifest['close_decision_ref'] == 'D-0012', 'Close lifecycle')
    require(len(manifest['obligations']) == 13 and all(o['resolved'] for o in manifest['obligations']), 'Incomplete close')
    tag = subprocess.run(['git', 'rev-parse', '--verify', 'refs/tags/cycle-01-close^{commit}'], cwd=ROOT, capture_output=True, text=True)
    anchor = manifest['snapshot_ref']
    if anchor == CUTOFF:
        # A checkout of the immutable assembly commit predates the metadata pin.
        # Only that exact tagged checkout may resolve its own completed anchor.
        head = git('rev-parse', 'HEAD').decode().strip()
        require(tag.returncode == 0 and tag.stdout.strip() == head
                and manifest == json.loads(git('show', head + ':cycles/cycle-01/manifest.json'))
                and manifest == json.loads((ROOT / 'cycles/cycle-01/manifest.json').read_text()),
                'Pre-close reference is only valid in the exact tagged assembly checkout')
        anchor = head
    frozen = json.loads(git('show', anchor + ':cycles/cycle-01/manifest.json'))
    require(frozen['status'] == 'CLOSED' and frozen['close_decision_ref'] == 'D-0012'
            and len(frozen['obligations']) == 13 and all(o['resolved'] for o in frozen['obligations']),
            'Snapshot must be a completed CLOSED commit')
    for field in ('schema_version', 'cycle_number', 'title', 'package_refs', 'obligations', 'close_decision_ref'):
        require(manifest[field] == frozen[field], 'Closed obligation contract differs from anchor')
    for path in (CLOSE + '/KNOWLEDGE_SNAPSHOT.json', CLOSE + '/KNOWLEDGE_SNAPSHOT.md',
                 CLOSE + '/CLOSE_BUNDLE.md', 'docs/decisions/DECISION-0012_CYCLE01_CLOSE.md', 'graph/decisions/D-0012.md'):
        require((ROOT / path).read_bytes() == git('show', anchor + ':' + path), 'Close output differs from anchor')
    closed_graph = graph.reconstruct(anchor)
    require(len(closed_graph['record_inputs']) == 39 and 'D-0012' in closed_graph['record_inputs'], 'Completed close graph')
    original_records = saved['graph']['record_inputs']
    require(all(closed_graph['record_inputs'][k] == v for k, v in original_records.items()), 'Prior record changed during closure')
    require(historical_hashes(anchor).items() >= saved['evidence_files'].items(), 'Prior evidence changed during closure')
    if tag.returncode == 0:
        require(tag.stdout.strip() == anchor, 'Immutable close tag differs from snapshot_ref')
    if manifest['status'] == 'PUBLISHED':
        require(CLOSE + '/PUBLICATION.json' in manifest['publication_refs'], 'Publication receipt missing')
        publication = json.loads((ROOT / CLOSE / 'PUBLICATION.json').read_text())
        require(publication['snapshot_ref'] == anchor and set(publication['sites']) == {'org', 'net'}, 'Publication source/sites')
        require(all(s['status'] == 'succeeded' and s['version_id'] and s['deployment_id'] and s['source_commit']
                    for s in publication['sites'].values()), 'Publication lacks succeeded deployment evidence')
    print(f'PASS: close inventory {len(saved["evidence_files"])} files, 38 pre-close/39 closed records; '
          f'13/13 obligations, completed snapshot and existing tag binding. Integrity only.')


if __name__ == '__main__':
    validate()
