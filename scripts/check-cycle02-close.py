"""Verify Cycle 02 close source bindings and lifecycle; never infer scientific truth."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CLOSE = 'cycles/cycle-02/close'
CUTOFF = 'f3d538a32987882c5a2a7c821a2da71a5092d6d1'
PATHS = ('baseline', 'research', 'graph', 'legacy', 'docs/decisions',
         'cycles/cycle-01/reviews', 'cycles/cycle-02/reviews',
         'cycles/cycle-02/CYCLE02_ENTRY_REVIEW.md', 'cycles/cycle-02/manifest.json')
CATEGORIES = {'initial_manifest_questions', 'package_disposition', 'protocol_checkpoint',
              'result_outputs', 'deviations_incomplete', 'graph_review', 'synthesis_foundation',
              'change_open', 'transition', 'close_bundle_snapshot'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def historical_hashes(commit):
    paths = git('ls-tree', '-r', '--name-only', commit, '--', *PATHS).decode().splitlines()
    hashes = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for path in paths:
            process.stdin.write(f'{commit}:{path}\n'.encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            require(len(header) == 3 and header[1] == b'blob', 'Missing historical evidence blob')
            remaining = int(header[2])
            digest = hashlib.sha256()
            while remaining:
                block = process.stdout.read(min(remaining, 1024 * 1024))
                require(block, 'Truncated historical evidence blob')
                digest.update(block)
                remaining -= len(block)
            require(process.stdout.read(1) == b'\n', 'Historical blob framing')
            hashes[path] = digest.hexdigest()
        process.stdin.close()
        require(process.wait() == 0, 'Historical hash reconstruction failed')
    return hashes


def check():
    snapshot = json.loads((ROOT / CLOSE / 'CYCLE02_KNOWLEDGE_SNAPSHOT.json').read_text())
    manifest = json.loads((ROOT / 'cycles/cycle-02/manifest.json').read_text())
    for field, expected in (('schema_version', '0.1'), ('captured_at', '2026-10-13'),
                            ('evidence_cutoff', CUTOFF), ('no_automatic_scientific_inference', True)):
        require(snapshot.get(field) == expected,
                f'Snapshot {field} mismatch: {snapshot.get(field)!r} != {expected!r}')
    require(snapshot['evidence_files'] == historical_hashes(CUTOFF),
            'Evidence file inventory differs from the historical cutoff')
    require(CUTOFF in git('rev-list', 'HEAD').decode().splitlines(),
            'Evidence cutoff is not an ancestor of this checkout')
    graph = snapshot['graph_review_inventory']
    graph_bytes = (ROOT / graph['path']).read_bytes()
    require(hashlib.sha256(graph_bytes).hexdigest() == graph['sha256'],
            'Referenced immutable graph-review inventory changed')
    graph_review = json.loads(graph_bytes)
    require(graph_review['reviewed_source_commit'] == graph['reviewed_source_commit']
            and len(graph_review['record_inputs']) == graph['records']
            and len(graph_review['declared_relations']) == graph['declared_relations']
            and len(graph_review['typed_references']) == graph['typed_references']
            and len(graph_review['forward_question_trace']) == graph['question_traces']
            and len(graph_review['backward_result_trace']) == graph['backward_result_traces'],
            'Graph-review summary does not match its immutable inventory')
    require(set(snapshot['mandatory_outputs']) == CATEGORIES, 'Mandatory output categories differ')
    for paths in snapshot['mandatory_outputs'].values():
        require(paths and all((ROOT / path).is_file() for path in paths), 'A mandatory close output is missing')
    require(manifest['status'] in {'CLOSED', 'PUBLISHED'}
            and manifest['close_decision_ref'] == 'D-0022'
            and len(manifest['obligations']) == 9
            and all(o['resolved'] for o in manifest['obligations']),
            'Cycle 02 is not completely closed by D-0022')
    require(manifest['obligations'][-1]['key'] == 'close-bundle'
            and manifest['obligations'][-1]['decision_ref'] == 'D-0022',
            'Close obligation is not bound to D-0022')
    require(manifest['snapshot_ref'] is None or len(manifest['snapshot_ref']) == 40,
            'Snapshot reference must be null during assembly or a full commit SHA')
    if manifest['snapshot_ref']:
        anchor = manifest['snapshot_ref']
        frozen = json.loads(git('show', f'{anchor}:cycles/cycle-02/manifest.json'))
        require(frozen['status'] == 'CLOSED' and frozen['close_decision_ref'] == 'D-0022'
                and len(frozen['obligations']) == 9 and all(o['resolved'] for o in frozen['obligations']),
                'Snapshot anchor is not a completed CLOSED commit')
        for field in ('schema_version', 'cycle_number', 'title', 'package_refs', 'obligations', 'close_decision_ref'):
            require(manifest[field] == frozen[field], 'Living manifest differs from closed snapshot contract')
        for path in (CLOSE + '/CYCLE02_CLOSE_BUNDLE.md', CLOSE + '/CYCLE02_KNOWLEDGE_SNAPSHOT.md',
                     CLOSE + '/CYCLE02_KNOWLEDGE_SNAPSHOT.json', 'docs/decisions/DECISION-0022_CYCLE02_CLOSE.md',
                     'graph/decisions/D-0022.md'):
            require((ROOT / path).read_bytes() == git('show', f'{anchor}:{path}'),
                    'Close record differs from its immutable snapshot anchor')
        require(historical_hashes(anchor).items() >= snapshot['evidence_files'].items(),
                'Pre-close evidence changed after closure')
    elif manifest['status'] != 'CLOSED' or manifest['publication_refs']:
        raise ValueError('Only the CLOSED assembly stage may have an unpinned snapshot')
    if manifest['status'] == 'PUBLISHED':
        require(CLOSE + '/PUBLICATION.json' in manifest['publication_refs'], 'Publication receipt missing')
        publication = json.loads((ROOT / CLOSE / 'PUBLICATION.json').read_text())
        require(publication['snapshot_ref'] == manifest['snapshot_ref']
                and set(publication['sites']) == {'org', 'net'}, 'Publication source/sites differ')
        require(all(site['status'] == 'succeeded' and site['version_id'] and site['deployment_id']
                    and site['source_commit'] for site in publication['sites'].values()),
                'Publication lacks successful deployment evidence')
    print(f"PASS: Cycle 02 close inventory {len(snapshot['evidence_files'])} files; "
          f"9/9 obligations, source-bound snapshot and {manifest['status']} lifecycle. Integrity only.")


if __name__ == '__main__':
    check()
