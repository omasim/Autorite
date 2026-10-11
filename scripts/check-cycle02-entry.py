"""Check the preserved entry design and source intake; execute no research audit."""
from pathlib import Path
import hashlib
import itertools
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['rp006', 'checkpoint-a', 'graph-review', 'synthesis', 'foundation',
        'what-changed', 'what-open', 'transition', 'close-bundle']


def validate(plan=None):
    plan = plan if plan is not None else json.loads((ROOT / 'research/RP006/ENTRY_PLAN.json').read_text())
    if plan['domain_path'] != 'research/RP006/DOMAIN.json' or plan['cycle_ref'] != 'cycles/cycle-02/manifest.json':
        raise ValueError('Fixed entry intake paths required')
    if plan['execution_authorized'] is not False or plan['source_frozen'] is not False or any(plan['readiness'].values()):
        raise ValueError('Preserved entry plan grants no execution/source-freeze readiness')
    fields = ['state', 'parents', 'birth_kind']
    masks = [dict(id=''.join(map(str, bits)), retained_fields=[f for f, b in zip(fields, bits) if b])
             for bits in itertools.product([0, 1], repeat=3)]
    if plan['field_order'] != fields or plan['masks'] != masks:
        raise ValueError('Exact eight uniform whole-field masks required')
    families = {'FULL': ['same_state', 'ancestor', 'shared_root', 'parents', 'birth_kind', 'alive'],
                'TOPOLOGY_STATE': ['same_state', 'ancestor', 'shared_root', 'parents']}
    if plan['query_families'] != families or plan['entity_universe'] != ['a', 'b', 'c']:
        raise ValueError('Declared family/universe scope')
    if plan['projection_keys'] != ['entities', 'fields'] or plan['side_information'] != [
            'common_entity_universe', 'query_definitions', 'uniform_mask', 'declared_finite_domain_semantics']:
        raise ValueError('Forbidden projection side information')
    raw = (ROOT / plan['domain_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != plan['domain_sha256']:
        raise ValueError('Domain receipt hash')
    domain = json.loads(raw)
    if domain['source_path'] != 'research/RP004/RP004_FIXTURES.json':
        raise ValueError('Fixed RP004 source intake path required')
    source = (ROOT / domain['source_path']).read_bytes()
    historical = subprocess.check_output(['git', 'show',
        '894d427d2e1e2cc7a7af308201b855c6e4bd3764:' + domain['source_path']], cwd=ROOT)
    if source != historical or hashlib.sha256(source).hexdigest() != domain['source_sha256']:
        raise ValueError('RP004 original source differs from close anchor')
    expected = [{'id': c['id'], 'events': c['events']} for c in json.loads(source)['cases']]
    if domain['cases'] != expected or [c['id'] for c in expected] != ['G0', 'G1', 'G2', 'G3', 'G4', 'C4']:
        raise ValueError('Known event logs changed or expected-answer data inserted')
    if plan['planned_counts'] != {'full_truth_rows': 216, 'topology_state_truth_rows': 180,
            'projections': 48, 'case_pair_mask_comparisons': 120, 'family_mask_verdicts': 16,
            'max_full_pair_query_checks': 4320, 'max_topology_state_pair_query_checks': 3600}:
        raise ValueError('Prospective coverage dimensions')
    if plan['proposed_limits'] != {'attempts': 1, 'monotonic_seconds': 60,
            'peak_process_rss_bytes': 134217728, 'processes': 1, 'network_access': False, 'seeds': []}:
        raise ValueError('Entry resource proposal changed without review')
    manifest = json.loads((ROOT / 'cycles/cycle-02/manifest.json').read_text())
    if [o['key'] for o in manifest['obligations']] != KEYS or any(o['weight'] != 1 for o in manifest['obligations']):
        raise ValueError('Initial nine-obligation denominator changed')
    if manifest['package_refs'] != ['RP-006'] or plan['package_ref'] != 'RP-006':
        raise ValueError('Entry package identity')
    # Preserve the dated plan and domain after their first accepted entry anchor.
    tag = subprocess.run(['git', 'rev-parse', '--verify', 'refs/tags/cycle-02-open^{commit}'],
                         cwd=ROOT, capture_output=True, text=True)
    if tag.returncode == 0:
        for path in ['research/RP006/ENTRY_PLAN.json', 'research/RP006/DOMAIN.json',
                     'research/RP006/RP006_OPERATIONAL_PROTOCOL.md', 'research/RP006/RP006_PRIOR_ART_REVIEW.md',
                     'cycles/cycle-02/CYCLE02_ENTRY_REVIEW.md', 'docs/decisions/DECISION-0013_CYCLE02_ENTRY.md']:
            original = subprocess.check_output(['git', 'show', tag.stdout.strip() + ':' + path], cwd=ROOT)
            if (ROOT / path).read_bytes() != original:
                raise ValueError('Dated entry changed; use a new reviewed version')


if __name__ == '__main__':
    validate()
    print('PASS: Cycle 02 entry, nine obligations, eight masks/two families, original six-case intake; no research audit executed.')
